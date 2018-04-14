''' This module provides functions that use a tweepy api to returns tweets by a
user.

Snippet to store the data from as a test file:

with open(os.path.join(os.getcwd(),
                       'tests',
                       'test_data',
                       '{}_data.pickle'.format(screen_name)), 'wb') as outfile:
    pickle.dump([clean_tweet(tweet) for tweet in tweets], outfile)

'''
import calendar
import re
import typing

from nltk.tokenize import TweetTokenizer


TKNZR = TweetTokenizer(strip_handles=True)
HANDLE_REGEX = r'/(^|\b)#\S*($|\b)/'
HASHTAG_REGEX = r'/(^|\b)@\S*($|\b)/'
URL_REGEX = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'


class Tweet(typing.NamedTuple):
    ''' Tweet NamedTuple for easier access.
    '''
    screen_name: str
    time: int
    raw_text: str
    cleaned_text: str
    hashtag_mentions: typing.List[str]
    user_mentions: typing.List[str]
    retweets: int
    favorites: int


def get_tweets_from_user(screen_name: str, api, count=200):
    ''' Receives a screen name to query and a tweepy api object. Uses this
    information to return tweets from this user.
    '''
    tweets = api.user_timeline(screen_name=screen_name, count=count)
    return [clean_tweet(tweet) for tweet in tweets]


def clean_tweet(tweet):
    ''' Takes a tweepy tweet object and returns a dictionary that contains
    the information from the tweet that we actually need.
    '''
    cleaned_text = re.sub(URL_REGEX, '',
                          re.sub(HASHTAG_REGEX, '',
                                 re.sub(HANDLE_REGEX, '', tweet.text)))
    return Tweet(
        screen_name=tweet.user.screen_name,
        time=calendar.timegm(tweet.created_at.utctimetuple()),
        raw_text=tweet.text,
        cleaned_text=cleaned_text,
        hashtag_mentions=[
            hashtag['text'].lower() for hashtag in tweet.entities['hashtags']],
        user_mentions=[
            user['screen_name'] for user in tweet.entities['user_mentions']],
        retweets=tweet.retweet_count,
        favorites=tweet.favorite_count)
