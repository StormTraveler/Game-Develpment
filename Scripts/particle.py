import math
import pygame
class Particle:
    def __init__(self, game, p_type, pos, velocity=(0, 0), frame=0, age=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + self.type].copy()
        self.animation.frame = frame
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.animation.img().get_width(), self.animation.img().get_height())
        self.age = age

    def update(self):
        kill = False
        self.age += 1
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))


class Spark:
    def __init__(self, pos, angle, speed): # TODO: Size, decay, color
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 1, 1)  # Assuming the size of the spark is 1x1


    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)

        return not self.speed

    def render(self, surf, offset=(0, 0)):
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),

            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0],
             self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),

            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0],
             self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]),

        ]

        pygame.draw.polygon(surf, (255, 255, 255), render_points)


class Projectile():
    def __init__(self, game, pos, velocity, duration, reflected=False, damage=1, img=None):
        self.game = game
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.duration = duration
        self.reflected = reflected
        self.damage = damage
        self.img = img
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 1, 1)


    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.duration -= 1

        if self.duration > 0:

            if self.game.tilemap.solid_check(self.pos):
                self.game.projectiles.remove(self)  # remove if colliding with wall
                if self.velocity[0] > 0:
                    self.game.create_sparks(self.pos[0], self.pos[1], True)
                elif self.velocity[0] < 0:
                    self.game.create_sparks(self.pos[0], self.pos[1], False)


            elif self.game.player.rect().collidepoint(self.pos):  # it hit the player
                if (abs(self.game.player.dashing[0]) < 30 and abs(
                        self.game.player.dashing[1]) < 30):  # after first 30 frames of dashing
                    self.game.projectiles.remove(self)
                    self.game.player.hurt(1)
                    self.game.sfx['hit'].play()
                    self.screenshake = max(32, self.game.screenshake)
                    self.game.create_explosion(self.pos[0] + self.img.get_width() // 2, self.pos[1] + self.img.get_height() // 2)

                else:
                    self.game.projectiles.remove(self)  # removed in dash

            if not self.reflected:
                for slash in self.game.player.slashes:
                    if not self.reflected and slash.rect().colliderect(
                            pygame.Rect(self.pos[0] - 4, self.pos[1] - 4, 8, 8)):
                        self.velocity = self.velocity[0] * -1, self.velocity[1]
                        self.reflected = True

            if self.reflected:  # Reflected by player so it can kill enemies
                for enemy in self.game.enemies:
                    if enemy.rect().colliderect(pygame.Rect(self.pos[0] - 4, self.pos[1] - 4, 8, 8)):
                        enemy.die()
                        try:
                            self.game.projectiles.remove(self)
                        except:
                            pass
                        self.game.sfx['hit'].play()
                        if self.velocity[0] > 0:
                            self.game.create_sparks(self.pos[0], self.pos[1], True)
                        elif self.velocity[0] < 0:
                            self.game.create_sparks(self.pos[0], self.pos[1], False)


        else:
            self.game.projectiles.remove(self)

    def render(self, surf, offset=(0, 0)):
        if self.img is not None:
            surf.blit(self.img, (self.pos[0] - self.img.get_width() / 2 - offset[0],
                                        self.pos[1] - self.img.get_height() / 2 - offset[1]))
        else:
            pygame.draw.rect(surf, (255, 0, 0), (self.pos[0] - offset[0], self.pos[1] - offset[1], 1, 1))