import os
import json
import itertools
from utils import NEWS_DIR, TRANSLATED_NEWS_DIR
from utils import get_dict_items, get_all_translations, date_to_epoch
from utils import has_equivalent_in_snapshot_linked, has_equivalent_in_snapshot_spacy
from enum import Enum
from typing import Union


class SnapshotEquivalents(Enum):
    LINKED = has_equivalent_in_snapshot_linked
    SPACY = has_equivalent_in_snapshot_spacy


# WORKING_DIR = TRANSLATED_NEWS_DIR
WORKING_DIR = NEWS_DIR

LANGS = [lang for lang in os.listdir(WORKING_DIR)]

START_DATE = "2023-09-27 00:01:00"
END_DATE = "2023-10-03 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

LANG_FORMATTER = {"Italiano": "ITA",
                  "English": "ENG",
                  "Français": "FRE",
                  "Deutsch": "GER"}

LANGS_TRANSL = ["Italiano", "English", "Français", "Deutsch"]


def one_commons(main_items: list[dict], other_items: dict,
                simil_snapshot_fun: SnapshotEquivalents = SnapshotEquivalents.LINKED) -> tuple[
                dict, list[tuple]]:
    """
    Given a set of items, compute how much news the other sections has in common with it
    :param main_items: list of items "pivot"
    :param other_items: list of sections to check commonality of
    :param simil_snapshot_fun: function to use for check equivalence in the set
    :return: number of news in common between each version and the main_items and list of paired urls
    """

    # Examples
    # main_items: [{item_1}, {item_2}, ..., {item_n}]
    # other_items: {"FRE": [{item_1},...,{item_m}], "ENG": [{item_1}, ..., item_z}], ...}

    simil_cache = {}
    commons = {lang: 0 for lang in other_items.keys()}
    paired = []

    for lang, items_set in other_items.items():
        for to_check in main_items:
            found, pair = simil_snapshot_fun(to_check, items_set, simil_cache)
            if found:
                commons[lang] += 1
                paired.append((to_check["item_url"], pair))
    return commons, paired


