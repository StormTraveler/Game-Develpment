import pygame
import sys
import time

from Scripts.Utils import load_images, Animation, load_image, load_grass, load_keys
from Scripts.Tilemap import Tilemap
from Scripts.Player import Player

import os
print(os.getcwd())


MAP_TO_EDIT = "data/maps/1.json"
class Editor:
    def __init__(self):
        self.game_size = [640, 480]
        self.render_scale = 1.25
        pygame.init()
        self.screen = pygame.display.set_mode([800, 600])
        self.debugging = False

        self.zoom_size = [1280, 1000]

        self.display = pygame.Surface((self.game_size[0], self.game_size[1]))   #   320, 240
        pygame.display.set_caption("Level Editor")

        self.clock = pygame.time.Clock()
        self.running = True
        self.movement = [False, False, False, False]

        self.background = load_image("background")
        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "spawners": load_images("tiles/spawners"),
            "misc": load_images("tiles/misc"),
            "collectables": load_images("items/collectables"),
            "snow": load_images("tiles/snow"),
            "sand": load_images("tiles/sand"),
            "cave": load_images("tiles/cave"),
            "jungle": load_images("tiles/jungle"),
            "keys": load_keys("keys/pc/dark"),
            "grass_blades": load_images("tiles/grass_blades"),




        }

        print(list(self.assets))


        self.collectables = {
            "Dash": False,
            "Double Jump": False,
            "Sword Charge": False,  #   Spur ability
            "Wall Jump": False,
            "Health": False,

        }



        self.tilemap = Tilemap(self, tile_size=16, editor=True)
        try:
            self.tilemap.load(MAP_TO_EDIT)
        except FileNotFoundError:
            pass
        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.alt = False
        self.ongrid = True
        self.starting_pos = None
        self.dragging = False
        self.tileable = True

    def run(self):
        while self.running:
            self.display.fill((0, 0, 0))
            self.display.blit(pygame.transform.scale(self.background, [800 / self.render_scale, 600 / self.render_scale]), (0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 5 / self.render_scale
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 5 / self.render_scale
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll, collision=False, misc=True)

            tile_assets = self.assets[self.tile_list[self.tile_group]]
            current_tile_img = tile_assets[self.tile_variant].copy() if isinstance(tile_assets, list) else tile_assets.copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / self.render_scale, mpos[1] / self.render_scale)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, (mpos[0], mpos[1]))

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos, 'tileable': self.tileable}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            if self.starting_pos is not None:
                mpos = pygame.mouse.get_pos()
                mpos = (mpos[0] / self.render_scale, mpos[1] / self.render_scale)
                dx = mpos[0] - self.starting_pos[0]
                dy = mpos[1] - self.starting_pos[1]
                self.scroll[0] -= dx
                self.scroll[1] -= dy
                self.starting_pos = mpos



            self.clock.tick(60)
            self.events()
            self.update()

            self.display.blit(current_tile_img, (5, 5))

            self.screen.blit(pygame.transform.scale(self.display, [800, 600]), [0, 0])

            pygame.display.update()

    def zoom_out(self):
        old_center = [self.scroll[i] + self.game_size[i] / 2 for i in range(2)]

        self.game_size[0] /= 1.25
        self.game_size[1] /= 1.25
        self.display = pygame.Surface((self.game_size[0], self.game_size[1]))
        self.render_scale /= 0.8
        self.render_scale = round(self.render_scale, 4)

        new_center = [self.scroll[i] + self.game_size[i] / 2 for i in range(2)]
        self.scroll = [self.scroll[i] + old_center[i] - new_center[i] for i in range(2)]

    def zoom_in(self):
        old_center = [self.scroll[i] + self.game_size[i] / 2 for i in range(2)]

        self.game_size[0] *= 1.25
        self.game_size[1] *= 1.25
        self.display = pygame.Surface((self.game_size[0], self.game_size[1]))
        self.render_scale *= 0.8
        self.render_scale = round(self.render_scale, 4)

        new_center = [self.scroll[i] + self.game_size[i] / 2 for i in range(2)]
        self.scroll = [self.scroll[i] + old_center[i] - new_center[i] for i in range(2)]



    def events(self):
        mpos = pygame.mouse.get_pos()
        mpos = (mpos[0] / self.render_scale, mpos[1] / self.render_scale)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicking = True
                    if not self.ongrid:
                        self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                if event.button == 3:
                    self.right_clicking = True

                if event.button == 2:
                    self.starting_pos = mpos

                if self.shift:
                    if event.button == 4:
                        self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                        self.tile_variant = 0
                    if event.button == 5:
                        self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        self.tile_variant = 0
                elif self.alt:
                    if event.button == 4:
                        self.zoom_out()
                    if event.button == 5:
                        self.zoom_in()
                elif self.shift == False and self.alt == False:
                    if event.button == 4:
                        self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.button == 5:
                        self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])





            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.movement[0] = True
                if event.key == pygame.K_d:
                    self.movement[1] = True
                if event.key == pygame.K_w:
                    self.movement[2] = True
                if event.key == pygame.K_s:
                    self.movement[3] = True
                if event.key == pygame.K_LSHIFT:
                    self.shift = True
                if event.key == pygame.K_LALT:
                    self.alt = True
                if event.key == pygame.K_LCTRL:
                    self.tileable = False
                if event.key == pygame.K_g:
                    self.ongrid = not self.ongrid
                if event.key == pygame.K_o:
                    self.tilemap.save(MAP_TO_EDIT)
                if event.key == pygame.K_t:
                    self.tilemap.auto_tile()

                if event.key == pygame.K_EQUALS:
                    self.zoom_in()
                if event.key == pygame.K_MINUS:
                    self.zoom_out()


            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.movement[0] = False
                if event.key == pygame.K_d:
                    self.movement[1] = False
                if event.key == pygame.K_w:
                    self.movement[2] = False
                if event.key == pygame.K_s:
                    self.movement[3] = False
                if event.key == pygame.K_LSHIFT:
                    self.shift = False
                if event.key == pygame.K_LALT:
                    self.alt = False
                if event.key == pygame.K_LCTRL:
                    self.tileable =  True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicking = False
                if event.button == 3:
                    self.right_clicking = False
                if event.button == 2:
                    self.starting_pos = None



    def update(self):
        pass

Editor().run()