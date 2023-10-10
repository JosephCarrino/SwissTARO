import json
import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}\\..\\..\\out\\cardinalities_stats"
FILE_DIR = f"2023-09-27T00.01.00_2023-10-03T23.59.00.json"
FULL_DIR = f"{OUT_DIR}\\{FILE_DIR}"

RATIO = True


def main():
    print_cardinalities(ratio=RATIO)


def print_cardinalities(ratio: bool):
    with open(FULL_DIR, "r", encoding="utf-8") as f:
        data = json.load(f)
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
        data["by_language_2"] = data["by_language"].copy()
        for lang in data["by_language"].keys():
            data["by_language"][lang] = {key: round(value/total_by_numbers[key], 2) for key, value in data["by_language"][lang].items()}
            data["by_language_2"][lang] = {key: round(value / total_by_lang[lang], 2) for key, value in
                                         data["by_language_2"][lang].items()}
        data["by_couples"] = {key.upper(): round(value/total_by_couples, 2) for key, value in data["by_couples"].items()}
        data["by_triples"] = {key.upper(): round(value/total_by_triples, 2) for key, value in data["by_triples"].items()}
    print_overall(data["overall"])
    print_languages(data["by_language"])
    print_languages_2(data["by_language_2"])
    print_overall(data["by_couples"], xlabel="Different couples", title="News translated in two different languages")
    print_overall(data["by_triples"], xlabel="Different triples", title="News translated in three different languages")


def print_overall(data: dict, xlabel: str = "Different versions", ylabel: str = "News",
                  title: str = "Translations of news in different languages"):
    ax = plt.subplot(111)
    bars = ax.bar(data.keys(), data.values())
    ax.bar_label(bars)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
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
            ax.legend([bars1, bars2, bars3, bars4], ["ENG", "FRE", "GER", "ITA"])
    plt.xticks([1, 2, 3, 4])
    plt.xlabel("Different versions")
    plt.ylabel("News")
    plt.title(f"Translations of news in different versions by language")
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
            ax.legend([bars1, bars2, bars3, bars4], ["1 version", "2 versions", "3 versions", "4 versions"])
    plt.xticks(range(1, 5), ["ENG", "FRE", "GER", "ITA"])
    plt.xlabel("Different versions")
    plt.ylabel("News")
    plt.title(f"Translations of news in different versions by language")
    plt.show()


if __name__ == "__main__":
    main()