def run_one_commons(simil_snapshot_fun: SnapshotEquivalents = SnapshotEquivalents.LINKED,
                    find_unpaired: bool = True) -> dict[dict]:
    """
    Run one_commons for each language section
    :param find_unpaired: boolean for computing also the list of the not paired news translations
    :param simil_snapshot_fun: function to use for check equivalence in the set
    :return: a dictionary for each section which states the items in common with each of them
    """

    # Comment for using the links methods
    simil_snapshot_fun = SnapshotEquivalents.LINKED

    outpath_ending = f"{OUT_START_DATE}_{OUT_END_DATE}_LINKED.json"

    news_items = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR)
    commons = {lang: {} for lang in news_items.keys()}
    paired = []

    # For each language section, compute the commons in other sections
    for lang in commons.keys():
        commons[lang], pairs = one_commons(news_items[lang], news_items, simil_snapshot_fun=simil_snapshot_fun)
        for pair in pairs:
            paired.append(pair)

    # This is for outputting the translations references not found in the homepages of the related Swissinfo version
    if find_unpaired:
        unpaired = get_unpaired(news_items)
        with open(f"../out/unpaired_{outpath_ending}", "w", encoding="utf-8") as f:
            json.dump(unpaired, f, indent=4)
            f.write("\n")

    commons["info"] = {"start_date": START_DATE, "end_date": END_DATE, "len": {}}
    # Adding Meta-Infos
    for lang in news_items.keys():
        infos = commons["info"]
        infos["len"][lang] = len(news_items[lang])

    print(commons)

    # Outputting to json
    with open(f"../out/commonality_stats/{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(commons, f, indent=4)
        f.write("\n")
    with open(f"../out/paired_items/{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(paired, f, indent=4)
        f.write("\n")

    return commons


def get_unpaired(news_items: dict) -> dict[dict[str]]:
    lang_urls = {lang: [item["item_url"] for item in news_items[lang]] for lang in news_items.keys()}
    unpaired = {lang_1: {lang_2: [] for lang_2 in news_items.keys()} for lang_1 in news_items.keys()}
    for lang in news_items.keys():
        for elem in news_items[lang]:
            for transl_lang, transl_url in elem["translations"].items():
                if transl_lang in LANGS_TRANSL:
                    if transl_url not in lang_urls[LANG_FORMATTER[transl_lang]]:
                        unpaired[lang][LANG_FORMATTER[transl_lang]].append(transl_url)
    unpaired["info"] = {"len": {lang: len(lang_urls[lang]) for lang in news_items.keys()},
                        "unpaired_len": {lang_1: {lang_2: len(unpaired[lang_1][lang_2])
                                                  for lang_2 in news_items.keys()}
                                         for lang_1 in news_items.keys()}}
    for lang_1 in news_items.keys():
        unpaired["info"]["unpaired_len"][lang_1]["total"] = 0
        for lang_2 in news_items.keys():
            unpaired["info"]["unpaired_len"][lang_1]["total"] += len(unpaired[lang_1][lang_2])

    outpath_ending = f"{OUT_START_DATE}_{OUT_END_DATE}.json"
    with open(f"../out/unpaired_items/{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(unpaired, f, indent=4)
        f.write("\n")
    return unpaired


def get_url_numbers(url: str) -> str:
    return url.split("/")[-1]


def get_id(news_item: dict) -> frozenset:
    article_id = news_item["lang"] + get_url_numbers(news_item["item_url"])
    translations_id = []
    for lang, url in news_item["translations"].items():
        if lang in LANGS_TRANSL:
            translations_id.append(LANG_FORMATTER[lang].lower() + get_url_numbers(url))
    return frozenset([article_id] + translations_id)


def get_cardinalities(news_items: list[dict], to_out: bool = False) -> dict[frozenset, list[dict]]:
    unique_articles = {}
    for news_item in news_items:
        article_id = get_id(news_item)
        found_ids = unique_articles.keys()
        is_found = False
        for found_id in found_ids:
            intersection = article_id.intersection(found_id)
            if intersection == found_id or intersection == article_id:
                is_found = True
                article_id = found_id
                break
        if not is_found:
            unique_articles[article_id] = []
        unique_articles[article_id].append(news_item)
    if to_out:
        output_unique_articles = {}
        for article_id, articles in unique_articles.items():
            output_unique_articles[str(sorted(article_id))] = articles
        with open(f"../out/ids_with_cardinalities/{OUT_START_DATE}_{OUT_END_DATE}.json", "w", encoding="utf-8") as f:
            json.dump(output_unique_articles, f, indent=4)
            f.write("\n")
    return unique_articles


def get_one_cardinality(article: dict, unique_articles: dict[frozenset, list[dict]]) -> int:
    for article_id in unique_articles.keys():
        intersection = get_id(article).intersection(article_id)
        if intersection == article_id or intersection == get_id(article):
            return len(unique_articles[article_id])


def get_cardinalities_stat(by_couples: bool = True, by_triples: bool = True) -> dict[str, dict]:
    """
    Given a range of time, get the cardinalities of the set of news translated respectively in
    two, three or four different languages
    :param by_couples: boolean for computing the cardinalities of the set of news translated in two different languages
    :param by_triples: boolean for computing the cardinalities of the set of news translated in three different languages
    :return: A dictionary with one key for each possible number of citations and its cardinality and a dictionary
    with the same sets but grouped by languages
    """
    news_items = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR)
    listed_items = []
    for lang in news_items.keys():
        for article in news_items[lang]:
            listed_items.append(article)
    unique_articles = get_cardinalities(listed_items, False)

    overall_cardinalities = {"1": 0, "2": 0, "3": 0, "4": 0}
    language_cardinalities = {lang: {"1": 0, "2": 0, "3": 0, "4": 0} for lang in news_items.keys()}

    for lang in news_items.keys():
        for news_item in news_items[lang]:
            language_cardinalities[lang][str(get_one_cardinality(news_item, unique_articles))] += 1
    for unique_article in unique_articles.keys():
        overall_cardinalities[str(len(unique_articles[unique_article]))] += 1

    to_print = {"overall": overall_cardinalities, "by_language": language_cardinalities}

    if by_couples:
        langs = list(LANG_FORMATTER.values())
        langs = [lang.lower() for lang in langs]
        couples = list(itertools.combinations(langs, 2))
        couples_cardinalities = {couple: 0 for couple in couples}

        for couple in couples:
            for unique_id, articles in unique_articles.items():
                if len(articles) == 2:
                    true_langs = [article["lang"] for article in articles]
                    if couple[0] in true_langs and couple[1] in true_langs:
                        couples_cardinalities[couple] += 1

        out_couples = {'-'.join(couple): cardinality for couple, cardinality in couples_cardinalities.items()}
        to_print["by_couples"] = out_couples

    if by_triples:
        langs = list(LANG_FORMATTER.values())
        langs = [lang.lower() for lang in langs]
        triples = list(itertools.combinations(langs, 3))
        triples_cardinalities = {triple: 0 for triple in triples}

        for triple in triples:
            for unique_id, articles in unique_articles.items():
                if len(articles) == 3:
                    true_langs = [article["lang"] for article in articles]
                    if triple[0] in true_langs and triple[1] in true_langs and triple[2] in true_langs:
                        triples_cardinalities[triple] += 1

        out_triples = {'-'.join(triple): cardinality for triple, cardinality in triples_cardinalities.items()}
        to_print["by_triples"] = out_triples

    with open(f"../out/cardinalities_stats/{OUT_START_DATE}_{OUT_END_DATE}.json", "w", encoding="utf-8") as f:
        json.dump(to_print, f, indent=4)
        f.write("\n")
    return to_print


def main():
    # run_one_commons()
    # get_versions_cardinalities()
    # get_unpaired(get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR))
    get_cardinalities_stat()


if __name__ == '__main__':
    main()
