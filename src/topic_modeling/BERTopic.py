import os
from bertopic import BERTopic
from src.utils import get_dict_items
from src.utils import NEWS_DIR, TRANSLATED_NEWS_DIR, UseCarousels
from src.utils import date_to_epoch

WORKING_DIR = TRANSLATED_NEWS_DIR

LANGS = [lang for lang in os.listdir(WORKING_DIR)]

START_DATE = "2023-09-26 00:00:00"
END_DATE = "2023-09-26 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')
OUT_PATH = f"{OUT_START_DATE}_{OUT_END_DATE}"


FROM_ORIGINALS =

def get_topic_model(news_dict: dict):
    to_ret_topics = {}
    for lang in news_dict.keys():
        contents = [new["en_content"] for new in news_dict[lang]]
        timestamps = [new["epoch"] for new in news_dict[lang]]
        topic_model = BERTopic()
        topics, _ = topic_model.fit_transform(contents)
        topics_over_time = topic_model.topics_over_time(contents, timestamps, nr_bins=10)
        to_ret_topics[lang] = {"topics": topics, "topics_over_time": topics_over_time}
    return to_ret_topics


def main():
    news_dict = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=UseCarousels.NO)
    topic_model = get_topic_model(news_dict)
