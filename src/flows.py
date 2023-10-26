
import json
import os
from utils import NEWS_DIR, UseCarousels
from utils import get_dict_items, date_to_epoch
from utils import get_originals_data
from commonality import one_commons

WORKING_DIR = NEWS_DIR

LANGS = [lang for lang in os.listdir(WORKING_DIR)]

START_DATE = "2023-10-19 00:00:00"
END_DATE = "2023-10-23 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

LANG_FORMATTER = {"Italiano": "ITA",
                  "English": "ENG",
                  "Français": "FRE",
                  "Deutsch": "GER"}

LANGS_TRANSL = ["Italiano", "English", "Français", "Deutsch"]

CAROUSEL = ["_no_carousels", "_carousels", ""]

SEPARATOR = "\\"
# SEPARATOR = "/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}out{SEPARATOR}originals_stats{SEPARATOR}"


def main():
    for carousel in UseCarousels:
        get_flows(carousel)


def get_flows(carousels=UseCarousels.YES) -> dict:
    news_items = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=carousels)
    flows = {key_1: {} for key_1 in news_items.keys()}
    originals = get_originals_data(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=carousels)["data"]
    for starting_lang in flows.keys():
        to_check_items = originals[starting_lang]
        temp_items = news_items.copy()
        del temp_items[starting_lang]
        flows[starting_lang] = one_commons(to_check_items, temp_items)[0]
    outpath_ending = f"{OUT_START_DATE}_{OUT_END_DATE}{CAROUSEL[carousels.value]}.json"
    with open(f"{OUT_DIR}{outpath_ending}", "w", encoding="utf-8") as f:
        json.dump(flows, f, indent=4)
        f.write("\n")
    return flows


if __name__ == "__main__":
    main()
