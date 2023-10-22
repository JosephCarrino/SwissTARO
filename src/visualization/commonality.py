import os
import seaborn as sns
import matplotlib.pyplot as plt
from utils import get_cite_matrix

METHODS = ["LINKED", "SPACY"]
CHOSEN_METHOD = METHODS[0]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}\\..\\..\\out"
FILE_DIR = f"commons_2023-09-27T00.00.00_2023-10-03T23.59.00_{CHOSEN_METHOD}.json"
FULL_DIR = f"{OUT_DIR}\\{FILE_DIR}"


RATIO = False


def main():
    print_heatmap(ratio=RATIO)


def print_heatmap(ratio: bool):
    df, infos = get_cite_matrix(FULL_DIR)
    if ratio:
        for lang in df.columns:
            df[lang] = df[lang].div(infos["len"][lang])
    cit_or_piv = "Cited" if CHOSEN_METHOD == METHODS[0] else "Pivot"
    with_ratio = f" divided by {cit_or_piv} total news" if ratio else ""
    sns.heatmap(df, annot=True, fmt=".2f", cmap="YlGnBu").set_title(f"News in common{with_ratio}")
    if CHOSEN_METHOD == METHODS[0]:
        plt.xlabel = "Cited"
        plt.ylabel = "Citing"
    else:
        plt.xlabel = "Pivot"
        plt.ylabel = "Scrolling"
    plt.show()


if __name__ == "__main__":
    main()
