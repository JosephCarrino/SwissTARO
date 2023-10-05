import json
import pandas as pd


def get_cite_matrix(in_dir: str) -> tuple[pd.DataFrame, dict]:
    with open(in_dir, "r", encoding="utf-8") as f:
        data = json.load(f)
    infos = data["info"]
    del data["info"]
    df = pd.DataFrame(data, dtype=float)
    return df, infos
