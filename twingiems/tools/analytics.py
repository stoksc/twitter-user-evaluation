''' This module provides functions for analyzing tweets.
'''

import re

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from .retrieval import Tweet

nltk.download('vader_lexicon')

REGEX_STR = r'<[^>]+>|(?:@[\w_]+)|(?:\#+[\w_]+[\w\'_\-]*[\w_]+)|\
http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|\
(?:%[0-9a-f][0-9a-f]))+|(?:(?:\d+,?)+(?:\.?\d+)?)'

MODEL = SentimentIntensityAnalyzer()


def analyze_tweets(tweets: [Tweet]) -> dict:
    ''' This function takes a group of tweets and returns statistics
    on them like average sentiment and related hashtags
    '''
    return {
        'most_popular_tweet' : max(tweets, key=popularity),
        'most_controversial_tweet' : max(tweets, key=controversiality),
        'sentiment' : average_sentiment(tweets),
        'related_hashtag' : most_related_hashtags(tweets),
        # 'related_user' : most_related(tweets),
    }


def most_related_hashtags(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets (represented as dictionaries) and
    returns the hashtags that appear most frequently.
    '''
    occurences = {}
    for tweet in tweets:
        for hashtag in tweet.hashtags:
            hashtag = hashtag['text'].lower()
            if hashtag in occurences:
                occurences[hashtag] += 1
            else:
                occurences[hashtag] = 1
    return occurences


def average_sentiment(tweets: [Tweet]) -> float:
    ''' Function takes a list of tweets and returns the average
    sentiment of them.
    '''
    tweet_texts = clean_text(tweets)
    total = 0
    for tweet_text in tweet_texts:
        total += MODEL.polarity_scores(tweet_text)['compound']
    return total/len(tweets)


def clean_text(tweets: [Tweet]) -> [Tweet]:
    ''' Takes tweets and returns tweets with tweet.text as safe, plain text,
    cleaned of emojis, foreign characters and everything else that breaks NLTK.
    '''
    return [re.sub(REGEX_STR, '', tweet.text) for tweet in tweets]


def popularity(tweet: Tweet) -> int:
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def controversiality(tweet: Tweet) -> float:
    ''' Function takes a tweet and returns how controversial a tweet is.
    '''
    return MODEL.polarity_scores(tweet.text)['neg']
