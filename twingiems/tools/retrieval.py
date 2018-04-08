''' This module provides functions that use a tweepy api to returns tweets by a
user.
'''
from collections import namedtuple


Tweet = namedtuple('Tweet', [
    'screen_name',
    'time',
    'text',
    'timezone',
    'hashtags',
    'retweets',
    'favorites'])


def get_tweets_from_user(screen_name: str, api, count=200) -> [Tweet]:
    ''' Receives a screen name to query and a tweepy api object. Uses this
    information to return tweets from this user.
    '''
    tweets = api.user_timeline(screen_name=screen_name, count=count)
    return [clean_tweet(tweet) for tweet in tweets]


def clean_tweet(tweet: dict) -> Tweet:
    ''' Takes a tweepy tweet object and returns a dictionary that contains
    the information from the tweet that we actually need.
    '''
    return Tweet(
        tweet.user.screen_name,
        tweet.created_at,
        tweet.text,
        tweet.user.time_zone,
        tweet.entities['hashtags'],
        tweet.retweet_count,
        tweet.favorite_count)
