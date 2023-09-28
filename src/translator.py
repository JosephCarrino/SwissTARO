import os
import json
from argostranslate import package, translate
from utils import NEWS_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../../data"

OUT_DIR = f"{BASE_DIR}/../../translated_data"

LANG_TO_TRANS = {'fre': 0,
                 'ger': 1,
                 'ita': 2}


def setup_translators():
    translators_to_ret = [{} for _ in range(len(LANG_TO_TRANS.keys()))]
    print(translators_to_ret)
    installed_languages = translate.get_installed_languages()
    for i in range(1, len(translators_to_ret) + 1):
        print(installed_languages)
        translators_to_ret[i-1] = installed_languages[i].get_translation(installed_languages[0])
    return translators_to_ret


translators = setup_translators()


def main():
    translate_all()


def get_one_snap(dir_to_get: str) -> list[dict]:
    """
    Get one snapshot given its path
    :param dir_to_get: directory of snapshots
    :return: one snapshot
    """
    if dir_to_get.endswith(".json"):
        with open(f"{dir_to_get}", "r", encoding="utf-8") as f:
            snapshot = json.load(f)
            return snapshot


def translate_one_snap(snapshot: dict) -> list[dict]:
    for idx, item in enumerate(snapshot):
        snapshot[idx] = translate_one_item(item)
    return snapshot


def translate_one_item(item: dict) -> dict:
    if item["lang"] == "eng":
        item["en_title"] = item["title"]
        item["en_content"] = item["content"]
        item["en_subtitle"] = item["subtitle"]
    else:
        item["en_title"] = translators[LANG_TO_TRANS[item["lang"]]].translate(item["title"])
        item["en_content"] = translators[LANG_TO_TRANS[item["lang"]]].translate(item["content"])
        item["en_subtitle"] = translators[LANG_TO_TRANS[item["lang"]]].translate(item["subtitle"])
    return item


def full_pipe_one_snap(snap_dir: str) -> list[dict]:
    snap = get_one_snap(snap_dir)
    return translate_one_snap(snap)


def translate_all():
    for language in os.listdir(NEWS_DIR):
        for file in os.listdir(f"{NEWS_DIR}/{language}"):
            if file.endswith(".json"):
                snap_dir = f"{NEWS_DIR}/{language}/{file}"
                translated_snap = full_pipe_one_snap(snap_dir)
                with open(f"{OUT_DIR}/{language}/{file}", "w", encoding="utf-8") as f:
                    json.dump(translated_snap, f, indent=4)
                    f.write("\n")
