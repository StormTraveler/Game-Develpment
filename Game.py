#!/usr/bin/env pypy
import logging
import sys
from array import array
from Scripts.Enemy import Zenith
from Scripts.Player import Player
from Scripts.Utils import *
from Scripts.Tilemap import Tilemap
from Scripts.Celestials import CloudManager, StarManager
from Scripts.particle import Particle, Spark
from Scripts.UI import UI, Button, Dialogue
from Scripts.grass import *
from Scripts.Menu import *
import threading
import json
import socket
# Pushed as of the 3/29


#SF = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
SF = 1
logging.debug("Scale Factor is " + str(SF))
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
        pygame.mixer.init()
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
        # self.screen_size = [1920, 1080]
        self.resolutions = [(640, 360), (854, 480), (960, 540),
                            (1024, 576), (1280, 720), (1366, 768),
                            (1600, 900), (1920, 1080)]
        self.zoom_size = [480, 270]  # 16:9 aspect ratio 480:270
        self.scale_factor = {1: 4, 1.25: 3.2}.get(SF)
        self.screen_size = [self.zoom_size[0] * self.scale_factor, self.zoom_size[1] * self.scale_factor]

        self.screen = pygame.display.set_mode(self.screen_size, pygame.OPENGL | pygame.DOUBLEBUF)
        self.full_display = pygame.Surface([1920, 1080], pygame.SRCALPHA | pygame.OPENGL | pygame.DOUBLEBUF)
        self.display = pygame.Surface(self.zoom_size, pygame.SRCALPHA | pygame.OPENGL | pygame.DOUBLEBUF)
        self.outline = pygame.Surface(self.zoom_size, pygame.OPENGL | pygame.DOUBLEBUF)

        self.outline.set_alpha(None)
        self.clock = pygame.time.Clock()
        self.state = "Main Menu"
        self.movement = [False, False]
        self.scroll = [0, 0]
        self.buttons = []
        self.sliders = []
        self.UIs = []
        self.dialogues = []

        self.debugging = False
        self.up = False
        self.down = False
        self.dragging = False
        self.button_selected = 0
        self.selected_keybind_button = None
        self.key_code = None
        self.music = False
        self.clouds_enabled = True
        self.stars_enabled = True
        self.ADMIN = False

        self.menu_states = ["Main Menu", "Pause", "Options", "Keybinds", "Audio", "Video", "Inventory"]
        self.screenshake = 0
        self.master_volume = 1.0
        self.sfx_volume = 0.3
        self.music_volume = 0.3
        self.framerate = 60
        self.start = time.time()
        self.grass_time = 0


        #multiplayer variables
        self.host = False
        self.client = False
        self.server_ip = None
        self.server_port = None
        self.players = {}
        self.actions = {}
        self.SIGNALING_SERVER_IP = '198.211.117.27'
        self.SIGNALING_SERVER_PORT = 5555
        self.player_name = 'Storm'
        self.peer_ip = None
        self.peer_port = None
        self.connected = False

        # Local UDP socket for punching
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))  # Bind to random available port



        self.gm = GrassManager('data/images/grass/medium_dark', tile_size=16, stiffness=600, max_unique=5, place_range=[1, 1])
        self.gm.enable_ground_shadows(shadow_radius=4, shadow_color=(0, 0, 1), shadow_shift=(1, 2))

        with open('data/shaders/vert.shd', 'r') as v:
            self.vert_shader = v.read()
        with open('data/shaders/frag.shd', 'r') as f:
            self.frag_shader = f.read()

        self.ctx = moderngl.create_context()
        self.program = self.ctx.program(vertex_shader=self.vert_shader, fragment_shader=self.frag_shader)
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 0.0,  # topleft
            1.0, 1.0, 1.0, 0.0,  # topright
            -1.0, -1.0, 0.0, 1.0,  # bottomleft
            1.0, -1.0, 1.0, 1.0,  # bottomright
        ]))


        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

        self.collectables = {
            key: self.ADMIN for key in ["Dash", "Double Jump", "Wall Climb", "Sword Charge", "Health"]}

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
            "grass_blades": load_images("tiles/grass_blades"),
            "stone": load_images("tiles/stone"),
            "cave": load_images("tiles/cave"),
            "spawners": load_images("tiles/spawners"),
            "misc": load_images("tiles/misc"),
            "collectables": load_images("items/collectables"),
            "jungle": load_images("tiles/jungle"),
            "dark_grass": load_images("tiles/dark_grass"),
            "background": pygame.transform.scale(load_image("backgrounds/background"), self.zoom_size),
            "clouds": load_images("celestials/clouds"),
            "stars": load_images("celestials/stars"),
            "foliage": load_images("foliage"),
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

            "zenith/red/idle": Animation(load_images("entities/zenith/red/idle"), 6),
            "zenith/red/run": Animation(load_images("entities/zenith/red/run"), 4),
            "zenith/green/idle": Animation(load_images("entities/zenith/green/idle"), 6),
            "zenith/green/run": Animation(load_images("entities/zenith/green/run"), 4),
            "zenith/blue/idle": Animation(load_images("entities/zenith/blue/idle"), 6),
            "zenith/blue/run": Animation(load_images("entities/zenith/blue/run"), 4),

            "particle/leaf": Animation(load_images("particles/leaf"), 20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), 6, loop=False),
            "particle/charge_particle": Animation(load_images("particles/charge_particle"), 6, loop=False),

            "slash/idle": Animation(load_images("particles/slash"), 1, loop=False),
            "pistol": load_image("pistol"),
            "ak": load_image("ak"),
            "burst": load_image("burst"),
            "bullet": load_image("bullet"),

            "ButtonSelected": pygame.image.load("data/images/ButtonSelect.png").convert_alpha(),
            "MenuBackground": load_image("backgrounds/MenuBackground"),

            "health": load_image("UI/player_health_pip"),
            "coin": load_image("UI/coin"),
            "MenuButton": load_image("UI/MenuButton"),
            "MenuButtonSelected": load_image("UI/MenuButtonSelected"),
            "DialogueBox": load_image_transparent("UI/DialogueBox", (200, 50)),
        }

        self.sfx = {
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "shoot": pygame.mixer.Sound("data/sfx/shoot.wav"),
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
            "charging": pygame.mixer.Sound("data/sfx/charging.wav"),
            "charged": pygame.mixer.Sound("data/sfx/charged.wav"),
        }

        self.sfx["jump"].set_volume(0.3 * self.sfx_volume)
        self.sfx["dash"].set_volume(0.2 * self.sfx_volume)
        self.sfx["hit"].set_volume(0.5 * self.sfx_volume)
        self.sfx["shoot"].set_volume(0.2 * self.sfx_volume)
        self.sfx["ambience"].set_volume(0.3 * self.sfx_volume)
        self.sfx["charging"].set_volume(0.5 * self.sfx_volume)
        self.sfx["charged"].set_volume(0.5 * self.sfx_volume)

        pygame.mixer.music.load("data/music.wav")

        #   Player INIT and Tilemap INIT
        self.player = Player(self, [50, 50], [8, 15], speed=2, max_health=3, health=3)
        self.tilemap = Tilemap(self, tile_size=16)

        #   Handle Map Initializing
        self.level = 0
        self.max_level = -1
        for f in os.scandir("data/maps"):
            if f.is_file():
                self.max_level += 1
        self.load_level(self.level)
        if self.clouds_enabled:
            self.cloud_manager = CloudManager(self.assets['clouds'], count=6)
        if self.stars_enabled:
            self.star_manager = StarManager(self.assets['stars'], count=8)

        logging.info("Max Level:" + str(self.max_level))

        self.multiplayer_thread = threading.Thread(target=self.handle_multiplayer, daemon=True)
        self.multiplayer_thread.start()



    def load_level(self, map_id, transition=True):

        # If map_id is equal to self.max_level, set it to 1 to avoid loading the first level again
        if map_id == self.max_level:
            self.level = 1
            map_id = 1

        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.gm.grass_tiles = {}
        self.leaf_spawners = []
        for tree in self.tilemap.extract(id_pairs=[('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        # Define a dictionary to map spawner variants to gun types
        variant_to_gun_type = {
            1: "pistol",
            2: "ak",
            3: "burst"
        }

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                gun_type = variant_to_gun_type.get(spawner['variant'])
                if gun_type:
                    self.enemies.append(
                        Zenith(self, spawner['pos'], [8, 15], speed=1, leeway=(2, 5), gun_type=gun_type))

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
            pygame.mixer.music.set_volume(0.5 * self.music_volume)
            pygame.mixer.music.play(-1)

        logging.info("state: " + str(self.state))

    def update_volumes(self):
        # Apply master volume to all sound effects
        self.sfx["jump"].set_volume(0.3 * self.sfx_volume * self.master_volume)
        self.sfx["dash"].set_volume(0.2 * self.sfx_volume * self.master_volume)
        self.sfx["hit"].set_volume(0.5 * self.sfx_volume * self.master_volume)
        self.sfx["shoot"].set_volume(0.2 * self.sfx_volume * self.master_volume)
        self.sfx["ambience"].set_volume(0.3 * self.sfx_volume * self.master_volume)
        self.sfx["charged"].set_volume(0.5 * self.sfx_volume * self.master_volume)
        self.sfx["charging"].set_volume(0.5 * self.sfx_volume * self.master_volume)

        # Apply master volume to music
        pygame.mixer.music.set_volume(0.5 * self.music_volume * self.master_volume)


    def handle_player(self):
        if self.player.health <= 0:
            self.load_level(self.level)
            self.player.health = self.player.max_health
        else:
            if self.debugging:
                self.player.draw_hitbox()
            # Multiply the player's speed by self.dt
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0),
                               speed=self.player.speed * self.dt + 120 // self.framerate)
            self.player.render(self.display, offset=self.render_scroll)

            for name, pos in self.players.items(): # render multiplayer
                if name != self.player_name:  # Avoid rendering the current player twice
                    self.display.blit(
                                            self.assets["player/idle"].img(),
                                            (int(pos[0] - self.scroll[0]), int(pos[1] - self.scroll[1]))
                                        )
    def handle_enemies(self):
        for enemy in self.enemies:
            enemy.update(self.tilemap, (0, 0), offset=self.render_scroll)
            if self.debugging:
                enemy.draw_hitbox()
            enemy.render(self.display, offset=self.render_scroll)


    def handle_UI(self):
        for ui in self.UIs:
            if ui.type == 'Health':
                ui.update(self.full_display, leng=[self.player.health, 1])
            else:
                ui.update(self.full_display)

            ui.render(self.full_display)

        fps = self.clock.get_fps()
        fps_text = pygame.font.Font(None, 20).render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        self.display.blit(fps_text, (self.display.get_width() - fps_text.get_width(), 0))

        money_text = pygame.font.Font(None, 30).render(f"{self.player.coins}", True, (205, 220, 25))
        self.display.blit(money_text, (16, 16))


    def handle_dialogues(self):
        for d in self.dialogues:
            d.update()
            d.render(self.full_display)


    def handle_celestials(self):
        if self.stars_enabled:
            self.star_manager.render(self.outline, offset=self.render_scroll, mod=True)

        if self.clouds_enabled:
            self.cloud_manager.update()
            self.cloud_manager.render(self.outline, offset=self.render_scroll, mod=True)


    def handle_transition_graphics(self):
        if self.transition:
            transition_surf = pygame.Surface((self.display.get_size()))
            pygame.draw.circle(transition_surf, (255, 255, 255),
                               (self.display.get_width() // 2, self.display.get_height() // 2),
                               (30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))


    def create_explosion(self, x, y):
        for i in range(30):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.sparks.append(Spark((x, y), angle, 2 + random.random()))
            self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                     math.sin(angle + math.pi) * speed * 0.5],
                                           frame=random.randint(0, 7)))


    def create_sparks(self, x, y, flipped):
        for i in range(4):
            self.sparks.append(
                Spark((x, y), random.random() - 0.5 + (math.pi if flipped else 0),
                      2 + random.random()))

    def setup_connection(self):
        # Connect to signaling server
        tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_conn.connect((self.SIGNALING_SERVER_IP, self.SIGNALING_SERVER_PORT))
        except Exception as e:
            logging.critical(f"[ERROR] Failed to connect to signaling server: {e}")
            print("[WARNING] Failed to connect to signaling server. Please check your internet connection and server.")
            return
        # Get the local UDP port of this client
        local_udp_port = self.sock.getsockname()[1]

        # Send it to the signaling server
        tcp_conn.send(str(local_udp_port).encode())

        # Wait for opponent inf
        peer_info = tcp_conn.recv(1024).decode()
        print(f"Got peer info: {peer_info}")
        self.peer_ip, self.peer_port = peer_info.split(":")
        self.peer_port = int(self.peer_port)

        tcp_conn.close()

        # NAT punching: send dummy packet to peer
        print(f"Punching to {self.peer_ip}:{self.peer_port}")
        for _ in range(10):  # send multiple times just in case
            self.sock.sendto(b"punch", (self.peer_ip, self.peer_port))

    def handle_multiplayer(self):
        if not self.connected:
            self.setup_connection()
            self.connected = True

        if self.peer_ip and self.peer_port:
            print(f"[INFO] Connected to peer at {self.peer_ip}:{self.peer_port}")
            while self.state != "Quit":
                # Prepare and send data
                data = [{"player": [self.player_name, self.player.pos], "actions": self.actions}]
                serialized_data = json.dumps(data)
                self.send_packet(serialized_data)
                logging.debug(f"[SEND] {serialized_data}")
                self.actions = []  # Clear sent actions

                try:
                    received_data = self.listen_for_data()
                    if not received_data:
                        continue  # No data? Try again next frame

                    test_packet = [{"player": ["Andranik", [-91.5835176538054, 241]], "actions": []}]


                    # Handle received data
                    logging.debug(f"received data: {received_data}")
                    try:
                        # Ensure received_data is deserialized properly
                        if isinstance(received_data, str):
                            received_data = json.loads(received_data)

                        # Access the data safely
                        if isinstance(received_data, list) and "player" in received_data[0]:
                            name = received_data[0]["player"][0]
                            pos = received_data[0]["player"][1]
                            logging.info(f"[RECV] Player: {name}, Position: {pos}")
                            self.players[name] = pos
                        else:
                            logging.critical(f"[ERROR] Invalid data structure: {received_data}")

                    except Exception as e:
                        logging.critical(f"[ERROR] Failed to unpack received data: {e}")

                except Exception as e:
                    logging.critical(f"[ERROR] Multiplayer handling failed: {e}")

                # Sync with game loop to avoid spamming
                time.sleep(1 / 30) # Limit packets to 30 FPS

        else:
            logging.critical("[ERROR] No peer IP and port set. Cannot send data.")

    def send_packet(self, data):
        self.sock.sendto(json.dumps(data).encode(), (self.peer_ip, self.peer_port))

    def listen_for_data(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            decoded = data.decode().strip()

            # Attempt to parse the received data into a JSON object
            decoded_json = json.loads(decoded)

            logging.info(f"[INFO] Received packet from {addr}: {decoded_json}")

            return decoded_json

        except json.JSONDecodeError:
            # Handle the case where the received data is not valid JSON
            logging.info(f"[INFO] Ignoring non-JSON packet from {addr}: {decoded}")
            return []

        except Exception as e:
            logging.critical(f"Error receiving: {e}")
            return []

    def handle_grass(self):
        # ooga booga do some magic, make grass blow in the wind
        self.t = time.time() - self.start
        phase_shift = self.t * 2
        rot_function = lambda x, y: (
            min(int((
                    math.sin(phase_shift - x * 0.2) * 20)),
                140 - (x % 2))
        )
        #lambda x, y: min(int((math.sin(phase_shift - x * 16 / 180) * 20)), 140 - (x % 2))
        # Honestly I have no idea what is going on here ^.^ but it works???
        return rot_function


    def render_screen(self, menu=False):
        #self.program['time'] = (time.time() - self.start) * 10

        if menu:
            for slider in self.sliders:
                slider.render(self.full_display)
            self.screen.blit(pygame.transform.scale(self.outline, self.screen_size), (0, 0))
            self.screen.blit(self.full_display, [0, 0])

            pygame.display.flip()
            frame_tex = self.surf_to_texture(self.screen)
            frame_tex.use(0)
            self.program['tex'] = 0
            self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

            frame_tex.release()

        else:
            self.outline.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.outline, self.screen_size), self.screenshake_offset)
            self.screen.blit(self.full_display, [0, 0])

            pygame.display.flip()
            frame_tex = self.surf_to_texture(self.screen)
            frame_tex.use(0)
            self.program['tex'] = 0
            self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

            frame_tex.release()


    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))

        return tex


    def run(self):

        self.handle_music()
        self.dt = time.time() - self.start
        last_frame_time = time.time()

        if self.state == "Game":
            self.UIs.append(
                UI(self, img=self.assets["health"], leng=[self.player.health, 1], size=[64, 64], type="Health"))
            self.UIs.append(UI(self, pos=[0, 64], img=self.assets["coin"], size=[64, 64], leng=(1, 1), type="Coin"))

            self.dialogues.append(Dialogue(self, [80, 850, 1760, 200], f"Welcome to Horizon's Embrace. You are now stuck in the Realm of Isoria."
                                                                       f"To move around press {self.key('Move Left')} and {self.key('Move Right')} or {self.key('Move Left', 1)} and {self.key('Move Right', 1)}. To jump press {self.key('Jump')} or {self.key('Jump', 1)}. "
                                                                       f"Your health is displayed in the top left. Currently you have a max of {self.player.max_health} health. You can upgrade this later, but for now lets get you going! "
                                                                       f"The last thing is to press {self.key('Attack')} to attack or get rid of these annoying pop ups. If you kill all the enemies in the level, you will continue on. ",
                                           text_color=(255, 255, 255), img=self.assets["DialogueBox"]))

        while self.state == 'Game':
            self.display.fill([0, 0, 0, 0])  # Clear the display
            self.full_display.fill([0, 0, 0, 0])  # Clear the full display
            self.outline.blit(self.assets['background'], (0, 0))
            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):  # If no enemies are left go to next level
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

            self.tilemap.render(self.display, offset=self.render_scroll)

            self.gm.update_render(self.display, self.dt, offset=self.render_scroll,
                                  rot_function=self.handle_grass())

            # (x, y), direction, timer, bounced

            for spark in self.sparks:
                spark.render(self.display, offset=self.render_scroll)
                if spark.update():
                    self.sparks.remove(spark)

            for particle in self.particles:
                particle.render(self.display, offset=self.render_scroll)

                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3

                if particle.update():
                    self.particles.remove(particle)

            player_thread = threading.Thread(target=self.handle_player)
            enemies_thread = threading.Thread(target=self.handle_enemies)
            celestials_thread = threading.Thread(target=self.handle_celestials)
            events_thread = threading.Thread(target=self.events)
            player_thread.start()
            enemies_thread.start()
            celestials_thread.start()
            events_thread.start()

            # self.handle_player()
            # self.handle_enemies()
            # self.handle_celestials()

            # Create the outline effect
            display_mask = pygame.mask.from_surface(self.display)
            display_sillouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.outline.blit(display_sillouette, offset)

            self.screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                       random.random() * self.screenshake - self.screenshake / 2)

            # Anything after this won't be affected by the outline
            # Make sure that the tilemap and grass is rendered after the outline offset is applied

            self.player.render(self.display, offset=self.render_scroll)
            for enemy in self.enemies:
                enemy.render(self.display, offset=self.render_scroll)

            for projectile in self.projectiles:
                projectile.update()
                projectile.render(self.display, offset=self.render_scroll)

            self.handle_transition_graphics()

            #   Handle Basic Clockrate and Displays

            current_time = time.time()
            self.dt = current_time - last_frame_time
            last_frame_time = current_time

            self.handle_UI()
            self.handle_dialogues()
            self.render_screen()
            self.clock.tick(self.framerate)

        #   Handle Menu States
        for state in self.menu_states:
            if self.state == "Main Menu":
                self.load_level(0)
                self.buttons = get_buttons(self, state)
                self.sliders = get_sliders(self, state) or []
                logging.info('intializing main menu')
            else:
                self.buttons = get_buttons(self, state)
                self.sliders = get_sliders(self, state) or []

            while self.state == state:
                if self.state != "Main Menu":
                    self.full_display.fill((0, 0, 0, 0))  # Clear the full display

                    # Handle Camera
                    self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) - 35
                    self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) - 20
                    self.render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                    #   Handle Basic Clockrate and Displays
                    self.clock.tick(self.framerate)
                    self.outline.blit(self.display, (0, 0))
                    self.events()

                    for button in self.buttons:
                        button.render(self.full_display)

                    self.render_screen(menu=True)

                else:  # Handle Menu Animation
                    if self.level > 0:
                        self.load_level(0)
                        self.level = 0

                    self.display.fill((0, 0, 0, 0))  # Clear the display
                    self.outline.blit(pygame.transform.scale(self.assets['background'], self.zoom_size), (0, 0))
                    self.movement[1] = True

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

                    self.handle_celestials()

                    self.tilemap.render(self.display, offset=self.render_scroll)

                    if self.tilemap.misc_tile_check(self.player.pos):  # Jump if the player is on a bouncer
                        self.player.jump(strength=1.2)

                    self.handle_player()
                    self.events()
                    #   Handle Basic Clockrate and Displays
                    self.clock.tick(self.framerate)
                    self.outline.blit(self.display, (0, 0))

                    for button in self.buttons:
                        button.render(self.full_display)

                    self.render_screen(menu=True)


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "quit"
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                self.screen_size = event.size
                self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                logging.info("Screen size changed to: " + str(self.screen_size) + " aspect ratio is now " + str(
                    self.screen_size[0] / self.screen_size[1]))

            if self.state == "Game":
                keys = pygame.key.get_pressed()
                if any(keys[k] for k in self.keybinds["Move Left"]):
                    self.movement[0] = True
                elif any(keys[k] for k in self.keybinds["Move Right"]):
                    self.movement[1] = True
                else:
                    self.movement[0] = False
                    self.movement[1] = False

                if event.type == pygame.KEYDOWN:
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
                        dialogue_skipped = False
                        for d in self.dialogues:
                            if d.done:
                                self.dialogues.remove(d)
                                dialogue_skipped = True
                        if not dialogue_skipped:
                            self.player.attack()
                            logging.info("Attack called")
                            if self.collectables["Sword Charge"]:
                                self.player.start_charging()

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
                    if self.ADMIN and event.key == pygame.K_KP1:
                        self.level -= 1
                        self.load_level(self.level)
                    # Swap admin if tilde is pressed
                    if event.key == pygame.K_BACKQUOTE:
                        self.ADMIN = not self.ADMIN


                if event.type == pygame.KEYUP:
                    if event.key in self.keybinds["Move Left"]:
                        self.movement[0] = False
                    if event.key in self.keybinds["Move Right"]:
                        self.movement[1] = False
                    if event.key in self.keybinds["Face Up"]:
                        self.up = False
                    if event.key in self.keybinds["Face Down"]:
                        self.down = False
                    if event.key in self.keybinds["Attack"]:
                        self.player.stop_charging()

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

                    self.selected_keybind_button = None  # Reset selected button after updating keybind

                    if event.key == pygame.K_ESCAPE:
                        self.state = "Options"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle mouse click to select a keybind button
                    for button in self.buttons:
                        if button.type == "keybind" and button.rect.collidepoint(event.pos):
                            self.selected_keybind_button = button

            if self.state in ['Main Menu', 'Pause', 'Options', 'Video', 'Audio']:
                for slider in self.sliders:  # Use a different variable name in the loop
                    slider.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state = 'Game'
                        return True
                    if event.key == pygame.K_SLASH:
                        logging.info("pressing", self.button_selected)
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
                            self.state = self.buttons[self.button_selected].action(self)
                            logging.info(self.buttons[self.button_selected].action(self))

                            self.button_selected = 0

                        else:
                            self.state = self.buttons[self.button_selected].action(self)
                            self.button_selected = 0

                        if self.state == "Quit":
                            pygame.quit()
                            sys.exit()
                        return None
                    return None
                return None
            return None
        return None


if __name__ == "__main__":
    game = Game()

    while True:
        game.run()

