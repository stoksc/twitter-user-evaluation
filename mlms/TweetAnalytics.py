import tweepy


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


def get_tweets_with_hashtag(hashtag, api, count, lang):
    ''' Receives a hashtag to query, a tweepy api object, the number of tweets to
    grab and the language. Uses this information to query twitter's api and
    return an array of tuples (created_at, text) corresponding to tweets that
    match these criteria.
    '''

    tweets = tweepy.Cursor(api.search,
        q="#{}".format(hashtag),
        count=count,
        lang=lang)

    hashtag_data = []
    for tweet in tweets.items():
        print(tweet, "\n\n")
        tweet_data = {
            'user' : tweet.user.screen_name,
            'time' : tweet.created_at,
            'text' : tweet.text,
            'timezone' : tweet.user.time_zone,
            'hashtags' : tweet.entities['hashtags'],
        }

        if hasattr(tweet, 'favorite_count'):
            tweet_data['favorites'] = tweet.favorite_count
        else:
            tweet_data['favorites'] = 0

        if hasattr(tweet, 'retweet_count'):
            tweet_data['retweets'] = tweet.retweet_count
        else:
            tweet_data['retweets'] = 0

        if hasattr(tweet, 'reply_count'):
            print('had replies')
            tweet_data['replies'] = tweet.reply_count
        else:
            tweet_data['replies'] = 0

        hashtag_data.append(tweet_data)

    return hashtag_data
