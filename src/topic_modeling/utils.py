import json
import os
from datetime import datetime
from enum import Enum


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../../data"
TRANSLATED_NEWS_DIR = f"{BASE_DIR}/../../translated_data"

ORIGINAL_TO_LANG = {"de": "GER", "it": "ITA", "fr": "FRE", "en": "ENG"}


class UseCarousels(Enum):
    YES = 2
    ONLY = 1
    NO = 0


def date_to_epoch(date: str) -> float:
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    epoch = datetime.utcfromtimestamp(0)
    return (date - epoch).total_seconds()


def in_range_epoch(file: str, start_epoch: float, end_epoch: float) -> bool:
    """
    Check if a file is in a given time range
    :param file: file to be checked
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :return: True if the file is in the time range, False otherwise
    """
    file_epoch = int(file.split("E")[1].split(".")[0])
    return start_epoch <= file_epoch <= end_epoch


def get_lang_items(dir_to_check: str, lang: str, start_epoch: float, end_epoch: float, carousels=UseCarousels.YES) \
        -> list[dict]:
    """
    Get all items in a given language section in a given time range
    :param dir_to_check: directory of scraped items
    :param lang: language of items to be gathered
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :param carousels: how to handle carousels
    :return: list of items in lang
    """
    items = []
    urls = []
    for file in os.listdir(f"{dir_to_check}/{lang}"):
        filepath = f"{dir_to_check}/{lang}/{file}"
        if in_range_epoch(file, start_epoch, end_epoch):
            with open(filepath, "r", encoding="utf-8") as f:
                news = json.load(f)
                for new in news:
                    if new["item_url"] not in urls:
                        if carousels == UseCarousels.NO and new["carousel"]:
                            continue
                        if carousels == UseCarousels.ONLY and not new["carousel"]:
                            continue
                        urls.append(new["item_url"])
                        items.append(new)
    return items


def get_dict_items(start_epoch: float, end_epoch: float, dir_to_check: str = NEWS_DIR, carousels=UseCarousels.YES) \
        -> dict:
    """
    Get all news items grouped by language section in a given time range
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :param dir_to_check: where to look for news items
    :param carousels: how to handle carousels
    :return: List of sections with associated items
    """
    items = {}
    for lang in os.listdir(dir_to_check):
        items[lang] = get_lang_items(dir_to_check, lang, start_epoch, end_epoch, carousels = carousels)
    return items


def get_originals_data(start_epoch: float, end_epoch: float, check_dir: str = NEWS_DIR, carousels=UseCarousels.YES,
                       start_date: str = "", end_date: str = "") -> dict:
    """
    Get a dict of items grouped by original news language
    :param start_epoch: the starting time of the time range
    :param end_epoch: the ending time of the time range
    :param check_dir: where to look for news items
    :param carousels: how to handle carousels
    :param start_date: starting date for output title
    :param end_date: ending date for output title
    :return: dict where keys are languages and values are news which are originally written in that language
    """
    items = get_dict_items(start_epoch, end_epoch, check_dir, carousels)
    originals = {key: [] for key in items.keys()}
    lens = {key: len(items[key]) for key in items.keys()}
    lens["total"] = sum([lens[key] for key in lens.keys()])
    for lang in items.keys():
        for item in items[lang]:
            original_lang = item["translations"]["Original"]
            if original_lang == "Unk":
                originals[item["lang"].upper()].append(item)
            elif original_lang in ORIGINAL_TO_LANG.keys():
                originals[ORIGINAL_TO_LANG[original_lang]].append(item)
    originals_lens = {key: len(originals[key]) for key in originals.keys()}

    carousels_string = ""
    if carousels == UseCarousels.ONLY:
        carousels_string = "_carousels"
    elif carousels == UseCarousels.NO:
        carousels_string = "_no_carousels"

    output_path = f"{BASE_DIR}/../../out/originals_data/{start_date}_{end_date}{carousels_string}.json"
    output = {"info": {"total_lens": lens, "originals_lens": originals_lens}, "data": originals}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        f.write("\n")
    return output