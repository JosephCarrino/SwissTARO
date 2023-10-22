import os
import pandas as pd
from utils import get_cite_matrix
import holoviews as hv

METHODS = ["LINKED", "SPACY"]
CHOSEN_METHOD = METHODS[0]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}\\..\\..\\out"
FILE_DIR = f"commons_2023-09-27T00.00.00_2023-10-03T23.59.00_{CHOSEN_METHOD}.json"
FULL_DIR = f"{OUT_DIR}\\{FILE_DIR}"


def main():
    print_chorded(False)


def print_chorded(ratio: bool = False):
    df, infos = get_cite_matrix(FULL_DIR)
    if ratio:
        for lang in df.columns:
            df[lang] = df[lang].div(infos["len"][lang])
    sources = []
    for lang in df.columns:
        for i in range(4):
            sources.append(lang)
    targets = []
    for i in range(4):
        for lang in df.columns:
            targets.append(lang)
    values = []
    for lang1 in df.columns:
        for lang2 in df.columns:
            values.append(df[lang1][lang2])
    data = pd.DataFrame({
        'Source': sources,
        'Target': targets,
        'Value': values
    })
    hv.extension("bokeh")
    chord = hv.Chord(data)
    chord.opts(
        node_color="index",
        node_size=30,
        edge_color="source",
        cmap="Category20",
        label_index="index",
        label_text_color="white",
    )

    # Render the ChordPlot to an HTML file
    hv.save(chord, 'chord_plot.html')


if __name__ == "__main__":
    main()