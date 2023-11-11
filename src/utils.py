import os
import json
import spacy
from spacy.tokens import Doc
from typing import Union
from datetime import datetime
from enum import Enum

# SPACY_PROCESSOR = spacy.load("en_core_web_md")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = f"{BASE_DIR}/../data"
TRANSLATED_NEWS_DIR = f"{BASE_DIR}/../translated_data"

PROCESSED_CONTENT_FIELD = "cont_nlp"
SIMILARITY_THRESHOLD = 0.9997

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


def get_lang_items(dir_to_check: str, lang: str, carousels=UseCarousels.YES) -> list[dict]:
    """
    Get all items in a given language section
    :param dir_to_check: directory of scraped items
    :param lang: language of items to be gathered
    :param carousels: how to handle carousels
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
                    if carousels == UseCarousels.NO and new["carousel"]:
                        continue
                    if carousels == UseCarousels.ONLY and not new["carousel"]:
                        continue
                    urls.append(new["item_url"])
                    items.append(new)
    return items


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


def get_dict_items(dir_to_check: str = NEWS_DIR, carousels=2) -> dict:
    """
    Get all news items grouped by language section
    :param dir_to_check: where to look for news items
    :param carousels: how to handle carousels
    :return: List of sections with associated items
    """
    items = {}
    for lang in os.listdir(dir_to_check):
        items[lang] = get_lang_items(dir_to_check, lang, carousels = carousels)
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
        -> tuple[bool, str]:
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
        -> tuple[bool, str]:
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

    output_path = f"{BASE_DIR}/../out/originals_data/{start_date}_{end_date}{carousels_string}.json"
    output = {"info": {"total_lens": lens, "originals_lens": originals_lens}, "data": originals}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
        f.write("\n")
    return output
