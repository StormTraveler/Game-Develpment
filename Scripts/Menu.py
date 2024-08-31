from Scripts.UI import Button
import pygame


def handle_state(game, state):
    menu = Menu(game, state)
    game.buttons = menu.get_buttons()
    menu.update()


class Menu:
    def __init__(self, game, menu_type):
        self.buttons = []
        self.type = menu_type
        self.game = game

        self.transparent = pygame.Surface(self.game.screen_size)
        self.transparent.fill((80, 190, 240))
        self.transparent.set_alpha(128)
        self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Pause":
            self.buttons.append(Button(self.game, (100, 100, 200, 50), "Resume", type="resume"))
            self.buttons.append(Button(self.game, (100, 200, 200, 50), "Restart", type="restart"))
            self.buttons.append(Button(self.game, (100, 300, 200, 50), "Options", type="options"))
            self.buttons.append(Button(self.game, (100, 400, 200, 50), "Main Menu", type="menu"))
            self.buttons.append(Button(self.game, (100, 500, 200, 50), "Quit", type="quit"))

            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size),
                                  (0, 0))  # Displays Game Screen
            self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Options":
            self.buttons.append(Button(self.game, (100, 100, 200, 50), "Keybinds", type="keybinds"))
            self.buttons.append(Button(self.game, (100, 200, 200, 50), "Resolution", type="resolution"))
            self.buttons.append(Button(self.game, (100, 300, 200, 50), "Back", type="back"))

            self.game.screen.blit(pygame.transform.scale(self.game.outline, self.game.screen_size),
                                  (0, 0))  # Displays Game Screen
            self.game.screen.blit(self.transparent, (0, 0))

        if self.type == "Keybinds":
            buttons_per_screen = self.game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x, iteration = 100, 0

            for key in self.game.keybinds.keys():
                self.buttons.append(Button(self.game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), key,
                                           type="keybind"))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons

        if self.type == "Resolution":
            buttons_per_screen = self.game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x, iteration = 100, 0

            for resolution in self.game.resolutions:
                self.buttons.append(
                    Button(self.game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), resolution,
                           type="resolution"))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons


    def get_buttons(self):
        return self.buttons

    def update(self):
        if self.type == "Main Menu":
            self.game.screen.fill((0, 0, 0))

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

        self.game.selected_coords = (
            self.game.buttons[self.game.button_selected].rect.x - 25,
            self.game.buttons[self.game.button_selected].rect.y - 12.5,
            self.game.buttons[self.game.button_selected].rect.width + 20,
            self.game.buttons[self.game.button_selected].rect.height + 20)



        if not self.game.state == "Keybinds" or self.game.state == "Inventory":
            self.game.screen.blit(self.game.assets["ButtonSelected"], self.game.selected_coords)

        self.game.events()
        self.game.clock.tick(60)

        pygame.display.update()


