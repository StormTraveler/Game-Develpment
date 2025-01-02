from Scripts.Entities import PhysicsEntity
import random
import pygame
from Scripts.particle import Particle
import math
import logging

logging.basicConfig(level=logging.CRITICAL)

#############################################
###########    PLAYER CLASS    ##############
#############################################
class Player(PhysicsEntity):

    # Define the Player inheriting from Physics Entity
    def __init__(self, game, pos, size, speed=1, health=1, max_jumps=1):
        super().__init__(game, "player", pos, size, speed)
        self.wall_slide = False
        self.max_jumps = max_jumps
        self.air_time = 0
        self.jumps = 2
        self.dashing = [0, 0]
        self.dead = 0
        self.health = health

    def draw_hitbox(self):
        if self.dashing[0] == 0 and self.dashing[1] == 0:
            pygame.draw.rect(self.game.display, (255, 0, 0), (self.pos[0] - self.game.scroll[0] - self.leeway[0] / 2,
                                                              self.pos[1] - self.game.scroll[1] - self.leeway[1] / 2,
                                                              self.rect().width + self.leeway[0],
                                                              self.rect().height + self.leeway[1]), 1)
        elif self.dashing[0] <= 30 and self.dashing[1] <= 30:
            # draw a circle around the player
            pygame.draw.circle(self.game.display, (255, 0, 0), (self.pos[0] - self.game.scroll[0] + self.rect().width // 2, self.pos[1] - self.game.scroll[1] + self.rect().height // 2), 10, 1)

    # Main Player Update Function (Overriden)
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        self.wall_slide = False


        if movement[0] != 0:
            if abs(self.dashing[0]) > 30:
                self.scale_speed = min(1.25, self.scale_speed + 0.03)
            else:
                self.scale_speed = min(1, self.scale_speed + 0.03)
        else:
            self.scale_speed = max(0.3, self.scale_speed - 0.08)

        if self.air_time > 160:  # time before despawning from fall
            self.dead += 1
            self.game.screenshake = max(16, self.game.screenshake)
            logging.debug('Despawned due to great fall')


        if self.collisions['down']:
            self.air_time = 0
            self.jumps = self.max_jumps
            self.wall_slide = False

        if (self.collisions['left'] or self.collisions['right']) and self.air_time > 4:
            self.wall_slide = True
            self.air_time -= 1  # to prevent from despawning after a long wall slide
            self.velocity[1] = min(self.velocity[1], 0.5)


        if self.wall_slide:
            self.set_action("wall_slide")
        elif self.air_time > 4:
            self.set_action("jump")
        elif movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        logging.debug("scale speed is: " + str(self.scale_speed))

        # Deal with Particles for Dash
        if abs(self.dashing[0]) in {60, 50} or abs(self.dashing[1]) in {90, 80}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed,
                             math.sin(angle) * speed]  # Speed for directional movement at an angle
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        for i in range(2):
            if self.dashing[i] > 0:
                self.dashing[i] = max(0, self.dashing[i] - 1)
            elif self.dashing[i] < 0:
                self.dashing[i] = min(0, self.dashing[i] + 1)


        # Common logic for both dashes
        for i in range(2):

            # sets the threshold for the dash depending on the direction of the dash (0 = horizontal, 1 = vertical)
            abs_dashing = abs(self.dashing[i])
            threshold = 50 if i == 0 else 80
            velocity_factor = 3 if i == 0 else 7.5
            velocity_modifier = 0.2 if i == 0 else 0.3

            if abs_dashing > threshold:
                self.velocity[i] = abs_dashing / self.dashing[i] * velocity_factor

                if abs_dashing == threshold + 1:
                    self.velocity[i] *= velocity_modifier

                pvelocity = [0, 0]
                pvelocity[i] = abs_dashing / self.dashing[i] * random.random() * 3
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7))
                )

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    # Main Player Render Function (Overriden)
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing[0]) <= 50:
            super().render(surf, offset=offset)

    # Main Player Jump Function
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True


        elif self.jumps > 0:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True

    # Player Dash Function
    def dash(self, up=False):
        logging.info("Dash called, flip is: " + str(self.flip) + " and abs movement = " + str(abs(self.game.movement[0])))
        if self.dashing[0] == 0 and self.dashing[1] == 0:
            self.scale_speed = 1.25     # burst of acceleration after dash to get to higher than max speed
            self.game.sfx['dash'].play()
            self.air_time = max (0, self.air_time - 80)

            #   Vertical Dash
            if self.game.up:
                self.dashing[1] = -90

            #   Movement Dash
            elif self.game.movement[0] > 0 or self.game.movement[1] > 0:
                self.velocity[1] = -1.36
                if self.flip:
                    self.dashing[0] = -60  # cooldown
                    logging.info("Dash left")
                elif not self.flip:
                    self.dashing[0] = 60  # cooldown
                    logging.info("Dash right")

            #   Standing Dash
            elif self.game.movement[0] == 0 and self.game.movement[1] == 0:
                self.velocity[1] = -1.36
                if self.flip:
                    self.dashing[0] = -60
                    logging.info("Dash left")
                elif not self.flip:
                    self.dashing[0] = 60
                    logging.info("Dash right")



    # Simple Heatlh/Damage Function
    def hurt(self, damage=1):
        logging.info("Ouch! I got hit for " + str(damage) + " damage!")
        self.game.sfx['hit'].play()
        self.dead += 1

