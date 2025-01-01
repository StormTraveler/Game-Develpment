import pygame
from Utils import center_window


class UI:
    def __init__(self, color=None, leng=(1, 1), size=(16, 16), pos=(0, 0), text="", img=None, font=None, type="Caption",
                 text_color=(255, 255, 255)):
        if font is None:
            font = ['Arial', 25]
        self.color = color
        self.text = text
        self.size = list(size)
        self.length = list(leng)
        self.img = img
        self.pos = pos
        self.type = type
        self.text_color = text_color
        self.font = pygame.font.SysFont(font[0], font[1])
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

        if self.img != None:
            self.img = pygame.transform.scale(self.img, (self.size[0], self.size[1]))

    def render(self, surf):
        for y in range(self.length[1]):
            for x in range(self.length[0]):
                if self.img != None:
                    surf.blit(self.img, (self.pos[0] + x * self.size[0], self.pos[1] + y * self.size[1]))

    def update(self, surf, leng=None):
        if leng != None:
            self.length = leng


class Button(UI):
    def __init__(self, game, rect, text, color=(255, 255, 0), type="Caption", image=None, selected_image=None,
                 font=('Arial', 25), text_color=(0, 0, 0), imgs=None):
        super().__init__(color=color, pos=(rect[0], rect[1]), text=text, type=type, font=font, img=image,
                         text_color=text_color)
        self.game = game
        self.rect = pygame.Rect(rect)
        self.selected_img = selected_image
        if imgs is not None:
            self.img = self.game.assets[imgs]
            self.selected_img = self.game.assets[imgs + "Selected"]

    def draw_text(self, surf):
        if self.type == "keybind":
            key_names = self.game.keybinds[self.text]
            if isinstance(key_names, list):
                key_names = ', '.join(pygame.key.name(k) for k in key_names)
            else:
                key_names = pygame.key.name(key_names)
            text_obj = self.font.render(str(self.text) + ": " + str(key_names), True, self.text_color)
        else:
            text_obj = self.font.render(str(self.text), True, self.text_color)

        text_rect = text_obj.get_rect(center=self.rect.center)
        surf.blit(text_obj, text_rect)

    def render(self, surf, offset=(0, 0)):
        if self.img is None:
            pygame.draw.rect(surf, self.color, self.rect)
            self.draw_text(surf)
        else:
            if self.game.buttons[self.game.button_selected] == self:
                if self.selected_img is not None:  # Check if the selected image is not None
                    surf.blit(self.selected_img, (self.rect.x, self.rect.y))  # Render the selected image
                    self.text_color = (255, 255, 255)
                    self.draw_text(surf)
                else:
                    surf.blit(self.img, (self.rect.x, self.rect.y))  # If no selected image, render the normal image
                    self.text_color = (0, 0, 20)
                    self.draw_text(surf)
            else:
                surf.blit(self.img, (self.rect.x, self.rect.y))  # Render the normal image
                self.text_color = (0, 0, 20)
                self.draw_text(surf)

    def action(self, game):

        if self.type == "resolution_choice":
            game.screen_size = game.resolutions[game.button_selected]
            return "Options"

        if self.type == "resolution":
            self.game.screen_size = self.game.resolutions[self.game.button_selected]
            if self.game.resolutions[self.game.button_selected] == (1920, 1080):
                self.game.screen = pygame.display.set_mode(self.game.screen_size, pygame.NOFRAME, pygame.RESIZABLE)
                center_window()
            else:
                self.game.screen = pygame.display.set_mode(self.game.screen_size, pygame.RESIZABLE)
                center_window()

        if self.type == "start":
            self.game.level = 1
            self.game.load_level(self.game.level, transition=False)
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

        if self.type == "video":
            return "Video"

        if self.type == "audio":
            return "Audio"

        if self.type == "back":
            return "Pause"

        if self.type == "menu":
            return "Main Menu"


class Slider(UI):
    def __init__(self, game, rect, min_val, max_val, value, type, color=(255, 255, 255), text="",
                 handle_color=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.type = type
        self.text = text
        self.handle_color = handle_color
        self.game = game
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.color = color
        self.handle_color = handle_color
        self.dragging = False
        # Update handle position based on initial value
        self.handle_rect = self.calculate_handle_rect()

    def calculate_handle_rect(self):
        # Calculate handle position based on current value
        normalized_value = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(normalized_value * self.rect.width)
        return pygame.Rect(handle_x - 5, self.rect.y, 10, 10)

    def set_value_from_mouse_x(self, mouse_x):
        # Clamp mouse_x to slider bounds
        mouse_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width))
        normalized_pos = (mouse_x - self.rect.x) / self.rect.width
        self.value = self.min_val + normalized_pos * (self.max_val - self.min_val)
        self.handle_rect = self.calculate_handle_rect()

        # Handle specific slider types
        if self.type == "music":
            self.game.music_volume = self.value
            pygame.mixer.music.set_volume(self.value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is anywhere on the slider
            if pygame.Rect(self.rect.x, self.rect.y - 5, self.rect.width, 20).collidepoint(event.pos):
                self.dragging = True
                # Immediately move handle to click position
                self.set_value_from_mouse_x(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                print(f"{self.text}: {self.value:.1f}")  # Print final value when released

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_value_from_mouse_x(event.pos[0])

    def render(self, surf):
        pygame.draw.rect(surf, self.color, [self.rect.x, self.rect.y, self.rect.width, 10])
        pygame.draw.rect(surf, self.handle_color, self.handle_rect)

class Dialogue(UI):
    def __init__(self, game, rect, text, color=None, leng=(1, 1), pos=(0, 0), img=None, font=None, type="Caption",
                 text_color=(255, 255, 255)):
        super().__init__(color=color, leng=leng, size=(rect[2], rect[3]), pos=pos, text=text, img=img, font=font,
                         type=type, text_color=text_color)
        self.counter = 0
        self.displayed_text = ""
        self.rect = pygame.Rect(rect)
        self.font = pygame.font.Font("data/images/UI/SlacksideOne-Regular.ttf", 32)
        self.done = False
        self.text_surfaces = []
        self.last_text = None

    def render(self, surf):
        if self.img != None:
            surf.blit(pygame.transform.scale(self.img, self.size), (self.rect[0], self.rect[1]))
        if self.text != "":
            self.draw_text(surf)

    def wrap_text(self, text, width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            # If adding the current word to the current line doesn't exceed the width
            if self.font.size(' '.join(current_line + [word]))[0] <= width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))
        return lines

    def draw_text(self, surf):
        displayed_text = self.text[0:(self.counter // 60)]
        if displayed_text != self.last_text:
            self.text_surfaces = []
            wrapped_text = self.wrap_text(displayed_text, self.rect.width - 20)
            for i, line in enumerate(wrapped_text):
                text_obj = self.font.render(line, True, self.text_color)
                self.text_surfaces.append((text_obj, pygame.Rect(self.rect[0] + 10,
                                                                 self.rect[1] + 5 + i * self.font.get_linesize(),
                                                                 self.rect[2], self.rect[3])))
            self.last_text = displayed_text

        for text_obj, text_rect in self.text_surfaces:
            surf.blit(text_obj, text_rect)

    def update(self, surf=None, leng=None):
        if self.counter < len(self.text) * 60:
            self.counter += 60
        else:
            self.done = True
