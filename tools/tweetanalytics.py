def analyze_tweets(tweets):
    ''' This function takes a group of tweets and returns some statistics on
    them.

    Args:

    '''
    # TODO: implement each function called
    print(tweets)
    return {
        'most_popular_tweet' : max(tweets, key=lambda tweet: popularity(tweet)),
        'most_controversial_tweet' : max(tweets, key=lambda tweet: controversiality(tweet)),
        # 'sentiment' : average_sentiment(tweets),
        'related_hashtag' : most_related_hashtags(tweets),
        # 'related_user' : most_related(tweets)
    }


def most_related_hashtags(tweets):
    ''' Function takes a list of tweets (represented as dictionaries) and
    returns the hashtags that appear most frequently.

    Args:
        tweets (list of dictionaries) - tweet tweet_data

    Returns:
        [(string)] - list of 5 strings representing the 5 most related hashtags.
    '''
    occurences = {}
    for tweet in tweets:
        for hashtag in tweet['hashtags']:
            hashtag = hashtag['text'].lower()
            if hashtag in occurences:
                occurences[hashtag] += 1
            else:
                occurences[hashtag] = 1

    return occurences


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
        (float) - Number representing the controversiality of a tweet.
    '''

    return tweet['replies'] / max(tweet['favorites'] + tweet['retweets'], 1)
