import os

import nltk
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
import pandas as pd
from sklearn.preprocessing import LabelEncoder


nltk.download('wordnet')

BASE_DIR = os.path.join(os.getcwd(), 'prepared_data')
TEXTS = os.path.join(BASE_DIR, 'texts.pickle')
LABELS = os.path.join(BASE_DIR, 'labels.pickle')

DEBATE_BASE_DIR = os.path.join(os.getcwd(), 'processed_debate_texts')
RAW_DEBATE_TEXTS = os.path.join(DEBATE_BASE_DIR, 'debates.csv')
DEBATE_TEXTS = os.path.join(DEBATE_BASE_DIR, 'texts.pickle')
DEBATE_LABELS = os.path.join(DEBATE_BASE_DIR, 'labels.pickle')

ENCODER = LabelEncoder()
SENTIMENT_MODEL = SentimentIntensityAnalyzer()
TOKENIZER = RegexpTokenizer(r'\w+')
STOPWORD_SET = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()


def get_data(clean_stopwords=False, lemmatize=False):
    if os.path.exists(TEXTS) and os.path.exists(LABELS):
        print('restored data from previous run')
        texts, labels = pd.read_pickle(TEXTS), pd.read_pickle(LABELS)
        print(texts.describe(), labels.describe())
        return texts, labels

    print('skipped restore')
    senators = pd.read_csv('pol_accounts.csv', sep=";", error_bad_lines=False)[['id', 'array_agg']]
    df = pd.read_csv('pol_tweets.csv', sep=";", error_bad_lines=False)[['user_id', 'tweet_text']]
    df = pd.merge(df, senators, left_on='user_id', right_on='id', how='left')
    df.dropna(axis=0, how='any', inplace=True)

    df['array_agg'] = df.apply(lambda row: to_category_with_neutrals(row), axis=1)
    if clean_stopwords and lemmatize:
        df['tweet_text'] = df.tweet_text.apply(nlp_clean, lemmatize=True)
    if clean_stopwords:
        df['tweet_text'] = df.tweet_text.apply(nlp_clean)

    df.dropna(axis=0, how='any', inplace=True)
    df.drop_duplicates(inplace=True, keep='first')
    max_rows = min(df['array_agg'].value_counts())
    new_cats = [
        df[df.array_agg == 0][:max_rows],
        df[df.array_agg == 1][:max_rows],
        df[df.array_agg == -1][:max_rows]]
    df = pd.concat(new_cats)

    ENCODER.fit(df.array_agg)
    df.array_agg = ENCODER.transform(df.array_agg)

    df.tweet_text.to_pickle(TEXTS)
    df.array_agg.to_pickle(LABELS)

    return df['tweet_text'], df['array_agg']


def get_debate_data():
    if os.path.exists(DEBATE_TEXTS) and os.path.exists(DEBATE_LABELS):
        print('restored data from previous run')
        texts, labels = pd.read_pickle(DEBATE_TEXTS), pd.read_pickle(DEBATE_LABELS)
        print(texts.describe(), labels.describe())
        return texts, labels

    print('skipped restore')
    df = pd.read_csv(RAW_DEBATE_TEXTS, sep=";", error_bad_lines=False)

    df.dropna(axis=0, how='any', inplace=True)
    df.drop_duplicates(inplace=True, keep='first')

    df.text.to_pickle(DEBATE_TEXTS)
    df.label.to_pickle(DEBATE_LABELS)

    return df.text, df.label


def to_category_with_neutrals(row):
    score = SENTIMENT_MODEL.polarity_scores(row['tweet_text'])
    if (score['neu'] > score['pos']) and (score['neu'] > score['neg']):
        return 0
    elif ('democrat' in row['array_agg']) or ('Democrat' in row['array_agg']):
        return 1
    elif ('republican' in row['array_agg']) or ('Republican' in row['array_agg']):
        return -1
    return None


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
