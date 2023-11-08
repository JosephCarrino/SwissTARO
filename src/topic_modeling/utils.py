import json
import os
from datetime import datetime
from enum import Enum


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../../data"
TRANSLATED_NEWS_DIR = f"{BASE_DIR}/../../translated_data"


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