import random
import math
import sys
import logging
import ctypes
import time
import cProfile

SF = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
print(SF)

from Scripts.Enemy import Enemy
from Scripts.Player import Player
from Scripts.Utils import *
from Scripts.Tilemap import Tilemap
from Scripts.Clouds import Clouds
from Scripts.particle import Particle
from Scripts.Spark import Spark
from Scripts.Menu import handle_state
from Scripts.UI import UI, Button



# os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0" Makes it open in the top left
logging.basicConfig(level=logging.INFO)


class Game:
    def __init__(self):
        self.screenshake_offset = [0, 0]
        self.scroll = []
        self.transition = 0
        self.enemies = []
        self.leaf_spawners = []
        self.particles = []
        self.projectiles = []
        self.sparks = []
        self.render_scroll = None
        pygame.init()
        self.screen_size = [1920, 1080]
        self.resolutions = [(640, 360), (854, 480), (960, 540), (1024, 576), (1280, 720), (1366, 768), (1600, 900),
                            (1920, 1080)]
        self.zoom_size = [480, 270]  # 16:9 aspect ratio 480:270
        self.scale_factor = {1: 4, 1.25: 3.2}.get(SF)
        self.screen_size = [self.zoom_size[0] * self.scale_factor, self.zoom_size[1] * self.scale_factor]

        self.screen = pygame.display.set_mode(self.screen_size, pygame.NOFRAME | pygame.RESIZABLE)
        pygame.display.set_caption("Test")

        self.full_display = pygame.Surface([1920, 1080], pygame.SRCALPHA)
        self.display = pygame.Surface(self.zoom_size, pygame.SRCALPHA)
        self.outline = pygame.Surface(self.zoom_size)

        self.clock = pygame.time.Clock()
        self.state = "Main Menu"
        self.movement = [False, False]
        self.scroll = [0, 0]
        self.debugging = False
        self.up = False
        self.down = False
        self.buttons = []
        self.button_selected = 0
        self.selected_keybind_button = None
        self.music = True  # Music Toggle
        self.key_code = None
        self.menu_states = ["Main Menu", "Pause", "Options", "Keybinds", "Resolution", "Inventory"]
        self.screenshake = 0
        self.music_volume = 0.5
        self.ADMIN = True
        self.UIs = []
        self.dialogues = []
        self.framerate = 60
        self.start = time.time()


        if self.ADMIN:
            self.collectables = {
                "Dash": True,
                "Double Jump": True,
                "Wall Climb": True,
                "Sword Charge": True,  # Spur ability
                "Wall Jump": True,
                "Health": True,
            }
            #self.music = False
        else:
            self.collectables = {
                "Dash": False,
                "Double Jump": False,
                "Wall Climb": False,
                "Sword Charge": False,  # Spur ability
                "Wall Jump": False,
                "Health": False,
            }

        self.keybinds = {
            "Face Up": [pygame.K_UP, pygame.K_w],
            "Face Down": [pygame.K_DOWN, pygame.K_s],
            "Move Left": [pygame.K_LEFT, pygame.K_a],
            "Move Right": [pygame.K_RIGHT, pygame.K_d],
            "Jump": [pygame.K_z, pygame.K_SPACE],
            "Dash": [pygame.K_c, pygame.K_LSHIFT],
            "Attack": [pygame.K_x, pygame.K_e],
            "Pause": pygame.K_ESCAPE,
            "Restart": pygame.K_r,
            "Jump2": pygame.K_w,
            "Inventory": pygame.K_v,
        }

        self.assets = {
            "player": load_image("entities/player"),
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "sand": load_images("tiles/sand"),
            "large_decor": load_images("tiles/large_decor"),
            "grass_tuft": load_images("tiles/grass_tuft"),
            "stone": load_images("tiles/stone"),
            "spawners": load_images("tiles/spawners"),
            "misc": load_images("tiles/misc"),
            "collectables": load_images("items/collectables"),
            "background": load_image("background"),
            "clouds": load_images("clouds"),
            "keys": load_keys("keys/pc/dark"),

            "player/idle": Animation(load_images("entities/player/idle"), 6),
            "player/run": Animation(load_images("entities/player/run"), 4),
            "player/jump": Animation(load_images("entities/player/jump"), 5),
            "player/slide": Animation(load_images("entities/player/slide"), 5),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide"), 5),

            "player/sword_idle": Animation(load_images("entities/player/sword_idle"), 6),
            "player/sword_run": Animation(load_images("entities/player/sword_run"), 4),
            "player/sword_jump": Animation(load_images("entities/player/sword_jump"), 5),
            "player/sword_slide": Animation(load_images("entities/player/sword_wall_slide"), 5),
            "player/sword_wall_slide": Animation(load_images("entities/player/sword_wall_slide"), 5),

            "particle/leaf": Animation(load_images("particles/leaf"), 20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), 6, loop=False),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), 6),
            "enemy/run": Animation(load_images("entities/enemy/run"), 4),
            "slash/idle": Animation(load_images("particles/slash"), 1, loop=False),
            "gun": load_image("gun"),
            "projectile": load_image("projectile"),
            "ButtonSelected": pygame.image.load("data/images/ButtonSelect.png").convert_alpha(),
            "MenuBackground": load_image("MenuBackground"),

            "health": load_image("UI/player_health_pip"),
            "MenuButton": load_image_transparent("UI/MenuButton", (200, 50)),
            "MenuButtonSelected": load_image_transparent("UI/MenuButtonSelected", (200, 50)),
            "DialogueBox": load_image_transparent("UI/DialogueBox", (200, 50)),
        }

        self.sfx = {
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "shoot": pygame.mixer.Sound("data/sfx/shoot.wav"),
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
        }

        self.sfx['ambience'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.3)
        self.sfx['dash'].set_volume(0.1)
        self.sfx['hit'].set_volume(0.5)
        self.sfx['shoot'].set_volume(0.2)
        pygame.mixer.music.load("data/music.wav")

        #   Player INIT and Tilemap INIT
        self.player = Player(self, [50, 50], [8, 15], speed=2, max_health=3, health=3)
        self.tilemap = Tilemap(self, tile_size=32)

        #   Handle Map Initializing
        self.level = 0
        self.max_level = 0
        for f in os.scandir("data/maps"):
            if f.is_file():
                self.max_level += 1
        self.load_level(self.level)
        self.clouds = Clouds(self.assets['clouds'], count=6)

        logging.info("Max Level:" + str(self.max_level))

    def load_level(self, map_id, transition=True):

        # If map_id is equal to self.max_level, set it to 1 to avoid loading the first level again
        if map_id == self.max_level:
            self.level = 1
            map_id = 1

        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract(id_pairs=[('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], [8, 15], speed=1, leeway=(2, 5)))

        if map_id != 1 and transition:
            self.transition = -30
            self.scroll = [self.player.rect().centerx - self.display.get_width() / 2,
                           self.player.rect().centery - self.display.get_height() / 2]

        else:
            self.transition = 0
            # Smoothly transition the scroll to the player's position
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20


        self.particles = []
        self.projectiles = []
        self.sparks = []
        self.player.air_time = 0
        self.player.death = 0
        self.movement = [False, False]
        self.player.dashing = [0, 0]
        self.player.attacking = 0
        self.player.jump_cooldown = 30
        self.dialogues = []


    def key(self, key, x=0):
        return pygame.key.name(self.keybinds[key][x])
    def handle_music(self):
        if self.music:
            self.sfx['ambience'].play(-1)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)

        logging.info("state: " + str(self.state))

    def handle_player(self):
        if self.player.health <= 0:
            self.load_level(self.level)
            self.player.health = self.player.max_health
        else:
            if self.debugging:
                self.player.draw_hitbox()
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=self.render_scroll)

    def handle_UI(self):
        for ui in self.UIs:
            ui.update(self.full_display, leng=[self.player.health, 1])
            ui.render(self.full_display)
        for d in self.dialogues:
            d.update(self.full_display)
            d.render(self.full_display)


    def run(self):

        self.handle_music()
        #self.dt = time.time() - self.start

        if self.state == "Game":
            self.UIs.append(UI(self, img=self.assets["health"], leng=[self.player.health, 1], size=[64, 64]))
            #self.dialogues.append(Dialogue(self, [80, 850, 1760, 200], f"Welcome to the game I still have not named. "
            #                                                           f"To move around press {self.key('Move Left')} and {self.key('Move Right')} or {self.key('Move Left', 1)} and {self.key('Move Right', 1)}. To jump press {self.key('Jump')} or {self.key('Jump', 1)}. To dash press {self.key('Dash')} or {self.key('Dash', 1)}. "
            #                               f"You can also dash in any different directions based on the keys you are pressing. Your health is displayed in the top left. Currently you have a max of {self.player.max_health} health. You can upgrade this later, but for now lets get you going! The last thing is to press {self.key('Attack')} or {self.key('Attack', 1)} to attack or get rid of these annoying pop ups. If you kill all the enemies in the level, you will continue on.",
            #                               text_color=(255, 255, 255), img=self.assets["DialogueBox"]))

            # Screen is 480x270
            pass

        while self.state == 'Game':
            self.display.fill([0, 0, 0, 0])  # Clear the display
            self.full_display.fill([0, 0, 0, 0])  # Clear the full display
            self.outline.blit(pygame.transform.scale(self.assets['background'], self.zoom_size), (0, 0))
            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):  # If no enemies are left next level
                self.transition += 1
                if self.transition > 30:
                    self.level += 1
                    self.load_level(self.level)


            if self.transition < 0:
                self.transition += 1

            # Handle Camera
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[
                0]) / 20  # 20 is the smoothness of the camera and the distance away from the character to lag behind
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[
                1]) / 20 - 0.75  # 0.75 is the offset to make the player appear lower on the screen
            self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Handle Leaves
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:  # bigger number = less leaves
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(
                        Particle(self, 'leaf', pos, velocity=(-0.11, 0.3), frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.outline, offset=self.render_scroll, mod=True)
            self.tilemap.render(self.display, offset=self.render_scroll)

            # Handle Enemies
            for enemy in self.enemies:
                enemy.update(self.tilemap, (0, 0))
                if self.debugging:
                    enemy.draw_hitbox()
                enemy.render(self.display, offset=self.render_scroll)



            # (x, y), direction, timer
            for projectile in self.projectiles:
                projectile[0][0] += projectile[1][0]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - self.render_scroll[1]))

                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)  # remove if colliding with wall
                    for i in range(4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[0][1] > 0 else 0),
                                  2 + random.random()))

                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)

                if self.player.rect().collidepoint(projectile[0]):  # it hit the player
                    if (abs(self.player.dashing[0]) < 30 and abs(
                            self.player.dashing[1]) < 30):  # after first 30 frames of dashing
                        self.projectiles.remove(projectile)
                        self.player.hurt(1)
                        self.screenshake = max(32, self.screenshake)

                        #   Make Explosion
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                     math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))
                    else:
                        self.projectiles.remove(projectile)
                        logging.info("projectile removed")

            for spark in self.sparks:
                kill = spark.update()
                spark.render(self.display, offset=self.render_scroll)
                if kill:
                    self.sparks.remove(spark)


            self.handle_player()


            display_mask = pygame.mask.from_surface(self.display)
            display_sillouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # outline
                self.outline.blit(display_sillouette, offset)

            for particle in self.particles:
                kill = particle.update()
                particle.render(self.display, offset=self.render_scroll)

                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            if self.transition:
                transition_surf = pygame.Surface((self.display.get_size()))
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                       random.random() * self.screenshake - self.screenshake / 2)

            if self.debugging:
                fps = self.clock.get_fps()
                fps_text = pygame.font.Font(None, 30).render(f"FPS: {fps:.2f}", True, (255, 255, 255))
                self.display.blit(fps_text, (self.display.get_width() - fps_text.get_width(), 0))





            #   Handle Basic Clockrate and Displays
            self.clock.tick(60)
            self.events()
            self.outline.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.outline, self.screen_size), self.screenshake_offset)
            self.screen.blit(pygame.transform.scale(self.full_display, self.screen_size), [0, 0])





            pygame.display.update()

        #   Handle Menu States
        for state in self.menu_states:
            if self.state == "Main Menu":
                self.buttons = []
                self.load_level(0)
                self.buttons.append(Button(self, (100, 100, 200, 50), text="Start", type="start", imgs="MenuButton"))
                self.buttons.append(Button(self, (100, 200, 200, 50), text="Options", type="options", imgs="MenuButton"))
                self.buttons.append(Button(self, (100, 300, 200, 50), text="Quit", type="quit", imgs="MenuButton"))
                print("Menu Loaded")

            while self.state == state:
                if self.state != "Main Menu":
                    handle_state(self, state)

                else:   # Handle Menu Animation
                    self.display.fill((0, 0, 0, 0))  # Clear the display

                    self.outline.blit(pygame.transform.scale(self.assets['background'], self.zoom_size), (0, 0))
                    # Handle Camera
                    self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) - 35
                    self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) - 20
                    self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                    # Handle Leaves
                    for rect in self.leaf_spawners:
                        if random.random() * 49999 < rect.width * rect.height:  # bigger number = less leaves
                            pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                            self.particles.append(
                                Particle(self, 'leaf', pos, velocity=(-0.11, 0.3), frame=random.randint(0, 20)))

                    #self.clouds.update()
                    #self.clouds.render(self.outline, offset=self.render_scroll)
                    self.tilemap.render(self.display, offset=self.render_scroll)

                    self.movement[1] = True
                    self.handle_player()

                    if self.tilemap.misc_tile_check(self.player.pos):  # Jump if the player is on a bouncer
                        self.player.jump(strength=1.2)

                    display_mask = pygame.mask.from_surface(self.display)
                    display_sillouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                    for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # outline
                        self.outline.blit(display_sillouette, offset)




                    #   Handle Basic Clockrate and Displays
                    self.clock.tick(self.framerate)
                    self.outline.blit(self.display, (0, 0))
                    self.events()
                    self.screen.blit(pygame.transform.scale(self.outline, self.screen_size), self.screenshake_offset)
                    self.screen.blit(pygame.transform.scale(self.full_display, self.screen_size), [0, 0])

                    for button in self.buttons:
                        button.render(self.full_display)

                    pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                self.screen_size = event.size
                self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                print("Screen size changed to: " + str(self.screen_size) + " aspect ratio is now " + str(
                    self.screen_size[0] / self.screen_size[1]))

            if self.state == "Game":
                if event.type == pygame.KEYDOWN:
                    if event.key in self.keybinds["Move Left"]:
                        self.movement[0] = True
                    if event.key in self.keybinds["Move Right"]:
                        self.movement[1] = True
                    if event.key in self.keybinds["Jump"]:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key in self.keybinds["Face Up"]:
                        self.up = True
                    if event.key in self.keybinds["Face Down"]:
                        self.down = True
                    if event.key in self.keybinds["Dash"]:
                        self.player.dash()
                    if event.key in self.keybinds["Attack"]:
                        self.player.attack()
                        logging.info("Attack called")
                        for d in self.dialogues:
                            if d.done:
                                self.dialogues.remove(d)
                    if event.key == pygame.K_EQUALS:
                        self.zoom_size = [self.zoom_size[0] + 4, self.zoom_size[1] + 3]
                        self.display = pygame.Surface(self.zoom_size, pygame.SRCALPHA)
                        self.outline = pygame.Surface(self.zoom_size)
                        logging.info("Zoom changed to: " + str(self.zoom_size))
                    if event.key == pygame.K_MINUS:
                        self.zoom_size = [self.zoom_size[0] - 4, self.zoom_size[1] - 3]
                        self.display = pygame.Surface(self.zoom_size, pygame.SRCALPHA)
                        self.outline = pygame.Surface(self.zoom_size)
                        logging.info("Zoom changed to: " + str(self.zoom_size))
                    if event.key == pygame.K_F3:
                        self.debugging = not self.debugging
                    if event.key == self.keybinds["Restart"]:
                        self.load_level(self.level)
                        self.player.death = 0
                    if event.key == self.keybinds["Pause"]:
                        self.state = "Pause"
                    if self.ADMIN and event.key == pygame.K_KP0:
                        self.level += 1
                        self.load_level(self.level)

                if event.type == pygame.KEYUP:
                    if event.key in self.keybinds["Move Left"]:
                        self.movement[0] = False
                    if event.key in self.keybinds["Move Right"]:
                        self.movement[1] = False
                    if event.key in self.keybinds["Face Up"]:
                        self.up = False
                    if event.key in self.keybinds["Face Down"]:
                        self.down = False

            if self.state == "Pause":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.state = "Game"

            if self.state == "Keybinds":
                if event.type == pygame.KEYDOWN:
                    if self.selected_keybind_button is not None:
                        # Update the keybind for the selected action
                        action_name = self.selected_keybind_button.text

                        self.key_code = pygame.key.key_code(pygame.key.name(event.key))

                        self.keybinds[action_name] = [self.key_code]

                        print(f"Keybind for {action_name} changed to {pygame.key.name(event.key)}")

                    self.selected_keybind_button = None  # Reset selected button after updating keybind

                    if event.key == pygame.K_ESCAPE:
                        self.state = "Options"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle mouse click to select a keybind button
                    for button in self.buttons:
                        if button.type == "keybind" and button.rect.collidepoint(event.pos):
                            self.selected_keybind_button = button
                            print(f"Selected keybind for {self.selected_keybind_button.text}")

            if self.state in ['Main Menu', 'Pause', 'Options', 'Resolution']:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state = 'Game'
                        return True
                    if event.key == pygame.K_SLASH:
                       print(self.button_selected)
                    if event.key == pygame.K_UP:
                        self.button_selected -= 1
                        if self.button_selected < 0:
                            self.button_selected = len(self.buttons) - 1
                    if event.key == pygame.K_DOWN:
                        self.button_selected += 1
                        if self.button_selected > len(self.buttons) - 1:
                            self.button_selected = 0

                    if event.key == pygame.K_z:
                        if self.state == "Keybinds":
                            pass
                        elif self.state == "Resolution":
                            self.screen.blit(pygame.transform.scale(self.outline, self.screen_size),
                                             self.screenshake_offset)
                            self.screen.blit(pygame.transform.scale(self.full_display, self.screen_size), [0, 0])

                        else:
                            self.state = self.buttons[self.button_selected].action(self)
                            self.button_selected = 0

                        if self.state == "Quit":
                            pygame.quit()
                            sys.exit()




if __name__ == "__main__":
    game = Game()

    while True:
        game.run()