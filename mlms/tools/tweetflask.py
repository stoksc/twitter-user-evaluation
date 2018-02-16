from flask import Flask
import tweepy

class TweetFlask(Flask):
    def __init__(self, name, keys):
        super().__init__(name)

        # init twitter api connection
        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
