import pygame
import json
import sys
sys.path.append('Scripts')

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'snow', 'sand', 'cave', 'jungle'}
AUTO_TILES = {'grass', 'stone', 'snow', 'sand', 'cave', 'jungle'}
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
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # Check if the tile's position is on the grid
            if tile['pos'][0] % 1 == 0 and tile['pos'][1] % 1 == 0:
                if 'tileable' in tile and tile['tileable'] == True:
                    neighbors = set()
                    for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                        check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                        if check_loc in self.tilemap:
                            if self.tilemap[check_loc]['type'] == tile['type']:
                                neighbors.add(shift)
                    neighbors = tuple(sorted(neighbors))
                    if tile['type'] in AUTO_TILES and neighbors in AUTO_TILES_MAP:
                       tile['variant'] = AUTO_TILES_MAP[neighbors]

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
        # Calculate the visible area            #### 20 is the buffer and 40 is to add 20 to the other sides aswell
        visible_area = pygame.Rect(offset[0] - 20, offset[1] - 20, self.game.zoom_size[0] + 40, self.game.zoom_size[1] + 40)

        # Render offgrid tiles
        for tile in self.offgrid_tiles:
            tile_rect = pygame.Rect(tile['pos'][0], tile['pos'][1], self.tile_size, self.tile_size)
            if visible_area.colliderect(tile_rect):
                surf.blit(self.game.assets[tile['type']][tile['variant']],
                          (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

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

    def render_old(self, surf, offset=(0, 0), collision=True, misc=False):

        for tile in self.offgrid_tiles:


            #     OFFGRID COLLECTABLE CHECK
            if collision:
                if tile['type'] == 'collectables':
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
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
                    if self.game.collectables[COLLECTABLE_KEYS[tile['variant']]]:
                        continue

                else:
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

            else:
                surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))



        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] == 'keys':

                        #   RESCALE THE KEYS TO 32x32
                        scaled = pygame.transform.smoothscale(self.game.assets[tile['type']][tile['variant']], (32, 32))

                        surf.blit(scaled,
                                  [x * self.tile_size - offset[0], y * self.tile_size - offset[1]])
                    if tile['type'] == 'misc' and (tile['variant'] == 0 or tile['variant'] == 1) and not misc:
                        continue

                    else:
                        print(tile)
                        surf.blit(self.game.assets[tile['type']][tile['variant']],
                              [tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]])

