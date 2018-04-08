''' This module defines an extension of the default Flask.
'''

from flask import Flask
import tweepy

class FlaskWithTwitterAPI(Flask):
    ''' This class just extends flask.Flask while holding the connection to the
    Twitter API to keep ../app.py a little cleaner.
    '''
    def __init__(self,
                 import_name,
                 twitter_consumer_key=None,
                 twitter_consumer_secret=None,
                 twitter_access_token=None,
                 twitter_access_token_secret=None):
        ''' Initializes an instance of FlaskWithTwitterAPI and makes the connection
        to Twitter's API with tweepy.
        '''
        super(FlaskWithTwitterAPI, self).__init__(import_name)

        assert twitter_consumer_key
        assert twitter_consumer_secret
        assert twitter_access_token
        assert twitter_access_token_secret

        _auth = tweepy.OAuthHandler(
            twitter_consumer_key,
            twitter_consumer_secret)
        _auth.set_access_token(
            twitter_access_token,
            twitter_access_token_secret)
        self.api = tweepy.API(_auth, wait_on_rate_limit=True)

    def check_api_status(self):
        ''' This method checks the status of the connection to Twitter's API.
        '''
        pass
