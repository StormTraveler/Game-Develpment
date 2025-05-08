from Scripts.Entities import PhysicsEntity
import random
import pygame
from Scripts.particle import Particle, Spark, Projectile
import math
import logging


#############################################
###########    ENEMY CLASS    ###############
#############################################
class Zenith(PhysicsEntity):

    # Define the Enemy Inheriting From Physics Entity
    def __init__(self, game, pos, size, speed=1, leeway=(0, 0), gun_type="pistol"):
        e_type = {"pistol": "red", "ak": "green", "burst": "blue"}.get(gun_type, "Zenith")
        super().__init__(game, "zenith/" + e_type, pos, size, speed, leeway)
        self.offcount = 0
        self.offmovecount = 0
        self.gun = gun_type
        self.walking = 0
        self.auto_shooting = False
        self.clip = 1
        clip_sizes = {"pistol": 1, "ak": 30, "burst": 3}
        self.max_clip_size = clip_sizes.get(self.gun, 1)
        self.reload = -60
        self.shoot_delay = 0
        delays = {"pistol": 0, "ak": 10, "burst": 5}
        self.max_shoot_delay = delays.get(self.gun, 0)

        # Determine the gun image and color based on gun_type
        self.gun_image = self.game.assets[self.gun]

    def die(self):
        self.game.sfx['hit'].play()
        self.game.enemies.remove(self)
        self.game.screenshake = max(16, self.game.screenshake)
        logging.debug("Enemy at x:" + str(self.rect().x) + " y:" + str(self.rect().y) + " died")
        self.dead = True

        self.game.player.coins += 1

        #   Death Sparks
        for i in range(25):
            speed = random.random() * 5
            angle = random.random() * math.pi * 2
            self.game.sparks.append(Spark((self.rect().x, self.rect().y), angle, 2 + random.random()))
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                frame=random.randint(0, 7)))

    def shoot_and_spark(self, vel):
        self.game.sfx['shoot'].play()

        self.game.projectiles.append(Projectile(self.game, self.rect().center, [vel[0] * 1.5, 0], 320,
                                                False, 1, img=self.game.assets['bullet']))

        self.game.create_sparks(self.rect().centerx, self.rect().centery, self.flip)

    # Main Enemy Update Function (Overriden)
    def update(self, tilemap, movement=(0, 0), offset=(0, 0)):

        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.rect().centery + 23)):
                if (self.collisions['left'] or self.collisions['right']):
                    self.flip = not self.flip
                movement = (movement[0] - 0.5 if self.flip else movement[0] + 0.5, movement[1])
            else:
                self.flip = not self.flip

            self.walking = max(0, self.walking - 1)

        elif random.random() < 0.01 and self.clip == self.max_clip_size:
            self.walking = random.randint(30, 120)

        if self.clip > 0 and self.shoot_delay <= 0:
            # Has ammo to shoot
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[0]) < 64 and abs(dis[1] < 32):  # Make sure the y distance is less than 32
                    if self.flip and dis[0] < 0:
                        self.shoot_and_spark((-1, 0))
                        self.clip -= 1
                        self.shoot_delay = 5
                        logging.debug(f"Shot fired. Remaining clip: {self.clip}")
                    elif not self.flip and dis[0] > 0:
                        self.shoot_and_spark((1, 0))
                        self.clip -= 1
                        self.shoot_delay = 5
                        logging.debug(f"Shot fired. Remaining clip: {self.clip}")
        else:
            if self.reload >= 0:
                reload_times = {"pistol": -120, "ak": -20, "burst": -30}
                self.reload = reload_times.get(self.gun, -60)
                self.clip = self.max_clip_size
                logging.debug(f"Reloading. New clip size: {self.clip}, reload time: {self.reload}")
            else:
                self.reload += 1
                self.shoot_delay -= 1
                logging.debug(f"Reloading in progress. Reload time: {self.reload}")

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

                self.die()

    # Main Enemy Render Function (Overriden)
    # Includes Gun Handling
    def render(self, surf, offset=(0, 0)):

        visible_area = pygame.Rect(offset[0] - 20, offset[1] - 20, self.game.zoom_size[0] + 40,
                                   self.game.zoom_size[1] + 40)
        if visible_area.colliderect(self.rect()):
            super().render(surf, offset=offset)

            # Render the gun and apply the color
            if self.flip:
                surf.blit(pygame.transform.flip(self.gun_image, True, False),
                          (self.rect().centerx - 4 - self.gun_image.get_width() - offset[0],
                           self.rect().centery - offset[1]))
            else:
                surf.blit(self.gun_image, (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

        else:
            self.offcount += 1
            if self.offcount % 60 == 0:
                logging.debug("Enemy at x:" + str(self.rect().x) + " y:" + str(self.rect().y) + " is offscreen")
