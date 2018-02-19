import json

from flask import jsonify, request, make_response

from tools.tweetflask import TweetFlask
from tools.tweetgrabber import get_tweets_with_hashtag
from tools.tweetgrabber import get_tweets_from_user
from tools.tweetanalytics import analyze_tweets


keys = {
    'consumer_key' : '',
    'consumer_secret' : '',
    'access_token' : '',
    'access_token_secret' : '',
}

app = TweetFlask(__name__, keys)


@app.route('/', methods=['GET'])
def get_hashtag_analytics():
    ''' This method handles a request of the form:
    http://serviceurl/?hashtag=hashtagtoquery
    and returns some analysis on the hashtag.
    '''
    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']
        tweets = get_tweets_with_hashtag(hashtag, app.api)

    if 'user' in request.args:
        user = request.args['user']
        tweets = get_tweets_from_user(user, app.api)

    response = analyze_tweets(tweets)
    return make_response(jsonify(response), 201)


@app.errorhandler(404)
def not_found(error):
    ''' This method handles invalid requests by sending a 404 response.
    '''
    response = {'error': 'bad request'}
    return make_response(jsonify(response), 404)


if __name__ == "__main__":
    app.run()
