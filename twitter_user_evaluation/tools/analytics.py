''' This module provides functions for analyzing tweets.
'''
import datetime
from typing import List
import os
import pickle

from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import numpy as np

from .retrieval import Tweet


# constants and file paths
HSL1 = "hsl(280, 70%, 50%)"
HSL2 = "hsl(15, 70%, 50%, 1)"
HSL3 = "hsl(175, 70%, 50%, 1)"
INTERVALS = 15
MAX_BAR_FIELDS = 50
POL_MODEL_DIR = os.path.join('twitter_user_evaluation', 'tools', 'models')
POL_MODEL_TKNZR_PATH = os.path.join(POL_MODEL_DIR, 'cdo_tknzr.pickle')
POL_MODEL_PATH = os.path.join(POL_MODEL_DIR, 'conv_dropout_model.h5')


# nltk tools and models
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')
MODEL = SentimentIntensityAnalyzer()

# keras political sentiment model
MAX_SEQUENCE_LENGTH = 1000
with open(POL_MODEL_TKNZR_PATH, 'rb') as handle:
    POL_MODEL_TKNZR = pickle.load(handle)
POL_MODEL = load_model(POL_MODEL_PATH)
POL_MODEL.predict(np.zeros((1, MAX_SEQUENCE_LENGTH)))


def analyze_tweets(tweets: List[Tweet]):
    ''' This function takes a group of tweets and returns statistics
    on them like average sentiment and related hashtags.
    '''
    return {
        'related_hashtag': related_hashtags(tweets),
        'related_user': related_users(tweets),
        'volume_line_graph': volume_by_interval(tweets, INTERVALS),
        'scatter_graph': political_sentiment_scatter(tweets),
        'named_entity_bar_graph': all_ne_occurences(tweets)}


def related_hashtags(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the hashtags that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    hashtag_occurences = {}
    for tweet in tweets:
        for hashtag in tweet.hashtag_mentions:
            if hashtag in hashtag_occurences:
                hashtag_occurences[hashtag][0] += 1
                hashtag_occurences[hashtag][1].append(tweet.tweet_id)
            else:
                hashtag_occurences[hashtag] = [1, [tweet.tweet_id]]
    return [{
        'id': hashtag,
        'label': hashtag,
        'value': occurences,
        'color': HSL1,
        'tweet_ids': ids,
        } for hashtag, (occurences, ids) in hashtag_occurences.items()]


def related_users(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the users that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    user_occurences = {}
    for tweet in tweets:
        for screen_name in tweet.user_mentions:
            if screen_name in user_occurences:
                user_occurences[screen_name][0] += 1
                user_occurences[screen_name][1].append(tweet.tweet_id)
            else:
                user_occurences[screen_name] = [1, [tweet.tweet_id]]
    return [{
        'id': user,
        'label': user,
        'value': occurences,
        'color': HSL1,
        'tweet_ids': ids,
        } for user, (occurences, ids) in user_occurences.items()]


def popularity(tweet: Tweet):
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def volume_by_interval(tweets: List[Tweet], intervals: int):
    ''' This function takes a list of tweets and locates the newest and oldest
    tweets in the bunch. It then breaks the length of time between these into
    intervals and returns the average sentiment of tweets per interval.

    What it returns is a dictionary that, when jsonified renders this React
    component.
        http://nivo.rocks/#/line
    '''
    favorites_by_interval = {'id': 'Favorites', 'color': HSL1, 'data': []}
    retweets_by_interval = {'id': 'Retweets', 'color': HSL2, 'data': []}
    totals_by_interval = {'id': 'Totals', 'color': HSL3, 'data': []}
    tweets.sort(key=lambda tweet: tweet.time)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_favorites_tally = current_retweets_tally = 0
    for tweet in tweets:
        if tweet.time > current_interval:
            favorites_by_interval['data'].append({
                'color': HSL1,
                'x': datetime.datetime.fromtimestamp(
                    current_interval - (interval_length / 2)).strftime('%m/%d'),
                'y': current_favorites_tally})
            retweets_by_interval['data'].append({
                'color': HSL2,
                'x': datetime.datetime.fromtimestamp(
                    current_interval - (interval_length / 2)).strftime('%m/%d'),
                'y': current_retweets_tally})
            totals_by_interval['data'].append({
                'color': HSL3,
                'x': datetime.datetime.fromtimestamp(
                    current_interval - (interval_length / 2)).strftime('%m/%d'),
                'y': (current_favorites_tally + current_retweets_tally)})
            current_interval += interval_length
            current_favorites_tally = current_retweets_tally = 0
        current_favorites_tally += tweet.favorites
        current_retweets_tally += tweet.retweets
    return [
        favorites_by_interval,
        retweets_by_interval,
        totals_by_interval]


def all_ne_occurences(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the hashtags that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/bar
    '''
    word_occurences = {}
    for tweet in tweets:
        cleaned_text = parse_ne_chunk(tweet.cleaned_text)
        if MODEL.polarity_scores(tweet.cleaned_text)['compound'] >= 0:
            sent = 'pos'
        else:
            sent = 'neg'
        for word in cleaned_text:
            if word in word_occurences:
                word_occurences[word][sent] += 1
            else:
                word_occurences[word] = {
                    'pos': 0,
                    'neg': 0}
                word_occurences[word][sent] += 1
    return sorted([{
        'id': word,
        'positive_occurences': occurences['pos'],
        'positive_occurencesColor': HSL2,
        'negative_occurences': occurences['neg'],
        'negative_occurencesColor': HSL1,
        } for word, occurences in word_occurences.items()],
                  key=lambda x: -(x['positive_occurences'] + \
                                  x['negative_occurences']))[:MAX_BAR_FIELDS]


def parse_ne_chunk(text):
    ''' Takes texts and finds the named entities

    why write it when it's already there.
    credit on so:
        /questions/31836058/nltk-named-entity-recognition-to-a-python-list
    '''
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if isinstance(i, Tree):
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
    return continuous_chunk


def political_sentiment_scatter(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns a bunch of data. It's the
    sentiment, polarity and political sentiment of the tweets but organized in
    a strange way so that when jsonified, it renders as this React component:
        http://nivo.rocks/#/scatterplot/
    '''
    sequences = POL_MODEL_TKNZR.texts_to_sequences(
        [tweet.raw_text for tweet in tweets])
    sequences = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    global POL_MODEL
    preds = POL_MODEL.predict(sequences)
    return [{
        'id': tweet.raw_text,
        'data': [{
            'id': i,
            'y': popularity(tweet),
            'x': float(pol_sent[1]),
        }]} for i, (tweet, pol_sent) in enumerate(zip(tweets, preds))]
