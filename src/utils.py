import os
import json
import spacy
from spacy.tokens import Doc
from typing import Union
from datetime import datetime

SPACY_PROCESSOR = spacy.load("en_core_web_md")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../data"
TRANSLATED_NEWS_DIR = f"{BASE_DIR}/../translated_data"

PROCESSED_CONTENT_FIELD = "cont_nlp"
SIMILARITY_THRESHOLD = 0.9997


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


def get_lang_items(dir_to_check: str, lang: str, start_epoch: float, end_epoch: float) -> list[dict]:
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
        if in_range_epoch(file, start_epoch, end_epoch):
            with open(filepath, "r", encoding="utf-8") as f:
                news = json.load(f)
                for new in news:
                    if new["item_url"] not in urls:
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


def get_dict_items(start_epoch: float, end_epoch: float, dir_to_check: str = NEWS_DIR) -> dict:
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


def get_snapshot_translation(snapshot: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Get all translations of a snapshot
    """
    translations = []
    true_urls = []
    for article in snapshot:
        translations.append(article["item_url"])
        true_urls.append(article["item_url"])
        for translation in get_item_translations(article):
            translations.append(translation)
            true_urls.append(article["item_url"])
    return translations, true_urls


def get_all_translations(news_items: dict) -> dict:
    CONSIDERED_LANGUAGES = ["Italiano", "Français", "Deutsch", "English"]
    translations = {lang: {} for lang in news_items.keys()}
    for lang in news_items.keys():
        for item in news_items[lang]:
            for trans_lang in item["translations"].keys():
                if trans_lang in CONSIDERED_LANGUAGES:
                    translations[lang][trans_lang] = item["translations"][trans_lang]
    return translations




def has_equivalent_in_snapshot_linked(main_news: dict, news_snapshot: list[dict], simil_cache: dict = None) \
        -> Union[bool, str]:
    """
    Check if a news item has an equivalent in a snapshot using translations links of Swissinfo
    """
    translations, true_urls = get_snapshot_translation(news_snapshot)
    for translation, true_url in zip(translations, true_urls):
        if translation == main_news["item_url"]:
            return True, true_url
    return False, ""


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


def has_equivalent_in_snapshot_spacy(main_news: dict, news_snapshot: list[dict], simil_cache: dict = None) \
        -> Union[bool, str]:
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
        try:
            main_news[PROCESSED_CONTENT_FIELD] = process_content(main_news["en_content"])
        except:
            return False, ""
    for news_item in news_snapshot:
        if main_news["title"] is not None and news_item["title"] is not None:
            title_1 = max(main_news["title"], news_item["title"])
            title_2 = min(main_news["title"], news_item["title"])
            idx = f"{title_1}_{title_2}"

            if idx in simil_cache and simil_cache[idx] is True:
                return True, news_item["item_url"]

            if PROCESSED_CONTENT_FIELD not in news_item:
                news_item[PROCESSED_CONTENT_FIELD] = process_content(news_item["en_content"])

            if are_similar(main_news, news_item):
                simil_cache[idx] = True
                return True, news_item["item_url"]

            simil_cache[idx] = False
    return False, ""
