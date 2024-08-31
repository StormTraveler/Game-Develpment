import random

import pygame
from Scripts.particle import Particle
import math
from Scripts.Spark import Spark
import logging

logging.basicConfig(level=logging.CRITICAL)

#############################################
###########    ENTITY CLASS    ##############
#############################################
class PhysicsEntity:

    # Define the Physics Entity
    def __init__(self, game, e_type, pos, size, speed=1, leeway=(0, 0)):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.leeway = leeway
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")
        self.last_movement = [0, 0]
        self.speed = speed
        self.scale_speed = 1

    # Return the Rect of the Entity
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    # Set the Action of the Entity for Animation
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + action].copy()

    # Draw the Hitbox of the Entity for Debug
    def draw_hitbox(self):
        pygame.draw.rect(self.game.display, (255, 0, 0), (self.pos[0] - self.game.scroll[0] - self.leeway[0] / 2,
                                                          self.pos[1] - self.game.scroll[1] - self.leeway[1] / 2,
                                                          self.rect().width + self.leeway[0],
                                                          self.rect().height + self.leeway[1]), 1)

    # Main Entity Update Function
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] * self.scale_speed + self.velocity[0], movement[1] * self.scale_speed + self.velocity[1])

        self.pos[0] += frame_movement[0] * self.speed * self.scale_speed  # speed mult
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(self.velocity[1] + 0.1, 5)  # 0.1 is gravity     5 is terminal velocity

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    # Main Render Function for Entity
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))



#############################################
###########    ENEMY CLASS    ###############
#############################################
class Enemy(PhysicsEntity):

    # Define the Enemy Inheriting From Physics Entity
    def __init__(self, game, pos, size, speed=1, leeway=(0, 0)):
        super().__init__(game, "enemy", pos, size, speed, leeway)

        self.walking = 0

    # Main Enemy Update Function (Overriden)
    def update(self, tilemap, movement=(0, 0)):

        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.rect().centery + 23)):
                if (self.collisions['left'] or self.collisions['right']):
                    self.flip = not self.flip
                movement = (movement[0] - 0.5 if self.flip else movement[0] + 0.5, movement[1])
            else:
                self.flip = not self.flip

            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1] < 16):  # Shoots
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], [-1.5, 0], 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          random.random() + 2))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], [1.5, 0], 0])
                        for i in range(4):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, random.random() + 2))


        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        if abs(self.game.player.dashing[0]) > 40:
            if self.rect().colliderect(self.game.player.pos[0] - self.leeway[0] / 2,
                                       self.game.player.pos[1] - self.leeway[1] / 2,
                                       self.game.player.size[0] + self.leeway[0],
                                       self.game.player.size[1] + self.leeway[1]):  # +5 is the leeway for collisions
                self.game.enemies.remove(self)
                self.game.sfx['hit'].play()
                logging.debug("Enemy at x:" + str(self.rect().x) + " y:" + str(self.rect().y) + " died")
                self.game.screenshake = max(16, self.game.screenshake)

                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(
                        Particle(self.game, 'particle', self.rect().center,
                                 velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                           math.sin(angle + math.pi) * speed * 0.5],
                                 frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))  # Big sparks
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))

    # Main Enemy Render Function (Overriden)
    # Includes Gun Handling
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        # Attach the Gun to the Enemy
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False),
                      (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0],
                       self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
