import pygame

from db import initialize_database
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.menu_screen import MenuScreen
from screens.profile import ProfileScreen
from screens.leaderboard import LeaderboardScreen
from managers.game_manager import GameManager
from settings_manager import load_settings, save_settings


pygame.init()

MIN_WIDTH = 800
MIN_HEIGHT = 600
windowed_size = (1100, 700)
fullscreen = bool(load_settings()["fullscreen"])

if fullscreen:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

pygame.display.set_caption(
    "SIBLA JERICHO F."
)

clock = pygame.time.Clock()

initialize_database()

login_screen = LoginScreen(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

register_screen = RegisterScreen(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

current_screen = "login"

player = None

menu_screen = None
profile_screen = None
leaderboard_screen = None
game = None


def rebuild_active_screen():
    global login_screen
    global register_screen
    global menu_screen
    global profile_screen
    global leaderboard_screen
    global game

    if current_screen == "login":
        old_screen = login_screen
        login_screen = LoginScreen(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
        login_screen.username = old_screen.username
        login_screen.password = old_screen.password
        login_screen.active_field = old_screen.active_field
        login_screen.show_password = old_screen.show_password

    elif current_screen == "register":
        old_screen = register_screen
        register_screen = RegisterScreen(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
        register_screen.username = old_screen.username
        register_screen.password = old_screen.password
        register_screen.confirm_password = old_screen.confirm_password
        register_screen.active_field = old_screen.active_field
        register_screen.show_password = old_screen.show_password
        register_screen.show_confirm_password = (
            old_screen.show_confirm_password
        )

    elif current_screen == "menu":
        menu_screen = MenuScreen(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            player
        )

    elif current_screen == "profile":
        profile_screen = ProfileScreen(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            player
        )

    elif current_screen == "leaderboard":
        leaderboard_screen = LeaderboardScreen(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

    elif current_screen == "game":
        game.update_viewport(
            screen,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )


def resize_window(size):
    global screen
    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    global windowed_size

    width = max(MIN_WIDTH, size[0])
    height = max(MIN_HEIGHT, size[1])
    windowed_size = (width, height)

    screen = pygame.display.set_mode(
        windowed_size,
        pygame.RESIZABLE
    )
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    rebuild_active_screen()


def toggle_fullscreen():
    global screen
    global fullscreen
    global SCREEN_WIDTH
    global SCREEN_HEIGHT

    fullscreen = not fullscreen
    settings = load_settings()
    settings["fullscreen"] = fullscreen
    save_settings(settings)

    if fullscreen:
        screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN
        )
    else:
        screen = pygame.display.set_mode(
            windowed_size,
            pygame.RESIZABLE
        )

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    rebuild_active_screen()


def sync_settings_display():
    if load_settings()["fullscreen"] != fullscreen:
        toggle_fullscreen()


running = True

while running:

    events = pygame.event.get()

    for event in events:

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            toggle_fullscreen()

        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            resize_window(event.size)

    if not running:
        break

    if current_screen == "login":

        for event in events:

            result = login_screen.handle_event(event)

            if result == "register":

                register_screen = RegisterScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )

                current_screen = "register"
                break

            elif isinstance(result, dict):

                player = result

                pygame.display.set_caption(
                    f"ORBITAL ARCADE — {player['player_name']}"
                )

                menu_screen = MenuScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    player
                )

                current_screen = "menu"
                break

        login_screen.draw()

    elif current_screen == "register":

        for event in events:

            result = register_screen.handle_event(event)

            if result == "login":

                login_screen = LoginScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )

                current_screen = "login"
                break

        register_screen.draw()

    elif current_screen == "menu":

        for event in events:

            result = menu_screen.handle_event(event)

            if result == "play":

                game = GameManager(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    player["id"],
                    player["player_name"]
                )

                current_screen = "game"
                break

            elif result == "profile":

                profile_screen = ProfileScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    player
                )

                current_screen = "profile"
                break

            elif result == "leaderboard":

                leaderboard_screen = LeaderboardScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )

                current_screen = "leaderboard"
                break

            elif result == "logout":

                player = None
                pygame.display.set_caption("ORBITAL ARCADE")
                menu_screen = None
                profile_screen = None
                leaderboard_screen = None
                game = None

                login_screen = LoginScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )

                current_screen = "login"
                break

        if current_screen == "menu":
            menu_screen.draw()

    elif current_screen == "profile":

        for event in events:

            result = profile_screen.handle_event(event)

            if result == "menu":

                menu_screen = MenuScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    player
                )

                current_screen = "menu"
                break

        if current_screen == "profile":
            profile_screen.draw()

    elif current_screen == "leaderboard":

        for event in events:

            result = leaderboard_screen.handle_event(event)

            if result == "menu":

                menu_screen = MenuScreen(
                    screen,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                    player
                )

                current_screen = "menu"
                break

        if current_screen == "leaderboard":
            leaderboard_screen.draw()

    elif current_screen == "game":

        result = game.update(events)

        if result == "menu":

            menu_screen = MenuScreen(
                screen,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                player
            )

            current_screen = "menu"

        elif result == "quit":

            running = False

    sync_settings_display()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
