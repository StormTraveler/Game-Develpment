import random

import pygame
import json
import sys
from Scripts.UI import Dialogue
sys.path.append('Scripts')

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'snow', 'sand', 'cave', 'jungle', 'dark_grass'}
AUTO_TILES = {'grass', 'stone', 'snow', 'sand', 'cave', 'jungle', 'dark_grass'}
AUTO_TILES_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8
}

AUTO_TILE_GRASS = [
    'grass',
    'jungle',
    'dark_grass'
]

FOREGROUND_TILES = {
    'grass_blades',
    'decor',
    'misc',
    'spawners'

}

COLLECTABLE_KEYS = {
    0: 'Dash',
    1: 'Double Jump',
    2: 'Sword Charge',
    3: 'Wall Jump',
    4: 'Health'
}

class Tilemap:
    def __init__(self, game, tile_size=16, editor=False):
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.game = game
        self.editor = editor

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        return matches

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def save(self, path):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if 'tileable' not in tile:
                tile['tileable'] = True
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
        print('Saved tilemap to', path)

    def load(self, path):
        f = open(path, 'r')
        data = json.load(f)
        f.close()
        self.tilemap = data['tilemap']
        self.tile_size = data['tile_size']
        self.offgrid_tiles = data['offgrid']


    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size,
                                self.tile_size))
        return rects

    def auto_tile(self):
        for loc in list(self.tilemap.keys()):
            tile = self.tilemap[loc]
            # Check if the tile's position is on the grid
            if tile['pos'][0] % 1 == 0 and tile['pos'][1] % 1 == 0:
                if 'tileable' in tile and tile['tileable'] == True:  # Tile Main Tiles
                    neighbors = set()
                    for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                        check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                        if check_loc in self.tilemap:
                            if self.tilemap[check_loc]['type'] == tile['type']:
                                neighbors.add(shift)
                    neighbors = tuple(sorted(neighbors))
                    if tile['type'] in AUTO_TILES and neighbors in AUTO_TILES_MAP:
                        tile['variant'] = AUTO_TILES_MAP[neighbors]

                # Add grass blade above any grass tile with air above it
                if 'tileable' in tile and tile['tileable'] == True:
                    if tile['type'] in AUTO_TILE_GRASS:
                        check_loc = str(tile['pos'][0]) + ';' + str(tile['pos'][1] - 1)
                        if check_loc not in self.tilemap or self.tilemap[check_loc]['type'] in FOREGROUND_TILES:
                            # add grass blades above as a random variant between 1 and 3
                            self.tilemap[check_loc] = {'type': 'grass_blades', 'variant': random.choice([1, 1, 1, 1, 1, 2, 2, 3]), 'pos': [tile['pos'][0], tile['pos'][1] - 1]}


    def misc_tile_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] == 'misc' and self.tilemap[tile_loc]['variant'] == 0:
                return True
            elif self.tilemap[tile_loc]['type'] == 'misc' and self.tilemap[tile_loc]['variant'] == 1:
                self.game.load_level(self.game.level)
                return False
        return False

    def render(self, surf, offset=(0, 0), collision=True, misc=False):
        # Calculate the visible area            #### 32 is the buffer and 64 is to add 32 to the other sides aswell
        #visible_area = pygame.Rect(0, 0, self.game.zoom_size[0] + 40, self.game.zoom_size[1] + 40)

        visible_area = pygame.Rect(offset[0] - 32, offset[1] - 32, self.game.zoom_size[0] + 64, self.game.zoom_size[1] + 64)

        # Render offgrid tiles
        for tile in self.offgrid_tiles:
            tile_rect = pygame.Rect(tile['pos'][0], tile['pos'][1], self.tile_size, self.tile_size)
            if visible_area.colliderect(tile_rect):
                surf.blit(self.game.assets[tile['type']][tile['variant']],
                          (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
                #check for collectable collisions
                if tile['type'] == 'collectables' and self.editor == False:
                    tile_rect = pygame.Rect(tile['pos'][0] - offset[0], tile['pos'][1] - offset[1], 16, 16)
                    if self.game.debugging:
                        pygame.draw.rect(surf, (0, 255, 0), tile_rect, 1)

                    player_rect = pygame.Rect(self.game.player.pos[0] - self.game.scroll[0],
                                              self.game.player.pos[1] - self.game.scroll[1],
                                              self.game.player.rect().width,
                                              self.game.player.rect().height)

                    if player_rect.colliderect(tile_rect):
                        print('collected', tile['variant'])
                        self.game.collectables[COLLECTABLE_KEYS[tile['variant']]] = True
                        self.offgrid_tiles.remove(tile)
                        self.game.player.health = self.game.player.max_health

                        # reward player with collected values
                        if tile['variant'] == 0:
                            self.game.collectables['Dash'] = True
                            self.game.dialogues.append(Dialogue(self, [80, 850, 1760, 200],
                                                                f"Dash Unlocked! You can now dash by pressing the dash button! ({', '.join(pygame.key.name(self.game.keybinds['Dash'][i]) for i in range(len(self.game.keybinds['Dash'])))}) "
                                                                f"Be careful when you use this ability, it can be dangerous! You can dash in any direction, even up! "
                                                                f"Use it to dodge enemy attacks or to get to hard to reach places! "
                                                                f"It is also a very lethal weapon when enemies come in contact with you during a dash! ",
                            text_color=(255, 255, 255), img=self.game.assets["DialogueBox"]))

                        if tile['variant'] == 1:
                            self.game.player.max_jumps += 1
                            self.game.dialogues.append(Dialogue(self, [80, 850, 1760, 200],
                            f"Double Jump Unlocked! You can now jump twice! Be careful when you use this ability, "
                            f"you don't want to jump too high ;) ",
                            text_color=(255, 255, 255), img=self.game.assets["DialogueBox"]))

                        if tile['variant'] == 2:
                            self.game.player.sword_charge = True
                            self.game.dialogues.append(Dialogue(self, [80, 850, 1760, 200],
                            f"Sword Charge Unlocked! You can now charge your sword by holding the attack button! ({', '.join(pygame.key.name(self.game.keybinds['Attack'][i]) for i in range(len(self.game.keybinds['Attack'])))}) "
                            f"Release the attack button to unleash a powerful attack once charged! ",
                            text_color=(255, 255, 255), img=self.game.assets["DialogueBox"]))

                        if tile['variant'] == 3:
                            self.game.collectables['Wall Climb'] = True
                            self.game.dialogues.append(Dialogue(self, [80, 850, 1760, 200],
                            f"Wall Climb Unlocked! You can now climb walls by jumping towards them! ",
                            text_color=(255, 255, 255), img=self.game.assets["DialogueBox"]))

                        if tile['variant'] == 4:
                            self.game.player.max_health += 1
                            self.game.player.health += 1
                            self.game.dialogues.append(Dialogue(self, [80, 850, 1760, 200],
                            f"Increased max health! You can now take more damage! Ya Noob! "
                            f"Be careful, you can still die! Your max health is now {self.game.player.max_health}. ",
                            text_color=(255, 255, 255),
                            img=self.game.assets["DialogueBox"]))



        # Render tiles in the tilemap
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    if self.tilemap[loc]['type'] == 'grass_blades' and self.editor == False:
                        self.game.gm.place_tile((x, y), self.tilemap[loc]['variant'] * 8)
                    else:
                        tile = self.tilemap[loc]
                        surf.blit(self.game.assets[tile['type']][tile['variant']],
                                  [tile['pos'][0] * self.tile_size - offset[0],
                                   tile['pos'][1] * self.tile_size - offset[1]])