def most_x(tweets, x=None):
    ''' Function takes an array of dictionaries, each dictionary representing a
    tweet and some information about it. Returns the text of the most popular
    tweet.

    Args:
        tweets (list of dictionaries) - tweet data
        metric (function) - how to grade tweets

    Returns:
        (dicionary) - Contains text and score of the most popular tweet.
    '''

    most_x = float('-inf')

    for tweet in tweets:
        tweet_x = x(tweet)
        if tweet_x > most_x:
            most_x_tweet = tweet
            most_x = tweet_x

    if most_x_tweet is None:
        return {
            'text' : '',
            'strength' : 0,
        }

    # TODO: return link to tweet
    return {
        'text' : most_x_tweet['text'],
        'strength' : most_x,
    }


def popularity(tweet):
    ''' Function takes a tweet and returns how popular the tweet was.

    Args:
        tweet (dictionary) - A dictionary of the stats on a tweet.

    Returns:
        (int) - Number representing the popularity of a tweet.
    '''

    return tweet['favorites'] + tweet['retweets']


def controversiality(tweet):
    ''' Function takes a tweet and returns how controversial a tweet was.

    Args:
        tweet (dictionary) - A dictionary of the stats on a tweet.

    Returns:
        (int) - Number representing the controversiality of a tweet.
    '''

    return tweet['replies'] - tweet['favorites'] - tweet['retweets']


def analyze_tweets(tweets):
    '''
    '''
        # TODO: implement each function called
    return {
            'most_popular_tweet' : most_x(tweets, x=popularity),
            'most_controversial_tweet' : most_x(tweets, x=controversiality),
            # 'sentiment' : average_sentiment(tweets),
            # 'related_hashtag' : most_related(tweets, hashtag),
            # 'related_user' : most_related(tweets)
    }
