import pygame


class Button:

    def __init__(self, game, rect, text, color=(255, 255, 0), type="Caption", image=None):
        self.rect = pygame.Rect(rect)
        self.text = str(text)
        self.color = color
        self.image = image
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont('Arial', 25)
        self.type = type
        self.game = game

    def draw_text(self, surf):
        if self.type == "keybind":
            text_obj = self.font.render(self.text + ": " + pygame.key.name(self.game.keybinds[self.text]), True, self.text_color)
        else:
            text_obj = self.font.render(self.text, True, self.text_color)

        text_rect = self.rect.topleft
        surf.blit(text_obj, text_rect)


    def render(self, surf, offset=(0, 0)):
        pygame.draw.rect(surf, self.color, self.rect)
        self.draw_text(surf)

    def action(self, game):

        if self.type == "resolution_choice":
            game.screen_size = game.resolutions[game.button_selected]
            print("hi")
            return "Options"

        if self.type == "resolution":
            return "Resolution"

        if self.type == "start":
            return "Game"

        if self.type == "options":
            return "Options"

        if self.type == "quit":
            return "Quit"

        if self.type == "resume":
            return "Game"

        if self.type == "restart":
            game.player.dead = 0
            game.load_level(game.level)
            return "Game"

        if self.type == "keybinds":
            return "Keybinds"

        if self.type == "resolution":
            return "Resolution"

        if self.type == "back":
            return "Pause"

        if self.type == "menu":
            return "Main Menu"

