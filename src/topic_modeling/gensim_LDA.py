import nltk
import os
import gensim
import re
import gensim.corpora as corpora
from pprint import pprint
from nltk.corpus import stopwords
from gensim.utils import simple_preprocess
from utils import get_dict_items
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

NUM_TOPICS = 30


def main():
    models = full_pipe()

def full_pipe():
    news_dict = get_dict_items(START_EPOCH, END_EPOCH, WORKING_DIR, carousels=UseCarousels.NO)
    news_dict = re_preprocessing(news_dict)
    data_words = nltk_preprocessing(news_dict)
    models = {}
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
        models[lang] = lda_model
    return models



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


if __name__ == "__main__":
    main()