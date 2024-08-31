from Scripts.Entities import PhysicsEntity
import random
import pygame
from Scripts.particle import Particle
from Scripts.Spark import Spark
import math
import logging


#############################################
###########    ENEMY CLASS    ###############
#############################################
class Enemy(PhysicsEntity):

    # Define the Enemy Inheriting From Physics Entity
    def __init__(self, game, pos, size, speed=1, leeway=(0, 0)):
        super().__init__(game, "enemy", pos, size, speed, leeway)
        self.offcount = 0
        self.offmovecount = 0

        self.walking = 0

    # Main Enemy Update Function (Overriden)
    def update(self, tilemap, movement=(0, 0), offset=(0, 0)):

        #############################Skip movement for offscreen enemies #############################
        # visible_area = pygame.Rect(offset[0] - 20, offset[1] - 20, self.game.zoom_size[0] + 40, self.game.zoom_size[1] + 40)
        # if not visible_area.colliderect(self.rect()):
        #     self.offmovecount += 1
        #     if self.offmovecount % 60 == 0:
        #         logging.debug("Enemy at x:" + str(self.rect().x) + " y:" + str(self.rect().y) + " is offscreen not doing movement")
        #     return

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

        visible_area = pygame.Rect(offset[0] - 20, offset[1] - 20, self.game.zoom_size[0] + 40, self.game.zoom_size[1] + 40)
        if visible_area.colliderect(self.rect()):
            super().render(surf, offset=offset)

            # Attach the Gun to the Enemy
            if self.flip:
                surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False),
                          (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0],
                           self.rect().centery - offset[1]))
            else:
                surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
        else:
            pass
            # If the Enemy is not in the visible area, do not render it
            self.offcount += 1
            if self.offcount % 60 == 0:
                logging.debug("Enemy at x:" + str(self.rect().x) + " y:" + str(self.rect().y) + " is offscreen")
