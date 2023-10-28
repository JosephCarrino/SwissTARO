import plotly.graph_objects as go
import json
import os
import matplotlib.pyplot as plt

SEPARATOR = "\\"
# SEPARATOR = "/"

START_DATE = "2023-10-19 00:00:00"
END_DATE = "2023-10-23 23:59:00"
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}..{SEPARATOR}out{SEPARATOR}originals_stats{SEPARATOR}"
OUT_PATH = f"{OUT_DIR}{OUT_START_DATE}_{OUT_END_DATE}"

CAROUSELS = ["_no_carousels", "_carousels", ""]
CAROUSELS_STRING = [" excluding carousels", " only carousels", ""]


def main():
    for carousel, carousel_string in zip(CAROUSELS, CAROUSELS_STRING):
        plot_sankey(f"{OUT_PATH}{carousel}.json", carousel_string)


def plot_sankey(path: str, carousel: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sources = []
    targets = []
    values = []
    i = 0
    for source in data.keys():
        j = 0
        for target in data[source].keys():
            if j == i:
                j += 1
            sources.append(i)
            targets.append(j)
            values.append(data[source][target])
            j += 1
        i += 1
    for i in range(len(targets)):
        targets[i] = targets[i] + len(data.keys())
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig = go.Figure(data=[go.Sankey(
        valueformat=".0f",
        valuesuffix=" items",
        # Define nodes
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[*list(data.keys()), *list(data.keys())],
            color=colors
        ),
        # Add links
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        ))])
    fig.update_layout(title_text=f"News translation{carousel}", font_size=10)
    fig.show()


if __name__ == "__main__":
    main()
