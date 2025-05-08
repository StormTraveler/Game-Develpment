import random
import pygame


class Celestials:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def render(self, surf, offset=(0, 0), mod=True):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        if mod:
            surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(),
                                 (render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height())))
        else:
            surf.blit(self.img, (render_pos[0] - self.img.get_width(), (render_pos[1] - self.img.get_height())))


class Cloud(Celestials):
    def __init__(self, pos, img, speed, depth):
        super().__init__(pos, img, speed, depth)

    def update(self):
        self.pos[0] += self.speed


class CloudManager:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        for i in range(count):
            self.clouds.append(Cloud([random.random() * 99999, random.random() * 99999], random.choice(cloud_images),
                                     random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0), mod=False):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset, mod=mod)


class Star(Celestials):
    def __init__(self, pos, img, speed, depth):
        super().__init__(pos, img, speed, depth)

    def render(self, surf, offset=(0, 0), mod=True):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        if mod:
            surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(),
                                 (render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height())))
        else:
            surf.blit(self.img, (render_pos[0] - self.img.get_width(), (render_pos[1] - self.img.get_height())))


class StarManager():
    def __init__(self, star_images, count=32):
        self.stars = []
        for i in range(count):
            self.stars.append(Star([random.random() * 99999, random.random() * 99999], random.choice(star_images),
                                   random.random() * 0.05 + 0.05, random.random() * 0.005 + 0.002))
            # the depth is set to a very small number which makes them further away hence moving slower

        self.stars.sort(key=lambda x: x.depth)

    def render(self, surf, offset=(0, 0), mod=False):
        for star in self.stars:
            star.render(surf, offset=offset, mod=mod)
