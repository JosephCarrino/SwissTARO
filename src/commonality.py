import os
import json
from utils import NEWS_DIR, TRANSLATED_NEWS_DIR
from utils import get_dict_items, get_all_translations, date_to_epoch
from utils import has_equivalent_in_snapshot_linked, has_equivalent_in_snapshot_spacy
from enum import Enum


class SnapshotEquivalents(Enum):
    LINKED = has_equivalent_in_snapshot_linked
    SPACY = has_equivalent_in_snapshot_spacy


# WORKING_DIR = TRANSLATED_NEWS_DIR
WORKING_DIR = NEWS_DIR


LANGS = [lang for lang in os.listdir(WORKING_DIR)]

START_DATE = "2023-09-27 00:00:00"
END_DATE = "2023-10-03 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

LANG_FORMATTER = {"Italiano": "ITA",
                  "English": "ENG",
                  "Français": "FRE",
                  "Deutsch": "GER"}


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
        unpaired = get_unpaired(news_items, paired)
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
    with open(f"../out/commons_{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(commons, f, indent=4)
        f.write("\n")
    with open(f"../out/paired_{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(paired, f, indent=4)
        f.write("\n")

    return commons


def get_unpaired(news_items, paired):
    translations_list = get_all_translations(news_items)
    unpaired = {lang: {} for lang in news_items.keys()}
    for lang in unpaired.keys():
        unpaired[lang] = {lang: [] for lang in news_items.keys()}
    for lang in translations_list.keys():
        for transl_lang in translations_list[lang].keys():
            found = False
            for pair in paired:
                if pair[0] != pair[1] and translations_list[lang][transl_lang] in pair:
                    found = True
                    break
            if not found:
                unpaired[lang][LANG_FORMATTER[transl_lang]].append(translations_list[lang][transl_lang])
    return unpaired


def main():
    run_one_commons()


if __name__ == '__main__':
    main()
