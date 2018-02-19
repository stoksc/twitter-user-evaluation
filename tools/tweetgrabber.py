import tweepy

def get_tweets_from_user(screen_name, api, count=200):
    ''' Receives a screen name to query and a tweepy api object. Uses this
    information to return a list of dictionaries, where each dictionary
    corresponds to a tweet from the screen name.

    Args:
        screen_name (str)
        api (tweepy.api)

    Returns:
        [{tweets}]
    '''

    tweets = api.user_timeline(screen_name=screen_name, count=count)

    cleaned_tweets = []
    for tweet in tweets:
        cleaned_tweets.append(clean_tweet(tweet))
    return cleaned_tweets


def get_tweets_with_hashtag(hashtag, api, count=1, lang='en'):
    ''' Receives a hashtag to query, a tweepy api object, the number of tweets
    to grab and the language. Uses this information to query twitter's api and
    returns an array of dictionaries, where each dictionary corresponds to a
    tweet that match these criteria.

    Args:
        hashtag (str)
        api (tweepy.api)
        count (int)
        lang (str)

    Returns:
        [{tweets}]
    '''

    tweets = tweepy.Cursor(api.search,
        q="#{}".format(hashtag),
        count=count,
        lang=lang)


    cleaned_tweets = []
    for tweet in tweets.items():
        cleaned_tweets.append(clean_tweet(tweet))
        print(tweet, '\n', clean_tweet(tweet))
    return cleaned_tweets


def clean_tweet(tweet):
    ''' Takes a tweepy tweet object and returns a dictionary that contains
    the information from the tweet that we actually need.

    Args:
        tweet (tweepy.tweet)

    Returns:
        {tweet}
    '''

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

    return tweet_data
