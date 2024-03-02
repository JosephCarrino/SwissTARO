import json
import os
from utils import date_to_epoch, TRANSLATED_NEWS_DIR
from itertools import combinations_with_replacement, combinations


START_DATES = [f"2023-11-{day} 16:15:00" for day in range(15, 21)]
END_DATES = [f"2023-11-{day} 16:29:00" for day in range(15, 21)]
START_EPOCHS: list[float] = [date_to_epoch(START_DATE) for START_DATE in START_DATES]
END_EPOCHS: list[float] = [date_to_epoch(END_DATE) for END_DATE in END_DATES]
OUT_START_DATES = [START_DATE.replace(' ', 'T').replace(':', '.') for START_DATE in START_DATES]
OUT_END_DATES = [END_DATE.replace(' ', 'T').replace(':', '.') for END_DATE in END_DATES]
OUT_PATHS = [f"{item[0]}_{item[1]}" for item in zip(OUT_START_DATES, OUT_END_DATES)]

NUM_TERMS = 10

WORKING_DIR = TRANSLATED_NEWS_DIR

LANGS = [lang for lang in os.listdir(WORKING_DIR)]


def main():
    lang_combs = [list(combinations(LANGS, r)) for r in range(2, 5)]
    all_combs = []
    for comb in lang_combs:
        all_combs += comb

    one_lang = {start: None for start in OUT_START_DATES}
    five_terms = {"orig": {lang: one_lang.copy() for lang in LANGS},
                  "all": {lang: one_lang.copy() for lang in LANGS}}
    for USE_ORIGINALS, use_originals in zip((False, True), ("orig", "all")):
        for lang in LANGS:
            for out_path, out_date in zip(OUT_PATHS, OUT_START_DATES):
                with open(f"../visualization/topic_modeling/{lang}/NER_"
                          f"{'originals_' if USE_ORIGINALS else ''}{out_path}.json", "r") as f:
                    curr_json = json.load(f)
                    curr_dict = five_terms[use_originals][lang][out_date] = curr_json["tinfo"]["Term"][:NUM_TERMS+1]
                    if "%" in curr_dict:
                        curr_dict.remove("%")
                    else:
                        curr_dict = curr_dict[:NUM_TERMS]
    by_day_original = generate_by_day(five_terms["orig"])
    by_day_full = generate_by_day(five_terms["all"])
    analyzed_original = analyze_all_comb(by_day_original, all_combs)
    analyzed_full = analyze_all_comb(by_day_full, all_combs)

    analyzed_original_all_days = analyze_all_comb_all_days(by_day_original, all_combs)
    analyzed_full_all_days = analyze_all_comb_all_days(by_day_full, all_combs)

    with open(f"../visualization/topic_modeling/intersections/originals_{OUT_START_DATES[0]}_{OUT_START_DATES[-1]}.json", "w") as f:
        json.dump(analyzed_original, f, indent=4)
    with open(f"../visualization/topic_modeling/intersections/{OUT_START_DATES[0]}_{OUT_START_DATES[-1]}.json", "w") as f:
        json.dump(analyzed_full, f, indent=4)
    with open(f"../visualization/topic_modeling/intersections/merged_originals_{OUT_START_DATES[0]}_{OUT_START_DATES[-1]}.json", "w") as f:
        json.dump(analyzed_original_all_days, f, indent=4)
    with open(f"../visualization/topic_modeling/intersections/merged_{OUT_START_DATES[0]}_{OUT_START_DATES[-1]}.json", "w") as f:
        json.dump(analyzed_full_all_days, f, indent=4)


def generate_by_day(full_dict: dict) -> dict:
    by_day = {out_date.split("T")[0]: {lang: set() for lang in LANGS} for out_date in OUT_START_DATES}
    for lang in LANGS:
        for out_date in OUT_START_DATES:
            only_date = out_date.split("T")[0]
            by_day[only_date][lang] = set(full_dict[lang][out_date])
    return by_day


def analyze_all_comb(terms: dict, combs: list) -> dict:
    by_day = {day: {'-'.join(comb): None for comb in combs} for day in terms}
    for day in terms:
        for comb in combs:
            lang_sets = [set(terms[day][lang]) for lang in comb]

            final_intersect = lang_sets[0]
            for second_set in lang_sets[1:]:
                final_intersect = final_intersect.intersection(second_set)
            by_day[day]['-'.join(comb)] = (len(final_intersect)/NUM_TERMS*100, list(final_intersect))
    average_overlap = {}
    for comb in combs:
        average_overlap['-'.join(comb)] = [by_day[day]['-'.join(comb)][0] for day in terms]
        average_overlap['-'.join(comb)] = round(sum(average_overlap['-'.join(comb)])/len(average_overlap['-'.join(comb)]),2)
    by_day["average"] = average_overlap
    return by_day


def analyze_all_comb_all_days(terms: dict, combs: list) -> dict:
    to_ret = {'-'.join(comb): None for comb in combs}
    for comb in combs:
        MAX_TERMS = 0
        lang_sets = []
        for lang in comb:
            single_set = []
            for day in terms:
                single_set += terms[day][lang]
                MAX_TERMS = max(MAX_TERMS, len(set(single_set)))
            lang_sets.append(set(single_set))
        final_intersect = lang_sets[0]
        for second_set in lang_sets[1:]:
            final_intersect = final_intersect.intersection(second_set)
        to_ret['-'.join(comb)] = (round(len(final_intersect)/MAX_TERMS*100,2), list(final_intersect))
    return to_ret


if __name__ == "__main__":
    main()