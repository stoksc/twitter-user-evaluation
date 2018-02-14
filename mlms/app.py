import json

from flask import jsonify, request, make_response

from TwitterFlask import TwitterFlask
from TweetAnalytics import get_tweets_with_hashtag
from TweetAnalytics import most_x, popularity, controversiality

keys = {
    'consumer_key' : '',
    'consumer_secret' : '',
    'access_token' : '',
    'access_token_secret' : '',
}

app = TwitterFlask(__name__, keys)

@app.route('/', methods=['GET'])
def get_hashtag_analytics():
    ''' This method handles a request of the form:
    http://serviceurl/?hashtag=hashtagtoquery
    and returns some analysis on the hashtag.
    '''
    response = {}

    if 'hashtag' in request.args:
        hashtag = request.args['hashtag']

        tweets = get_tweets_with_hashtag(
            hashtag,
            app.api,
            app.count,
            app.lang
        )

        # TODO: implement each function called
        response = {
            'most_popular_tweet' : most_x(tweets, x=popularity),
            'most_controversial_tweet' : most_x(tweets, x=controversiality),
            # 'sentiment' : average_sentiment(tweets),
            # 'related_hashtag' : most_related(tweets, hashtag),
            # 'related_user' : most_related(tweets)
        }

    return make_response(jsonify(response), 201)


@app.errorhandler(404)
def not_found(error):
    ''' This method handles invalid requests by sending a 404 response.
    '''
    response = {'error': 'bad request'}
    return make_response(jsonify(response), 404)


if __name__ == "__main__":
    app.run()
