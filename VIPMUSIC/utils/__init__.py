from .channelplay import *
from .database import *
from .decorators import *
from .extraction import *
from .formatters import *
from .inline import *
from .pastebin import *
from .sys import *

import os
import yaml

languages = {}
languages_present = {}


def get_string(lang: str):
    """Return the string dictionary for a given language code."""
    # Fix: ensure lang exists and default to English
    if lang not in languages:
        lang = "en"
    return languages[lang]


# Load all available language YAML files
for filename in os.listdir("./strings/langs/"):
    if "en" not in languages:
        with open("./strings/langs/en.yml", encoding="utf8") as f:
            languages["en"] = yaml.safe_load(f)
        languages_present["en"] = languages["en"].get("name", "English")

    if filename.endswith(".yml"):
        lang_name = filename[:-4]
        if lang_name == "en":
            continue

        with open(f"./strings/langs/{filename}", encoding="utf8") as f:
            languages[lang_name] = yaml.safe_load(f)

        # Fill missing keys from English defaults
        for key, value in languages["en"].items():
            if key not in languages[lang_name]:
                languages[lang_name][key] = value

        try:
            languages_present[lang_name] = languages[lang_name]["name"]
        except Exception:
            print(f"⚠️ Issue with language file: {filename}")
            exit()
          
