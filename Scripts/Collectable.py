import pygame
import Utils

class Collectable:

    def __init__(self, rect, type, game, img):
        self.rect = rect
        self.pos = [self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2]
        self.type = type
        self.game = game
        self.img = img
        self.animation = self.game.assets['item/' + self.img].copy()
        self.animation.frame = 0
        self.animation.speed = 0.1
        self.animation.loop = True
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.animation.img().get_width(), self.animation.img().get_height())
        self.collected = False


    def update(self):
        self.render(self.game.display, self.game.scroll)


    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))