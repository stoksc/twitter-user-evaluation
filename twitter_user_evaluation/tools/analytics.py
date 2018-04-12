''' This module provides functions for analyzing tweets.
'''
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from rake_nltk import Rake

from .retrieval import Tweet

nltk.download('vader_lexicon')


HSL1 = "hsl(280, 70%, 50%)"
HSL2 = "hsl(15, 70%, 50%, 1)"
HSL3 = "hsl(175, 70%, 50%, 1)"
INTERVALS = 60
MODEL = SentimentIntensityAnalyzer()
RAKE = Rake()


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
        'volume_line_graph': volume_by_interval(tweets, INTERVALS),
    }


def related_hashtags(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the hashtags that appear.
    '''
    occurences = {}
    for tweet in tweets:
        for hashtag in tweet.hashtag_mentions:
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
        for screen_name in tweet.user_mentions:
            if screen_name in occurences:
                occurences[screen_name] += 1
            else:
                occurences[screen_name] = 1
    return occurences


def average_sentiment(tweets: [Tweet]) -> float:
    ''' Function takes a list of tweets and returns the average
    sentiment of them.
    '''
    total = 0
    for tweet in tweets:
        total += MODEL.polarity_scores(tweet.cleaned_text)['compound']
    return total/len(tweets)


def popularity(tweet: Tweet) -> int:
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def controversiality(tweet: Tweet) -> float:
    ''' Function takes a tweet and returns how controversial a tweet is.
    '''
    return MODEL.polarity_scores(tweet.cleaned_text)['neg']


def volume_by_interval(tweets: [Tweet], intervals: int) -> [dict]:
    ''' This function takes a list of tweets and locates the newest and oldest
    tweets in the bunch. It then breaks the length of time between these into
    intervals and returns the average sentiment of tweets per interval.

    What it returns is a dictionary that, when jsonified renders this:
     http://nivo.rocks/#/line
    React component.
    '''
    if not tweets:
        return []

    favorites_by_interval = {
        'id': 'Favorites',
        'color': HSL1,
        'data': []
    }
    retweets_by_interval = {
        'id': 'Retweets',
        'color': HSL2,
        'data': []
    }
    totals_by_interval = {
        'id': 'Totals',
        'color': HSL3,
        'data': []
    }
    tweets.sort(key=lambda tweet: tweet.time)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_favorites_tally = current_retweets_tally = 0
    for tweet in tweets:
        if tweet.time > current_interval:
            favorites_by_interval['data'].append({
                'color': HSL1,
                'x': (current_interval - (interval_length / 2)),
                'y': current_favorites_tally,
            })
            retweets_by_interval['data'].append({
                'color': HSL2,
                'x': (current_interval - (interval_length / 2)),
                'y': current_retweets_tally,
            })
            totals_by_interval['data'].append({
                'color': HSL3,
                'x': (current_interval - (interval_length / 2)),
                'y': (current_favorites_tally + current_retweets_tally),
            })
            current_interval += interval_length
            current_favorites_tally = current_retweets_tally = 0
        current_favorites_tally += tweet.favorites
        current_retweets_tally += tweet.retweets
    return [
        favorites_by_interval,
        retweets_by_interval,
        totals_by_interval,
    ]
