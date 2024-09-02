import pygame
import os
from PIL import Image
import numpy as np
import colorsys
import ctypes

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

BASE_IMG_PATH = "data/images/"


def load_image(path):
    img = (pygame.image.load(BASE_IMG_PATH + path + ".png").convert())
    img.set_colorkey((0, 0, 0))
    return img


def load_image_transparent(path, scale=(64, 32)):
    img = (pygame.image.load(BASE_IMG_PATH + path + ".png").convert())
    img.set_colorkey((255, 255, 255))
    img = pygame.transform.scale(img, scale)
    return img


# def load_biome(path, biome):
#     imgs = load_images(path + "/" + biome)
#     images = {}
#     for i in range(len(imgs)):
#         images[i] = imgs[i]
#     print(images)
#
#     return images


def load_images(path):
    images = []
    for file in sorted(os.listdir(BASE_IMG_PATH + path)):
        if file.endswith(".png"):
            images.append(load_image(path + "/" + file[:-4]))
    return images


def load_images_hue(path, hue):
    images = []
    for file in sorted(os.listdir(BASE_IMG_PATH + path)):
        if file.endswith(".png"):
            base_img = Image.open(BASE_IMG_PATH + path + "/" + file)
            arr = np.array(base_img)
            hue_shifted_arr = shift_hue(arr, hue / 360.).astype('uint8')
            img = Image.fromarray(hue_shifted_arr, 'RGBA')
            images.append(img.convert())
    return images


def load_keys(path):
    images = []
    for file in sorted(os.listdir(BASE_IMG_PATH + path)):
        if file.endswith(".png"):
            img = load_image(path + "/" + file[:-4])
            pygame.transform.scale(img, (16, 16))
            images.append(img)
    return images


def load_images_traparent(path):
    images = []
    for file in sorted(os.listdir(BASE_IMG_PATH + path)):
        if file.endswith(".png"):
            images.append(load_image_transparent(path + "/" + file[:-4]))
    return images


def shift_hue(image_file):
    # Open the image file
    img = Image.open(image_file)

    # Ensure the image is in RGB mode
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Load image data
    img_data = img.load()

    # Iterate over each pixel in the image
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = img_data[x, y]
            # Convert RGB to HSV
            h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)

            # Shift hue by 80 degrees (converted to scale 0-1)
            h = (h + 120 / 360.) % 1

            # Convert HSV back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)

            # Replace original pixel with new pixel
            img_data[x, y] = int(r * 255), int(g * 255), int(b * 255)

    # Save the modified image
    img.save('hue_shifted_' + image_file)


# {0: [img1, img2, img3], 1: {img1, img2, img3}}

def load_grass(path):
    images = {}

    return images


def scale_screen(self, new_size):
    self.screen_size = new_size
    self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
    self.display = pygame.Surface(self.zoom_size, pygame.SRCALPHA)
    self.outline = pygame.Surface(self.zoom_size)
    print("Screen size changed to: " + str(self.screen_size) + " aspect ratio is now " + str(
        self.screen_size[0] / self.screen_size[1]))


def center_window():
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    window = pygame.display.get_surface()
    window_size = window.get_size()
    window_pos = (screen_width // 2 - window_size[0] // 2, screen_height // 2 - window_size[1] // 2)

    ctypes.windll.user32.SetWindowPos(pygame.display.get_wm_info()['window'], 0, window_pos[0], window_pos[1], 0, 0,
                                      0x0001)


class Animation:
    def __init__(self, images, img_dur=1, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.img_duration)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.img_duration - 1)
            if self.frame >= len(self.images) * self.img_duration - 1:
                self.done = True

        return self.done

    def img(self):
        return self.images[int(self.frame // self.img_duration)]
