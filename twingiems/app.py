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
    'wGecVg5soVa5lIZR8l5iX5XYi',
    'C0lATkNWD14ve6FOKHcbK0CoWoRsrFLd8VWdta0YabG3dlmnZF')
auth.set_access_token(
    '318694853-64JKzz76Al4Aakddw7tSEL0Ku6Pvqib9pqHfna8a',
    'nc3H9mEIsdBKeJppub7gtCH6O8wst4SF14p1agoUpmzRa')
api = tweepy.API(auth, wait_on_rate_limit=True)

NULL_QUERY_RESPONSE = {
    'error': 'query returned no tweets'
}

BAD_QUERY_RESPONSE = {
    'error': 'request was not hashtag or user'
}

BAD_ROUTE_RESPONSE = {
    'error': 'bad route'
}


@app.route('/', methods=['GET'])
def get_analytics():
    ''' This method handles a request of the form:
        http://serviceurl/?hashtag=hashtagtoquery
    and returns some analysis on the hashtag.
    '''
    tweets = []
    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']
        tweets = get_tweets_with_hashtag(hashtag, api)
    elif 'user' in request.args:
        user = request.args['user']
        tweets = get_tweets_from_user(user, api)
    else:
        return make_response(jsonify(BAD_QUERY_RESPONSE), 400)

    if len(tweets) == 0:
        return make_response(jsonify(NULL_QUERY_RESPONSE), 400)

    response = analyze_tweets(tweets)
    return make_response(jsonify(response), 200)


@app.errorhandler(404)
def not_found(error):
    ''' This method handles invalid requests by sending a 404 response.
    '''
    return make_response(jsonify(BAD_ROUTE_RESPONSE), 404)
