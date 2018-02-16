import tweepy

def get_tweets_from_user(screen_name, api):
    '''
    '''
    pass


def get_tweets_with_hashtag(hashtag, api, count=1, lang='en'):
    ''' Receives a hashtag to query, a tweepy api object, the number of tweets
    to grab and the language. Uses this information to query twitter's api and
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
            print('had replies')
            tweet_data['replies'] = tweet.reply_count
        else:
            tweet_data['replies'] = 0

        hashtag_data.append(tweet_data)

    return hashtag_data
