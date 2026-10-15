import os

import pygame


BACKGROUND_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets",
    "images",
    "game_bg.jpg"
)

_background_cache = {}
_background_image = None


def draw_space_background(screen, width, height, overlay_alpha=92):
    """Draw the shared space image with a readable sci-fi color wash."""
    global _background_image

    if _background_image is None:
        _background_image = pygame.image.load(BACKGROUND_PATH).convert()

    cache_key = (width, height)
    if cache_key not in _background_cache:
        image_width, image_height = _background_image.get_size()
        scale = max(width / image_width, height / image_height)
        scaled_size = (
            max(1, int(image_width * scale)),
            max(1, int(image_height * scale))
        )
        scaled = pygame.transform.smoothscale(
            _background_image,
            scaled_size
        )
        crop = pygame.Surface((width, height))
        crop.blit(
            scaled,
            (
                (width - scaled_size[0]) // 2,
                (height - scaled_size[1]) // 2
            )
        )
        _background_cache[cache_key] = crop

    screen.blit(_background_cache[cache_key], (0, 0))

    wash = pygame.Surface((width, height), pygame.SRCALPHA)
    wash.fill((3, 8, 25, overlay_alpha))
    screen.blit(wash, (0, 0))


SPACE_PALETTE = {
    "panel": (10, 22, 48),
    "panel_light": (18, 41, 78),
    "input": (5, 14, 33),
    "input_active": (18, 55, 91),
    "border": (44, 177, 229),
    "border_light": (117, 224, 255),
    "cyan": (82, 231, 255),
    "blue": (104, 135, 255),
    "blue_light": (139, 181, 255),
    "green": (97, 232, 177),
    "yellow": (255, 210, 98),
    "red": (255, 105, 153),
    "white": (235, 249, 255),
    "gray": (167, 202, 222),
    "dark_gray": (91, 128, 157),
}
