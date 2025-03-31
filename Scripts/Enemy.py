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
        self.burst_count = 0

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

    def burst_shoot(self, vel, burst_size=3, burst_delay=10):
        if self.burst_count < burst_size:
            self.shoot_and_spark(vel)
            self.burst_count += 1
        else:
            self.burst_count = 0
            pygame.time.set_timer(pygame.USEREVENT + 1, burst_delay)

    def auto_shoot(self, vel, auto_delay=5):
        if not self.auto_shooting:
            self.auto_shooting = True
            pygame.time.set_timer(pygame.USEREVENT + 2, auto_delay)
        self.shoot_and_spark(vel)



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
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(dis[1] < 16):
                    if self.flip and dis[0] < 0:
                        if self.gun == "burst":
                            self.burst_shoot((-1, 0))
                        elif self.gun == "ak":
                            self.auto_shoot((-1, 0))
                        else:
                            self.shoot_and_spark((-1, 0))
                    elif not self.flip and dis[0] > 0:
                        if self.gun == "burst":
                            self.burst_shoot((1, 0))
                        elif self.gun == "ak":
                            self.auto_shoot((1, 0))
                        else:
                            self.shoot_and_spark((1, 0))


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

                self.die()



    # Main Enemy Render Function (Overriden)
    # Includes Gun Handling
    def render(self, surf, offset=(0, 0)):

        visible_area = pygame.Rect(offset[0] - 20, offset[1] - 20, self.game.zoom_size[0] + 40, self.game.zoom_size[1] + 40)
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

