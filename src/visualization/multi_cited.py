import json
import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}\\..\\..\\out"
JSON_DIR = f"{OUT_DIR}\\paired_2023-09-27T00.00.00_2023-10-03T23.59.00_LINKED.json"

LANGS = ["ita", "eng", "fre", "ger"]


def main():
    multi_cited(True)


def multi_cited(by_version: bool = False):
    if by_version:
        data = get_values(JSON_DIR)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        ax = plt.subplot(111)
        for i, version in zip(range(len(data.keys())), data.keys()):
            cited_two = ax.bar(i, data[version]["2"], color=colors[0])
            autolabel(cited_two, ax)
            bottom = data[version]["2"]
            cited_three = ax.bar(i, data[version]["3"], color=colors[1], bottom=bottom)
            autolabel(cited_three, ax, true_h=cited_three[0].get_heigh() + bottom)
            bottom = data[version]["2"] + data[version]["3"]
            cited_four = ax.bar(i, data[version]["4"], color=colors[2], bottom=bottom)
            autolabel(cited_four, ax, true_h=cited_four[0].get_height() + bottom)
            if i == len(data.keys()) - 1:
                ax.legend([cited_two, cited_three, cited_four], ["2 Versions", "3 Versions", "4 Versions"])
        plt.xticks(range(len(data.keys())), list(data.keys()))
        plt.title("Number of news cited by multiple versions for each langauge")
        plt.xlabel("Version")
        plt.ylabel("News Items")
        plt.show()


def get_values(json_dir: str, by_version: bool = False) -> dict:
    with open(json_dir, "r", encoding="utf-8") as f:
        data = json.load(f)
    item_cits = {}





    if by_version:
        citations_n = {version: {"2": 0, "3": 0, "4": 0} for version in LANGS}
        for news_item in item_cits.keys():
            if item_cits[news_item] == 1:
                continue
            else:
                version = news_item.split("/")[-3]
                citations_n[version][str(item_cits[news_item])] += 1
    else:
        citations_n = {"2": 0, "3": 0, "4": 0}
        for news_item in item_cits.keys():
            if item_cits[news_item] == 1:
                continue
            else:
                version = news_item.split("/")[-3]
                citations_n[str(item_cits[news_item])] += 1
    return citations_n


def autolabel(rects, ax, true_h=-1):
    for rect in rects:
        h = rect.get_height()
        if true_h != -1:
            h = true_h
        ax.text(rect.get_x() + rect.get_width() / 2., h, f"{rect.get_height():.2f}",
                ha='center', va='bottom')


if __name__ == "__main__":
    main()
