''' This module provides functions for analyzing tweets.
'''
import datetime
import re

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from .retrieval import Tweet

nltk.download('vader_lexicon')


INTERVALS = 60
MODEL = SentimentIntensityAnalyzer()
REGEX_TO_CLEAN = r'<[^>]+>|(?:@[\w_]+)|(?:\#+[\w_]+[\w\'_\-]*[\w_]+)|\
http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|\
(?:%[0-9a-f][0-9a-f]))+|(?:(?:\d+,?)+(?:\.?\d+)?)'
REGEX_TO_FIND_HANDLES = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'


def analyze_tweets(tweets: [Tweet]) -> dict:
    ''' This function takes a group of tweets and returns statistics
    on them like average sentiment and related hashtags
    '''
    return {
        'most_popular_tweet' : max(tweets, key=popularity),
        'most_controversial_tweet' : max(tweets, key=controversiality),
        'sentiment' : average_sentiment(tweets),
        'related_hashtag' : related_hashtags(tweets),
        'related_user' : related_users(tweets),
        'activity_by_interval': activity_by_interval(tweets, INTERVALS),
    }


def related_hashtags(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the hashtags that appear.
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


def related_users(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the users that appear.
    '''
    occurences = {}
    for tweet in tweets:
        handle = re.search(REGEX_TO_FIND_HANDLES, tweet.text)
        if not handle:
            continue
        handle = handle.group(0)
        if handle in occurences:
            occurences[handle] += 1
        else:
            occurences[handle] = 1
    return occurences


def average_sentiment(tweets: [Tweet]) -> float:
    ''' Function takes a list of tweets and returns the average
    sentiment of them.
    '''
    tweet_texts = [clean_text(tweet) for tweet in tweets]
    total = 0
    for tweet_text in tweet_texts:
        total += MODEL.polarity_scores(tweet_text)['compound']
    return total/len(tweets)


def clean_text(tweet: Tweet) -> None:
    ''' Takes tweets and returns tweets with tweet.text as safe, plain text,
    cleaned of emojis, foreign characters and everything else that breaks NLTK.
    '''
    return re.sub(REGEX_TO_CLEAN, '', tweet.text)


def popularity(tweet: Tweet) -> int:
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def controversiality(tweet: Tweet) -> float:
    ''' Function takes a tweet and returns how controversial a tweet is.
    '''
    return MODEL.polarity_scores(tweet.text)['neg']


def activity_by_interval(tweets: [Tweet], intervals: int) -> [dict]:
    ''' This function takes a list of tweets and locates the newest and oldest
    tweets in the bunch. It then breaks the length of time between these into
    intervals and returns the average sentiment of tweets per interval.
    '''
    activity_by_interval = []
    if not len(tweets):
        return []

    tweets.sort(key=lambda tweet: tweet.time)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_interval_tally = 0
    current_interval_sentiment = 0
    for tweet in tweets:
        if tweet.time > current_interval:
            activity_by_interval.append({
                'interval': (current_interval - (interval_length / 2)),
                'tweets': current_interval_tally,
                'sentiment': current_interval_sentiment / current_interval_tally
            })
            current_interval += interval_length
            current_interval_tally = 0
            current_interval_sentiment = 0
        current_interval_tally += 1
        current_interval_sentiment += MODEL.polarity_scores(clean_text(tweet))['compound']
    return activity_by_interval
