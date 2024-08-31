import random

import pygame
from Scripts.particle import Particle
import math
from Scripts.Spark import Spark
import logging

logging.basicConfig(level=logging.CRITICAL)

#############################################
########   PHYSICS ENTITY CLASS   ###########
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
        self.scale_speed =  1


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

        frame_movement = (movement[0] * self.scale_speed + self.velocity[0] , movement[1] * self.scale_speed + self.velocity[1])

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
##########   ENTITY CLASS  ##################
#############################################

class Entity():
    def __init__(self, game, e_type, pos, size, speed=1, leeway=(0, 0)):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]

        self.leeway = leeway
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")
        self.last_movement = [0, 0]
        self.speed = speed
        self.scale_speed = 1
        self.dead = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

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

    def update(self, tilemap, pos=None, movement=(0, 0)):


        if pos is None:
            self.pos = self.pos

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        if self.game.debugging:
            self.draw_hitbox()
        self.done = self.animation.update()

        if self.type == "slash":
            for enemy in self.game.enemies:
                if self.rect().colliderect(enemy.rect()) and self.dead == False:
                    enemy.die()




    def render(self, surf, pos, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (pos[0] - offset[0] + self.anim_offset[0], pos[1] - offset[1] + self.anim_offset[1]))
