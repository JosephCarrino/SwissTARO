import nltk
import os
import gensim
import re
import pyLDAvis
import pyLDAvis.gensim
import gensim.corpora as corpora
import matplotlib.pyplot as plt
from pprint import pprint
from nltk.corpus import stopwords
from gensim.utils import simple_preprocess
from utils import get_dict_items, get_originals_data
from utils import NEWS_DIR, TRANSLATED_NEWS_DIR, UseCarousels
from utils import date_to_epoch

# nltk.download('stopwords')

WORKING_DIR = TRANSLATED_NEWS_DIR

LANGS = [lang for lang in os.listdir(WORKING_DIR)]

START_DATE = "2023-10-23 23:45:00"
END_DATE = "2023-10-23 23:59:00"
START_EPOCH: float = date_to_epoch(START_DATE)
END_EPOCH: float = date_to_epoch(END_DATE)
OUT_START_DATE = START_DATE.replace(' ', 'T').replace(':', '.')
OUT_END_DATE = END_DATE.replace(' ', 'T').replace(':', '.')
OUT_PATH = f"{OUT_START_DATE}_{OUT_END_DATE}"

NUM_TOPICS = 5

USE_ORIGINALS = True


def main():
    models = full_pipe()
    for lang in models.keys():
        LDAvis_prepared = pyLDAvis.gensim.prepare(models[lang]["model"], models[lang]["corpus"], models[lang]["id2word"], sort_topics=False)
        pyLDAvis.save_html(LDAvis_prepared, f"../visualization/topic_modeling/{lang}/{'originals_' if USE_ORIGINALS else ''}{OUT_PATH}.html")
        for lang_2 in models.keys():
            if lang != lang_2:
                compute_differences(models[lang]["model"], models[lang_2]["model"])


def full_pipe(use_originals=USE_ORIGINALS):
    if use_originals:
        news_dict = get_originals_data(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=UseCarousels.NO,
                                       start_date=OUT_START_DATE, end_date=OUT_END_DATE)["data"]
    else:
        news_dict = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=UseCarousels.NO)
    news_dict = re_preprocessing(news_dict)
    data_words = nltk_preprocessing(news_dict)
    output = {lang: {"model": None, "corpus": None, "id2word": None} for lang in data_words.keys()}
    for lang in data_words.keys():
        corpus, id2word = to_tdf(data_words[lang])
        lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=NUM_TOPICS,
                                               random_state=100,
                                               chunksize=100,
                                               passes=10,
                                               per_word_topics=True)
        pprint(lda_model.print_topics())
        doc_lda = lda_model[corpus]
        print('\nPerplexity: ', lda_model.log_perplexity(corpus))
        coherence_model_lda = gensim.models.CoherenceModel(model=lda_model, texts=data_words[lang], dictionary=id2word,
                                                           coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda)
        output[lang]["model"] = lda_model
        output[lang]["corpus"] = corpus
        output[lang]["id2word"] = id2word
    return output



def re_preprocessing(news_dict: dict) -> dict:
    for lang in news_dict.keys():
        news_dict[lang] = [re.sub(r'[,\.!?]', '', new["en_content"]) for new in news_dict[lang]]
        map(lambda x: x["en_content"].lower(), news_dict[lang])
    return news_dict


def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)


def nltk_preprocessing(news_dict: dict) -> dict:
    stop_words = stopwords.words('english')
    list_contents = {}
    data_words = {lang: [] for lang in news_dict.keys()}
    for lang in news_dict.keys():
        corpus = news_dict[lang]
        i = 0
        for text in corpus:
            data_words[lang].append([])
            for word in simple_preprocess(text):
                if word not in stop_words:
                    data_words[lang][i].append(word)
            i+=1
    return data_words


def to_tdf(data_words: list) -> list:
    id2word = corpora.Dictionary(data_words)
    texts = data_words
    corpus = [id2word.doc2bow(text) for text in texts]
    return corpus, id2word


def compute_differences(first_model, second_model):
    mdiff, annotation = first_model.diff(second_model, distance='jaccard', num_words=50)
    plot_difference(mdiff, title="Topic difference between models", annotation=annotation)


def plot_difference(mdiff, title="", annotation=None):
    fig, ax = plt.subplots(figsize=(18, 14))
    data = ax.imshow(mdiff, cmap='RdBu_r', origin='lower')
    plt.title(title)
    plt.colorbar(data)
    plt.show()


if __name__ == "__main__":
    main()