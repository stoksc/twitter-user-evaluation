import os

import nltk
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd


nltk.download('wordnet')

TOKENIZER = RegexpTokenizer(r'\w+')
STOPWORD_SET = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()


def get_data(clean_stopwords=False, lemmatize=False):
    senators = pd.read_csv('pol_accounts.csv', sep=";", error_bad_lines=False)[['id', 'array_agg']]
    df = pd.read_csv('pol_tweets.csv', sep=";", error_bad_lines=False)[['user_id', 'tweet_text']]
    df = pd.merge(df, senators, left_on='user_id', right_on='id', how='left')
    df.dropna(axis=0, how='any', inplace=True)

    df['array_agg'] = df.array_agg.apply(to_category)
    if clean_stopwords and lemmatize:
        df['tweet_text'] = df.tweet_text.apply(nlp_clean, lemmatize=True)
    if clean_stopwords:
        df['tweet_text'] = df.tweet_text.apply(nlp_clean)
    df.dropna(axis=0, how='any', inplace=True)

    return df['tweet_text'], df['array_agg']


def to_category(entry):
    if ('democrat' in entry) or ('Democrat' in entry):
        return 1
    elif ('republican' in entry) or ('Republican' in entry):
        return 0
    return None


def nlp_clean(sentence, lemmatize=False):
    new_str = sentence.lower()
    tokenized_text = TOKENIZER.tokenize(new_str)
    tokenized_text = list(set(tokenized_text).difference(STOPWORD_SET))
    if lemmatize:
        tokenized_text = [LEMMATIZER.lemmatize(word) for word in tokenized_text]
    return ' '.join(tokenized_text)
