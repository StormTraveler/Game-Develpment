from Scripts.UI import Button
import pygame
import moderngl

def menu_render(game):
    game.screen.blit(pygame.transform.scale(game.outline, game.screen_size), (0, 0))
    game.screen.blit(game.full_display, [0, 0])


    pygame.display.flip()
    frame_tex = game.surf_to_texture(game.screen)
    frame_tex.use(0)
    game.program['tex'] = 0
    game.render_object.render(mode=moderngl.TRIANGLE_STRIP)

    frame_tex.release()


def get_buttons(game, state):
    buttons = []
    print(state)
    match state:
        case 'Main Menu':
            buttons.append(Button(game, (100, 100, 200, 50), text="Start", type="start", imgs="MenuButton"))
            buttons.append(Button(game, (100, 200, 200, 50), text="Options", type="options", imgs="MenuButton"))
            buttons.append(Button(game, (100, 300, 200, 50), text="Quit", type="quit", imgs="MenuButton"))
            print("Menu Loaded")
            return buttons


        case 'Pause':
            buttons.append(Button(game, (100, 100, 200, 50), "Resume", type="resume", imgs='MenuButton'))
            buttons.append(Button(game, (100, 200, 200, 50), "Restart", type="restart", imgs='MenuButton'))
            buttons.append(Button(game, (100, 300, 200, 50), "Options", type="options", imgs='MenuButton'))
            buttons.append(Button(game, (100, 400, 200, 50), "Main Menu", type="menu", imgs='MenuButton'))
            buttons.append(Button(game, (100, 500, 200, 50), "Quit", type="quit", imgs='MenuButton'))
            return buttons


        case 'Options':
            buttons.append(Button(game, (100, 100, 200, 50), "Keybinds", type="keybinds", imgs='MenuButton'))
            buttons.append(Button(game, (100, 200, 200, 50), "Resolution", type="resolution", imgs='MenuButton'))
            buttons.append(Button(game, (100, 300, 200, 50), "Back", type="back", imgs='MenuButton'))
            return buttons


        case 'Keybinds':
            buttons_per_screen = game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x, iteration = 100, 0

            for key in game.keybinds.keys():
                buttons.append(Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), key,
                                           type="keybind", imgs='MenuButton'))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons
            return buttons


        case 'Resolution':
            buttons_per_screen = game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x = 100
            iteration = 0

            for resolution in game.resolutions:
                buttons.append(
                    Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), resolution,
                           type="resolution", imgs='MenuButton'))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons

            buttons.append(
                Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), "Back", type="back", imgs='MenuButton'))
            return buttons


class Menuu:
    def __init__(self, game, menu_type):
        self.buttons = []
        self.type = menu_type
        self.game = game

        self.transparent = pygame.Surface(self.game.screen_size)
        self.transparent.fill((80, 190, 240))
        self.transparent.set_alpha(128)
        self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Pause":


            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size),
                                  (0, 0))  # Displays Game Screen
            self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Options":


            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size),
                                  (0, 0))  # Displays Game Screen
            self.game.screen.blit(self.transparent, (0, 0))





    def update(self):
        if self.type == "Pause":
            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size), (0, 0))
            self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Options":
            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size), (0, 0))
            self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Keybinds":
            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size), (0, 0))
            self.game.screen.blit(self.transparent, (0, 0))

        for button in self.game.buttons:
            button.render(self.game.screen)



        self.game.events()
        menu_render(self.game)
        self.game.clock.tick(60)




