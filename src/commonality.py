import os
import json
from utils import NEWS_DIR
from utils import get_dict_items, date_to_epoch
from utils import has_equivalent_in_snapshot_linked, has_equivalent_in_snapshot_spacy
from enum import Enum


class SnapshotEquivalents(Enum):
    LINKED = has_equivalent_in_snapshot_linked
    SPACY = has_equivalent_in_snapshot_spacy


LANGS = [lang for lang in os.listdir(NEWS_DIR)]

START_DATE = "2023-09-27 15:00:00"
END_DATE = "2023-09-27 22:01:00"
START_EPOCH = date_to_epoch(START_DATE)
END_EPOCH = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':','.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':','.')


def one_commons(main_items: list[dict], other_items: dict,
                simil_snapshot_fun: SnapshotEquivalents = SnapshotEquivalents.LINKED) -> dict:
    """
    Given a set of items, compute how much news the other sections has in common with it
    :param main_items: list of items "pivot"
    :param other_items: list of sections to check commonality of
    :param simil_snapshot_fun: function to use for check equivalence in the set
    :return: number of news in common between each version and the main_items
    """

    # Examples
    # main_items: [{item_1}, {item_2}, ..., {item_n}]
    # other_items: {"FRE": [{item_1},...,{item_m}], "ENG": [{item_1}, ..., item_z}], ...}

    simil_cache = {}
    commons = {lang: 0 for lang in other_items.keys()}

    for lang, items_set in other_items.items():
        for to_check in main_items:
            if simil_snapshot_fun(to_check, items_set, simil_cache):
                commons[lang] += 1
    return commons


def run_one_commons(simil_snapshot_fun: SnapshotEquivalents = SnapshotEquivalents.LINKED) -> dict[dict]:
    """
    Run one_commons for each language section
    :param simil_snapshot_fun: function to use for check equivalence in the set
    :return: a dictionary for each section which states the items in common with each of them
    """

    # Comment for using the links methods
    simil_snapshot_fun = SnapshotEquivalents.LINKED

    news_items = get_dict_items(START_EPOCH, END_EPOCH, NEWS_DIR)
    commons = {lang: {} for lang in news_items.keys()}
    for lang in commons.keys():
        commons[lang] = one_commons(news_items[lang], news_items, simil_snapshot_fun=simil_snapshot_fun)
    print(commons)
    with open(f"../out/commons_{OUT_START_DATE}_{OUT_END_DATE}_LINKED.json", "w", encoding="utf-8") as f:
        json.dump(commons, f, indent=4)
        f.write("\n")
    return commons


def main():
    run_one_commons()


if __name__ == '__main__':
    main()