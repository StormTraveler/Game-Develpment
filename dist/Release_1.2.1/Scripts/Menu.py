from Scripts.UI import Button, Slider
import pygame
import moderngl


def get_buttons(game, state):
    buttons = []
    sliders = []
    if state == 'Main Menu':
            buttons.append(Button(game, (100, 100, 200, 50), text="Start", type="start", imgs="MenuButton"))
            buttons.append(Button(game, (100, 200, 200, 50), text="Options", type="options", imgs="MenuButton"))
            buttons.append(Button(game, (100, 300, 200, 50), text="Quit", type="quit", imgs="MenuButton"))
            print("Menu Loaded")
            return buttons

    elif state == 'Pause':
            buttons.append(Button(game, (100, 100, 200, 50), "Resume", type="resume", imgs='MenuButton'))
            buttons.append(Button(game, (100, 200, 200, 50), "Restart", type="restart", imgs='MenuButton'))
            buttons.append(Button(game, (100, 300, 200, 50), "Options", type="options", imgs='MenuButton'))
            buttons.append(Button(game, (100, 400, 200, 50), "Main Menu", type="menu", imgs='MenuButton'))
            buttons.append(Button(game, (100, 500, 200, 50), "Quit", type="quit", imgs='MenuButton'))
            return buttons

    elif state == 'Options':
            buttons.append(Button(game, (100, 100, 200, 50), "Keybinds", type="keybinds", imgs='MenuButton'))
            buttons.append(Button(game, (100, 200, 200, 50), "Audio", type="audio", imgs='MenuButton'))
            buttons.append(Button(game, (100, 300, 200, 50), "Video", type="video", imgs='MenuButton'))
            buttons.append(Button(game, (100, 400, 200, 50), "Back", type="back", imgs='MenuButton'))
            return buttons

    elif state == 'Audio':
            buttons.append(Button(game, (100, 200, 200, 50), "Music Volume", type="music_volume", imgs='MenuButton'))
            buttons.append(Button(game, (100, 300, 200, 50), "SFX Volume", type="sfx_volume", imgs='MenuButton'))
            buttons.append(Button(game, (100, 400, 200, 50), "Back", type="back", imgs='MenuButton'))
            return buttons

    elif state == 'Keybinds':
            buttons_per_screen = game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x, iteration = 100, 0

            for key in game.keybinds.keys():
                buttons.append(Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), key,
                                      type="keybind", imgs='MenuButton'))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons
            return buttons

    elif state == 'Video':
            buttons_per_screen = game.screen_size[1] - 100
            max_buttons = buttons_per_screen // 100
            x = 100
            iteration = 0

            for resolution in game.resolutions:
                buttons.append(
                    Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), resolution,
                           type="video", imgs='MenuButton'))
                x += 250 if (iteration + 1) % max_buttons == 0 else 0
                iteration = (iteration + 1) % max_buttons

            buttons.append(
                Button(game, (x, (100 + (100 * iteration)) % buttons_per_screen, 200, 50), "Back", type="back",
                       imgs='MenuButton'))
            return buttons
    return None


def get_sliders(game, state):
    sliders = []
    if state == 'Main Menu':
        print("Menu Loaded")
        return sliders

    elif state == 'Pause':
        return sliders

    elif state == 'Options':
        return sliders

    elif state == 'Audio':
        sliders.append(
            Slider(game, [100, 100, 200, 50], 0, 2, game.master_volume, type="master_volume", text="Master Volume"))
        sliders.append(
            Slider(game, [100, 150, 200, 50], 0, 2, game.music_volume, type="music_volume", text="Music Volume"))
        sliders.append(Slider(game, [100, 200, 200, 50], 0, 2, game.sfx_volume, type="sfx_volume", text="SFX Volume"))
        return sliders

    elif state == 'Keybinds':
        return sliders

    elif state == 'Video':
        return sliders
    return None
