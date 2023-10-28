import matplotlib.pyplot as plt
import os
import json

SEPARATOR = "\\"
# SEPARATOR = "/"

START_DATE = "2023-10-23 23:45:00"
END_DATE = "2023-10-23 23:59:00"
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR_1 = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}..{SEPARATOR}out{SEPARATOR}originals_stats{SEPARATOR}"
OUT_DIR_2 = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}..{SEPARATOR}out{SEPARATOR}originals_data{SEPARATOR}"
OUT_PATH = f"{OUT_START_DATE}_{OUT_END_DATE}"

CAROUSELS = ["_no_carousels", "_carousels", ""]
CAROUSELS_STRING = [" excluding carousels", " only carousels", ""]

LANG_STRING = {"ITA": "Italian",
               "ENG": "English",
               "FRE": "French",
               "GER": "German"}


def main():
    for carousel, carousel_string in zip(CAROUSELS, CAROUSELS_STRING):
        plot_pies_1(f"{OUT_DIR_1}{OUT_PATH}{carousel}.json", carousel_string)
        plot_pies_2(f"{OUT_DIR_2}{OUT_PATH}{carousel}.json", carousel_string)


def plot_pies_1(path: str, carousel: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fig, axs = plt.subplots(2, 2)
    i = 0
    j = 0
    for starting_lang in data.keys():
        labels = list(data[starting_lang].keys())
        values = list(data[starting_lang].values())
        axs[i][j].pie(values, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
        axs[i][j].set_title(f"From {LANG_STRING[starting_lang]}")
        j += 1
        if j == 2:
            j = 0
            i += 1
    fig.suptitle(f"Versions translations{carousel}", fontsize=16)
    plt.show()


def plot_pies_2(path: str, carousel: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    values = data["info"]["originals_lens"].values()
    labels = data["info"]["originals_lens"].keys()
    plt.pie(values, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
    plt.title(f"Originals edition{carousel}")
    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    main()
