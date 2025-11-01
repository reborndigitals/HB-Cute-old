import os
from typing import List
import yaml

languages = {}
languages_present = {}


def get_string(lang: str):
    # ✅ Safe version — always returns a valid language dict
    if not isinstance(lang, str):
        lang = "en"
    if lang not in languages:
        lang = "en"
    return languages[lang]


# ✅ Load all available language files
base_path = "./strings/langs/"
for filename in os.listdir(base_path):
    # Always ensure English (default) is loaded first
    if "en" not in languages:
        with open(os.path.join(base_path, "en.yml"), encoding="utf8") as f:
            languages["en"] = yaml.safe_load(f)
        languages_present["en"] = languages["en"].get("name", "English")

    # Load other language YAML files
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        if language_name == "en":
            continue

        with open(os.path.join(base_path, filename), encoding="utf8") as f:
            languages[language_name] = yaml.safe_load(f)

        # Fill in any missing keys from English fallback
        for key in languages["en"]:
            if key not in languages[language_name]:
                languages[language_name][key] = languages["en"][key]

        try:
            languages_present[language_name] = languages[language_name]["name"]
        except Exception as e:
            print(f"[ERROR] Problem in language file: {filename} → {e}")
            exit()
