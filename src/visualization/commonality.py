import os
import seaborn as sns
import matplotlib.pyplot as plt
from utils import get_cite_matrix

METHODS = ["LINKED", "SPACY"]
CHOSEN_METHOD = METHODS[0]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}\\..\\..\\out\\commonality_stats"
FILE_DIR = f"2023-10-23T23.45.00_2023-10-23T23.59.00_no_carousels_SPACY.json"
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
    carousels = ""
    if "carousels" in FILE_DIR:
        if "no" in FILE_DIR:
            carousels = " without carousels"
        else:
            carousels = " only carousels"
    sns.set(font_scale=2)
    sns.heatmap(df, annot=True, fmt=".2f", cmap="YlGnBu")
    if CHOSEN_METHOD == METHODS[0]:
        plt.xlabel = "Cited"
        plt.ylabel = "Citing"
    else:
        plt.xlabel = "Pivot"
        plt.ylabel = "Scrolling"
    plt.show()


if __name__ == "__main__":
    main()
