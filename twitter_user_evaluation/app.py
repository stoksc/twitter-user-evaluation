''' This module uses flask to implement a microservices that exposes a REST API
for the project's PHP backend to consume. It takes a couple queries:
    GET /?user=user
        sends back a json object with analysis of the user
'''
import os

from flask import jsonify, make_response, request

from .tools.analytics import analyze_tweets
from .tools.default_responses import BAD_QUERY_RESPONSE, BAD_QUERY_CODE, \
    BAD_ROUTE_RESPONSE, BAD_ROUTE_CODE, NULL_QUERY_RESPONSE, NULL_QUERY_CODE, \
    OK_QUERY_CODE
from .tools.flasks import FlaskWithTwitterAPI
from .tools.retrieval import get_tweets_from_user


app = FlaskWithTwitterAPI(
    __name__,
    twitter_consumer_key=os.environ['TWITTER_CK'],
    twitter_consumer_secret=os.environ['TWITTER_CS'],
    twitter_access_token=os.environ['TWITTER_AT'],
    twitter_access_token_secret=os.environ['TWITTER_ATS'],)


@app.route('/', methods=['GET'])
def get_analytics():
    ''' This method handles a request of the form:
        /?user=usertoquery
    and returns some analysis on the hashtag.
    '''
    if 'user' in request.args:
        user = request.args['user']
        tweets = get_tweets_from_user(user, app.api)
    else:
        return make_response(jsonify(BAD_QUERY_RESPONSE), BAD_QUERY_CODE)

    if not tweets:
        return make_response(jsonify(NULL_QUERY_RESPONSE), NULL_QUERY_CODE)

    response = analyze_tweets(tweets)
    return make_response(jsonify(response), OK_QUERY_CODE)


@app.errorhandler(BAD_ROUTE_CODE)
def not_found(_):
    ''' This method handles invalid requests by sending a 404 response.
    '''
    return make_response(jsonify(BAD_ROUTE_RESPONSE), BAD_ROUTE_CODE)
