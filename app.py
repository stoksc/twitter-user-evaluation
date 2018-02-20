''' This module uses flask to implement a microservices that exposes a REST API for the
project's PHP backend to consume. It takes a couple queries:
    GET /?hashtag=hashtag
        sends back a json object with analysis of the hashtag
    GET /?user=user
        sends back a json object with analysis of the user
'''

from flask import Flask, jsonify, make_response, request
import tweepy

from tools.tweetgrabber import get_tweets_with_hashtag
from tools.tweetgrabber import get_tweets_from_user
from tools.tweetanalytics import analyze_tweets


app = Flask(__name__)

auth = tweepy.OAuthHandler(
    '',
    '')
auth.set_access_token(
    '',
    '')
api = tweepy.API(auth, wait_on_rate_limit=True)


@app.route('/', methods=['GET'])
def get_hashtag_analytics():
    ''' This method handles a request of the form:
    http://serviceurl/?hashtag=hashtagtoquery
    and returns some analysis on the hashtag.
    '''
    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']
        tweets = get_tweets_with_hashtag(hashtag, api)

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
