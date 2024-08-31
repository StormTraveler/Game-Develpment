import pygame
from Scripts.Utils import load_image

BASE_IMG_PATH = "data/images/"
pygame.init()
screen = pygame.display.set_mode([800, 600])
display = pygame.Surface([320, 240])
pygame.display.set_caption("test")

def load_biome(path, biome):
    print(path + "/" + biome + "_0")
    images = {
        0: load_image(path + "/" + biome + "_0"),
        1: load_image(path + "/" + biome + "_1"),
        2: load_image(path + "/" + biome + "_2"),
        3: load_image(path + "/" + biome + "_3"),
        4: load_image(path + "/" + biome + "_4"),
        5: load_image(path + "/" + biome + "_5"),
        6: load_image(path + "/" + biome + "_6"),
        7: load_image(path + "/" + biome + "_7"),
        8: load_image(path + "/" + biome + "_8")
    }




    return images

def load_grass(path):
    images = []

    load_biome(path, "default")

    return images


load_grass("tiles/grass")


for i in range(60):
    pygame.display.update()
    pygame.time.delay(1000)
