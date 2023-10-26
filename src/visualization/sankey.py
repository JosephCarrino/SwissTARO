import plotly.graph_objects as go
import json
import os

SEPARATOR = "\\"
# SEPARATOR = "/"

START_DATE = "2023-10-19 00:00:00"
END_DATE = "2023-10-23 23:59:00"
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = f"{BASE_DIR}{SEPARATOR}..{SEPARATOR}out{SEPARATOR}originals_stats{SEPARATOR}"
OUT_PATH = f"{OUT_DIR}{OUT_START_DATE}_{OUT_END_DATE}"

CAROUSELS = ["_no_carousels", "_carousels", ""]


def main():
    for carousel in CAROUSELS:
        plot_sankey(f"{OUT_PATH}{carousel}.json", carousel)


def plot_sankey(path: str, carousel: str):
    pass


if __name__ == "__main__":
    main()