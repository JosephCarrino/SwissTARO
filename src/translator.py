import os
import json
from argostranslate import translate
from googletrans import Translator
from utils import in_range_epoch, date_to_epoch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# NEWS_DIR = f"{BASE_DIR}/../data"
NEWS_DIR = f"{BASE_DIR}/../../ConcepTitle/fulltext/NER/flow"

# OUT_DIR = f"{BASE_DIR}/../translated_data"
OUT_DIR = f"{BASE_DIR}/../../ConcepTitle/fulltext/translated"

TO_TRANS = ["Spiegel", "BBC", "ABC", "France24", "ilPost", "ANSA_Esteri"]

START_DATE = "2023-03-10 00:00:00"
END_DATE = "2023-03-19 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)

LANGUAGE_FIELD = "language"

# LANG_TO_TRANS = {'fre': 0,
#                  'ger': 1,
#                  'ita': 2}

LANG_TO_TRANS = {'FR': 0,
                 'DE': 1,
                 'IT': 2,
                 'ES': 3}

# TO_GOOGLE_LANG = {'fre': 'fr',
#                   'ger': 'de',
#                   'ita': 'it'}

TO_GOOGLE_LANG = {'FR': 'FR',
                  'DE': 'DE',
                  'IT': 'IT',
                  'ES': 'ES'}

ALREADY_TRANSLATED = {}

def setup_translators():
    translators_to_ret = [{} for _ in range(len(LANG_TO_TRANS.keys()))]
    installed_languages = translate.get_installed_languages()
    for i in range(1, len(translators_to_ret) + 1):
        translators_to_ret[i - 1] = installed_languages[i].get_translation(installed_languages[0])
    return translators_to_ret


translators = setup_translators()

google_translator = Translator()


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


def translate_one_snap(snapshot: list[dict]) -> list[dict]:
    if "en_title" in snapshot[0]:
        return snapshot
    for idx, item in enumerate(snapshot):
        snapshot[idx] = translate_one_item_argos(item)
        # snapshot[idx] = translate_one_item_google(item)
    return snapshot


def translate_one_item_argos(item: dict) -> dict:
    if item[LANGUAGE_FIELD] == "EN":
        item["en_title"] = item["title"]
        item["en_content"] = '\n'.join(item["content"])
        item["en_subtitle"] = item["subtitle"]
    else:
        if item["news_url"] in ALREADY_TRANSLATED.keys():
            item["en_title"] = ALREADY_TRANSLATED[item["news_url"]]["en_title"]
            item["en_content"] = ALREADY_TRANSLATED[item["news_url"]]["en_content"]
            item["en_subtitle"] = ALREADY_TRANSLATED[item["news_url"]]["en_subtitle"]
            return item
        else:
            try:
                item["en_title"] = translators[LANG_TO_TRANS[item[LANGUAGE_FIELD]]].translate(item["title"])
                item["en_content"] = translators[LANG_TO_TRANS[item[LANGUAGE_FIELD]]].translate(item["content"])
            except:
                pass
            try:
                item["en_subtitle"] = translators[LANG_TO_TRANS[item[LANGUAGE_FIELD]]].translate(item["subtitle"])
            except:
                item["en_subtitle"] = ""
            ALREADY_TRANSLATED[item["news_url"]] = {"en_title": item["en_title"], "en_content": item["en_content"],
                                                        "en_subtitle": item["en_subtitle"]}
    return item


def translate_one_item_google(item: dict) -> dict:
    if item[LANGUAGE_FIELD] == "EN":
        item["en_title"] = item["title"]
        item["en_content"] = '\n'.join(item["content"])
        item["en_subtitle"] = item["subtitle"]
    else:
        if item["item_url"] in ALREADY_TRANSLATED.keys():
            item["en_title"] = ALREADY_TRANSLATED[item["item_url"]]["en_title"]
            item["en_content"] = ALREADY_TRANSLATED[item["item_url"]]["en_content"]
            item["en_subtitle"] = ALREADY_TRANSLATED[item["item_url"]]["en_subtitle"]
            return item
        else:
            try:
                item["en_title"] = google_translator.translate(item["title"], src=TO_GOOGLE_LANG[item[LANGUAGE_FIELD]], dest="en")
                item["en_content"] = google_translator.translate(item["content"], src=TO_GOOGLE_LANG[item[LANGUAGE_FIELD]], dest="en")
            except:
                pass
            try:
                item["en_subtitle"] = google_translator.translate(item["subtitle"], src=TO_GOOGLE_LANG[item[LANGUAGE_FIELD]], dest="en")
            except:
                item["en_subtitle"] = ""
            ALREADY_TRANSLATED[item["item_url"]] = {"en_title": item["en_title"], "en_content": item["en_content"],
                                                        "en_subtitle": item["en_subtitle"]}
    return item


def full_pipe_one_snap(snap_dir: str) -> list[dict]:
    snap = get_one_snap(snap_dir)
    return translate_one_snap(snap)


def translate_all():
    for language in os.listdir(NEWS_DIR):
        print(language)
        for outlet in os.listdir(f"{NEWS_DIR}/{language}"):
            print(outlet)
            if outlet not in TO_TRANS:
                continue
            for file in os.listdir(f"{NEWS_DIR}/{language}/{outlet}"):
                if file.endswith(".json"):
                    snap_dir = f"{NEWS_DIR}/{language}/{outlet}/{file}"
                    if in_range_epoch(file, START_EPOCH, END_EPOCH):
                        print(file)
                        if file in os.listdir(f"{OUT_DIR}/{language}/{outlet}"):
                            print("Already Found")
                            continue
                        translated_snap = full_pipe_one_snap(snap_dir)
                        with open(f"{OUT_DIR}/{language}/{outlet}/{file}", "w", encoding="utf-8") as f:
                            json.dump(translated_snap, f, indent=4)
                            f.write("\n")


if __name__ == "__main__":
    main()
