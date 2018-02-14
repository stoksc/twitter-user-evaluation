import tweepy


def most_popular(tweets):
    ''' Function takes an array of dictionaries, each dictionary representing a
    tweet and some information about it. Returns the text of the most popular
    tweet.

    Args:
        tweets (list) - List of tweets represented by dictionaries.

    Returns:
        (str) - Text of the most popular tweet.
    '''

    most_popular = float('-inf')

    for tweet in tweets:
        tweet_popularity = popularity(tweet)
        if tweet_popularity > most_popular:
            most_popular_tweet = tweet
            most_popular = tweet_popularity

    return {
        'text' : most_popular_tweet['text'],
        'popularity' : most_popular,
    }


def popularity(tweet):
    ''' Function takes a tweet and returns how popular the tweet was.

    Args:
        tweet (dictionary) - A dictionary of the stats on a tweet.

    Returns:
        (int) - Number representing the popularity of a tweet.
    '''

    return tweet['favorites'] + tweet['retweets']


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
            tweet_data['replies'] = tweet.reply_count
        else:
            tweet_data['replies'] = 0

        hashtag_data.append(tweet_data)

    return hashtag_data
