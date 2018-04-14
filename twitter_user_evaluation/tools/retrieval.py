''' This module provides functions that use a tweepy api to returns tweets by a
user.
'''
import calendar
from collections import namedtuple
import re

from nltk.tokenize import TweetTokenizer
from tweepy.models import Status
from tweepy.api import API


TKNZR = TweetTokenizer(strip_handles=True)
URL_REGEX = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
HASHTAG_REGEX = r'/(^|\b)@\S*($|\b)/'
HANDLE_REGEX = r'/(^|\b)#\S*($|\b)/'

Tweet = namedtuple('Tweet', [
    'screen_name',
    'time',
    'raw_text',
    'cleaned_text',
    'timezone',
    'hashtag_mentions',
    'user_mentions',
    'retweets',
    'favorites'])


def get_tweets_from_user(screen_name: str, api: API, count=200) -> [Tweet]:
    ''' Receives a screen name to query and a tweepy api object. Uses this
    information to return tweets from this user.
    '''
    tweets = api.user_timeline(screen_name=screen_name, count=count)
    return [clean_tweet(tweet) for tweet in tweets]


def clean_tweet(tweet: Status) -> Tweet:
    ''' Takes a tweepy tweet object and returns a dictionary that contains
    the information from the tweet that we actually need.
    '''
    cleaned_text = re.sub(URL_REGEX, '',
                          re.sub(HASHTAG_REGEX, '',
                                 re.sub(HANDLE_REGEX, '', tweet.text)))
    return Tweet(
        tweet.user.screen_name,
        calendar.timegm(tweet.created_at.utctimetuple()),
        tweet.text,
        cleaned_text,
        tweet.user.time_zone,
        [hashtag['text'].lower() for hashtag in tweet.entities['hashtags']],
        [user['screen_name'] for user in tweet.entities['user_mentions']],
        tweet.retweet_count,
        tweet.favorite_count)
