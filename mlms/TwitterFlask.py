from flask import Flask
import tweepy

class TwitterFlask(Flask):
    def __init__(self, name, keys, count=1, lang='en'):
        super().__init__(name)

        # init twitter api connection
        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

        # defaults
        self.count = count
        self.lang = lang
