import json
import os
import matplotlib.pyplot as plt

SEPARATOR = "\\"
# SEPARATOR = "/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}..{SEPARATOR}out{SEPARATOR}cardinalities_stats"
FILE_DIR = f"2023-10-23T23.45.00_2023-10-23T23.59.00_no_carousels.json"
FULL_DIR = f"{OUT_DIR}{SEPARATOR}{FILE_DIR}"
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
CAROUSELS = ""
if "carousels" in FILE_DIR:
    if "no" in FILE_DIR:
        CAROUSELS = " without carousels"
    else:
        CAROUSELS = " only carousels"

# This is for dividing the values by total
RATIO = True

# This is for dividing the values of the couples by the number of the total news of the two versions
COUPLES_TOTAL = False


def main():
    print_cardinalities(ratio=RATIO, couples_total=COUPLES_TOTAL)


def print_cardinalities(ratio: bool, couples_total: bool):
    with open(FULL_DIR, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["by_language_2"] = data["by_language"].copy()
    if ratio:
        total_overall = sum([val for val in data["overall"].values()])
        total_by_lang = {lang: sum([val for val in data["by_language"][lang].values()]) for lang in data["by_language"].keys()}
        total_by_numbers = {"1": 0, "2": 0, "3": 0, "4": 0}
        for lang in data["by_language"].keys():
            for key in data["by_language"][lang].keys():
                total_by_numbers[key] += data["by_language"][lang][key]
        total_by_couples = sum([val for val in data["by_couples"].values()])
        total_by_triples = sum([val for val in data["by_triples"].values()])
        data["overall"] = {key: round(value/total_overall, 2) for key, value in data["overall"].items()}
        for lang in data["by_language"].keys():
            data["by_language"][lang] = {key: round(value/total_by_numbers[key], 2) for key, value in data["by_language"][lang].items()}
            data["by_language_2"][lang] = {key: round(value / total_by_lang[lang], 2) for key, value in
                                         data["by_language_2"][lang].items()}
        data["by_couples"] = {key.upper(): round(value/total_by_couples, 2) for key, value in data["by_couples"].items()}
        data["by_triples"] = {key.upper(): round(value/total_by_triples, 2) for key, value in data["by_triples"].items()}
    if couples_total and ratio:
        raise (Exception("Cannot compute ratio and couples total together"))
    if couples_total:
        totals = compute_totals(data)
        for key, value, total in zip(data["by_couples"].keys(), data["by_couples"].values(), totals):
            data["by_couples"][key] = round(value/total, 2)

    print_overall(data["overall"])
    print_languages(data["by_language"])
    print_languages_2(data["by_language_2"])
    print_overall(data["by_couples"], xlabel="Different couples", title=f"News translated in two different languages divided by total news{CAROUSELS}")
    print_overall(data["by_triples"], xlabel="Different triples", title=f"News translated in three different languages{CAROUSELS}")
    print_languages_stacked(data["by_language_2"])


def print_overall(data: dict, xlabel: str = "Different versions", ylabel: str = "News",
                  title: str = f"Translations of news in different languages{CAROUSELS}"):
    ax = plt.subplot(111)
    bars = ax.bar(data.keys(), data.values())
    ax.bar_label(bars, fontsize=12, weight="bold")
    plt.xlabel(xlabel, fontsize=12, weight="bold")
    plt.ylabel(ylabel, fontsize=12, weight="bold")
    plt.show()

def print_languages(data: dict):
    ax = plt.subplot(111)
    formatted_data = {"1": {}, "2": {}, "3": {}, "4": {}}
    for lang in data.keys():
        formatted_data["1"][lang] = data[lang]["1"]
        formatted_data["2"][lang] = data[lang]["2"]
        formatted_data["3"][lang] = data[lang]["3"]
        formatted_data["4"][lang] = data[lang]["4"]
    w = 0.7
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for i, key in enumerate(formatted_data.keys()):
        j = i+1
        bars1 = ax.bar(j - (1.5 * (w/4)), formatted_data[key]["ENG"], width=w/4, align='center', color=colors[0])
        ax.bar_label(bars1)
        bars2 = ax.bar(j - (0.5 * (w/4)), formatted_data[key]["FRE"], width=w/4, align='center', color=colors[1])
        ax.bar_label(bars2)
        bars3 = ax.bar(j + (0.5 * (w/4)), formatted_data[key]["GER"], width=w/4, align='center', color=colors[2])
        ax.bar_label(bars3)
        bars4 = ax.bar(j + (1.5 * (w/4)), formatted_data[key]["ITA"], width=w/4, align='center', color=colors[3])
        ax.bar_label(bars4)

        if i == len(formatted_data.keys()) - 1:
            ax.legend([bars1, bars2, bars3, bars4], ["ENG", "FRE", "GER", "ITA"], fontsize=12)
    plt.xticks([1, 2, 3, 4], fontsize=12, weight='bold')
    plt.xlabel("Different versions", fontsize=12, weight='bold')
    plt.ylabel("News", fontsize=12, weight='bold')
    plt.show()


def print_languages_2(data: dict):
    ax = plt.subplot(111)
    w = 0.7
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for i, key in enumerate(data.keys()):
        j = i + 1
        bars1 = ax.bar(j - (1.5 * (w / 4)), data[key]["1"], width=w / 4, align='center',
                       color=colors[0])
        ax.bar_label(bars1)
        bars2 = ax.bar(j - (0.5 * (w / 4)), data[key]["2"], width=w / 4, align='center',
                       color=colors[1])
        ax.bar_label(bars2)
        bars3 = ax.bar(j + (0.5 * (w / 4)), data[key]["3"], width=w / 4, align='center',
                       color=colors[2])
        ax.bar_label(bars3)
        bars4 = ax.bar(j + (1.5 * (w / 4)), data[key]["4"], width=w / 4, align='center',
                       color=colors[3])
        ax.bar_label(bars4)

        if i == len(data.keys()) - 1:
            ax.legend([bars1, bars2, bars3, bars4], ["1 version", "2 versions", "3 versions", "4 versions"], fontsize=12)
    plt.xticks(range(1, 5), ["ENG", "FRE", "GER", "ITA"], fontsize=12, weight='bold')
    plt.xlabel("Different versions", fontsize=12, weight='bold')
    plt.ylabel("News", fontsize=12, weight='bold')
    plt.show()


def print_languages_stacked(data: dict):
    ax = plt.subplot(111)
    w = 0.7
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for i, key in enumerate(data.keys()):
        j = i + 1
        bars1 = ax.bar(j - (0.5 * (w / 2)), data[key]["1"], width=w / 4, align='center',
                       color=colors[0])
        autolabel(bars1, ax, true_h = data[key]["1"])
        bars2 = ax.bar(j + (0.5 * (w / 2)), data[key]["2"], width=w / 4, align='center',
                       color=colors[1])
        autolabel(bars2, ax, true_h = data[key]["2"])
        bars3 = ax.bar(j + (0.5 * (w / 2)), data[key]["3"], width=w / 4, align='center',
                       color=colors[2], bottom=bars2[0].get_height())
        autolabel(bars3, ax, true_h=data[key]["3"] +bars2[0].get_height())
        bars4 = ax.bar(j + (0.5 * (w / 2)), data[key]["4"], width=w / 4, align='center',
                       color=colors[3], bottom=bars2[0].get_height() + bars3[0].get_height())
        autolabel(bars4, ax, true_h = data[key]["4"] + bars2[0].get_height() + bars3[0].get_height())

        if i == len(data.keys()) - 1:
            ax.legend([bars1, bars2, bars3, bars4], ["1 version", "2 versions", "3 versions", "4 versions"], fontsize=12)
    plt.xticks(range(1, 5), ["ENG", "FRE", "GER", "ITA"], fontsize=12, weight='bold')
    plt.xlabel("Different versions", fontsize=12, weight='bold')
    plt.ylabel("News", fontsize=12, weight='bold')
    plt.show()

def autolabel(rects, ax, true_h=-1):
    for rect in rects:
        h = rect.get_height()
        if true_h != -1:
            h = true_h
        ax.text(rect.get_x() + rect.get_width() / 2., h, f"{rect.get_height():.2f}",
                ha='center', va='bottom', fontsize=12, weight="bold")


def compute_totals(data: dict) -> list:
    totals = []
    for couple in data["by_couples"].keys():
        splitted = couple.split("-")
        elem_A = splitted[0].upper()
        elem_B = splitted[1].upper()
        total_A = 0
        for key in data["by_language"][elem_A].keys():
            total_A += data["by_language"][elem_A][key]
        total_B = 0
        for key in data["by_language"][elem_B].keys():
            total_B += data["by_language"][elem_B][key]
        totals.append(total_A + total_B)
    return totals


if __name__ == "__main__":
    main()
