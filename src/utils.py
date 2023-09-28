import os
import json
import spacy
from spacy.tokens import Doc
from typing import Union
from datetime import datetime

SPACY_PROCESSOR = spacy.load("en_core_web_sm")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../../../SwissScrape/scraped_items"

PROCESSED_CONTENT_FIELD = "cont_nlp"
SIMILARITY_THRESHOLD = 0.90


def date_to_epoch(date: str) -> str:
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    epoch = datetime.utcfromtimestamp(0)
    return (date - epoch).total_seconds()

def in_range_epoch(file: str, start_epoch: int, end_epoch: int) -> bool:
    """
    Check if a file is in a given time range
    :param file: file to be checked
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :return: True if the file is in the time range, False otherwise
    """
    file_epoch = int(file.split("E")[1].split(".")[0])
    return start_epoch <= file_epoch <= end_epoch


def get_lang_items(dir_to_check: str, lang: str) -> list[dict]:
    """
    Get all items in a given language section
    :param dir_to_check: directory of scraped items
    :param lang: language of items to be gathered
    :return: list of items in lang
    """
    items = []
    urls = []
    for file in os.listdir(f"{dir_to_check}/{lang}"):
        filepath = f"{dir_to_check}/{lang}/{file}"
        with open(filepath, "r", encoding="utf-8") as f:
            news = json.load(f)
            for new in news:
                if new["item_url"] not in urls:
                    urls.append(new["item_url"])
                    items.append(new)
    return items


def get_lang_items(dir_to_check: str, lang: str, start_epoch: int, end_epoch: int) -> list[dict]:
    """
    Get all items in a given language section in a given time range
    :param dir_to_check: directory of scraped items
    :param lang: language of items to be gathered
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :return: list of items in lang
    """
    items = []
    urls = []
    for file in os.listdir(f"{dir_to_check}/{lang}"):
        filepath = f"{dir_to_check}/{lang}/{file}"
        with open(filepath, "r", encoding="utf-8") as f:
            news = json.load(f)
            for new in news:
                if new["item_url"] not in urls:
                    if in_range_epoch(file, start_epoch, end_epoch):
                        urls.append(new["item_url"])
                        items.append(new)
    return items


def get_all_items(dir_to_check: str = NEWS_DIR) -> list[dict]:
    """
    Get all news items from a directory
    :param dir_to_check:  where to look for news items
    :return: list of news items
    """
    items = []
    for lang in os.listdir(dir_to_check):
        lang_items = get_lang_items(dir_to_check, lang)
        for item in lang_items:
            items.append(item)
    return items


def get_dict_items(dir_to_check: str = NEWS_DIR) -> dict:
    """
    Get all news items grouped by language section
    :param dir_to_check: where to look for news items
    :return: List of sections with associated items
    """
    items = {}
    for lang in os.listdir(dir_to_check):
        items[lang] = get_lang_items(dir_to_check, lang)
    return items


def get_dict_items(start_epoch: int, end_epoch: int, dir_to_check: str = NEWS_DIR) -> dict:
    """
    Get all news items grouped by language section in a given time range
    :param start_epoch: start of the time range
    :param end_epoch: end of the time range
    :param dir_to_check: where to look for news items
    :return: List of sections with associated items
    """
    items = {}
    for lang in os.listdir(dir_to_check):
        items[lang] = get_lang_items(dir_to_check, lang, start_epoch, end_epoch)
    return items


def get_item_translations(item: dict) -> list[dict]:
    """
    Get all translations of a news item
    """
    translations = []
    for translation in item["translations"].values():
        translations.append(translation)
    return translations


def get_snapshost_translation(snapshot: list[dict]) -> list[dict]:
    """
    Get all translations of a snapshot
    """
    translations = []
    for article in snapshot:
        for translation in get_item_translations(article):
            translations.append(translation)
    return translations


def has_equivalent_in_snapshot_linked(main_news: dict, news_snapshot: list[dict], simil_cache: dict = None) -> bool:
    """
    Check if a news item has an equivalent in a snapshot using translations links of Swissinfo
    """
    translations = get_snapshost_translation(news_snapshot)
    for translation in translations:
        if translation["item_url"] == main_news["item_url"]:
            return True
    return False


def process_content(to_process: list[str]) -> Union[Doc, Doc]:
    """
    Process the content of a news item with SpaCy
    """
    plain_content = "\n".join(to_process)
    return SPACY_PROCESSOR(plain_content)


def are_similar(news_A: dict, news_B: dict) -> bool:
    """
    Compute similarity rate between two items using Spacy
    :param news_A
    :param news_B
    :return: True if the similarity is above between threshold, False otherwise
    """
    similarity = news_A[PROCESSED_CONTENT_FIELD].similarity(news_B[PROCESSED_CONTENT_FIELD])
    return similarity > SIMILARITY_THRESHOLD


def has_equivalent_in_snapshot_spacy(main_news: dict, news_snapshot: list[dict], simil_cache: dict = None) -> bool:
    """
    Check if a news item has an equivalent in a snapshot by using SpaCy similarity
    :param main_news: items to be checked
    :param news_snapshot: snapshot to check in
    :param simil_cache: a dictionary that caches the result of similarity computing between pairs of items
    :return: True if there is an equivalent article to main_news in news_snapshot, False otherwise
    """
    if simil_cache is None:
        simil_cache = {}
    if PROCESSED_CONTENT_FIELD not in main_news:
        main_news[PROCESSED_CONTENT_FIELD] = process_content(main_news["content"])
    for news_item in news_snapshot:
        title_1 = max(main_news["title"], news_item["title"])
        title_2 = min(main_news["title"], news_item["title"])
        idx = f"{title_1}_{title_2}"

        if idx in simil_cache and simil_cache[idx]:
            return True

        if PROCESSED_CONTENT_FIELD not in news_item:
            news_item[PROCESSED_CONTENT_FIELD] = process_content(news_item["content"])

        if are_similar(main_news, news_item):
            simil_cache[idx] = True
            return True

        simil_cache[idx] = False
    return False
