import pygame
import time

pygame.init()
pygame.display.set_mode((1, 1))
surface = pygame.image.load("../../data/images/backgrounds/bg.png").convert()
width, height = surface.get_size()

start = time.time()
for y in range(height):
    for x in range(width):
        r, g, b, _ = surface.get_at((x, y))
        gray = (r + g + b) // 3
        surface.set_at((x, y), (gray, gray, gray))
end = time.time()

print("Python grayscale time:", end - start)
