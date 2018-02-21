''' This module uses flask to implement a microservices that exposes a REST API for the
project's PHP backend to consume. It takes a couple queries:
    GET /?hashtag=hashtag
        sends back a json object with analysis of the hashtag
    GET /?user=user
        sends back a json object with analysis of the user
'''

from flask import Flask, jsonify, make_response, request
import tweepy

from .tools.tweetgrabber import get_tweets_with_hashtag
from .tools.tweetgrabber import get_tweets_from_user
from .tools.tweetanalytics import analyze_tweets


app = Flask(__name__)

auth = tweepy.OAuthHandler(
    'Vx1XFEUQxygdWrGqSIUSDDKMq',
    'T16DhtlYP7rWxELFgKaDX5IZzRRwzPgIVl5gF9xR845klfmds8')
auth.set_access_token(
    '318694853-64JKzz76Al4Aakddw7tSEL0Ku6Pvqib9pqHfna8a',
    'nc3H9mEIsdBKeJppub7gtCH6O8wst4SF14p1agoUpmzRa')
api = tweepy.API(auth, wait_on_rate_limit=True)


@app.route('/', methods=['GET'])
def get_hashtag_analytics():
    ''' This method handles a request of the form:
    http://serviceurl/?hashtag=hashtagtoquery
    and returns some analysis on the hashtag.
    '''
    response = {'error': 'bad request'}
    
    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']
        print(type(api))
        tweets = get_tweets_with_hashtag(hashtag, api)
        response = analyze_tweets(tweets)

    if 'user' in request.args:
        user = request.args['user']
        tweets = get_tweets_from_user(user, api)
        response = analyze_tweets(tweets)

    return make_response(jsonify(response), 201)


@app.errorhandler(404)
def not_found():
    ''' This method handles invalid requests by sending a 404 response.
    '''
    response = {'error': 'bad request'}
    return make_response(jsonify(response), 404)


if __name__ == "__main__":
    app.run()
