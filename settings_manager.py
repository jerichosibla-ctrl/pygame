import json
import os


SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "settings.json"
)

DEFAULT_SETTINGS = {
    "sound_volume": 0.8,
    "music_volume": 0.6,
    "mobile_controls": False,
    "fullscreen": False,
    "difficulty": "normal"
}


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        settings = {}

    values = DEFAULT_SETTINGS.copy()
    values.update(settings)
    return values


def save_settings(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=4)
