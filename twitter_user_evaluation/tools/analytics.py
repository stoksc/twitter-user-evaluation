''' This module provides functions for analyzing tweets.
'''
import operator

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tag import pos_tag

from .retrieval import Tweet


nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')

HSL1 = "hsl(280, 70%, 50%)"
HSL2 = "hsl(15, 70%, 50%, 1)"
HSL3 = "hsl(175, 70%, 50%, 1)"
INTERVALS = 60
MODEL = SentimentIntensityAnalyzer()


def analyze_tweets(tweets: [Tweet]) -> dict:
    ''' This function takes a group of tweets and returns statistics
    on them like average sentiment and related hashtags
    '''
    return {
        'most_popular_tweet' : max(tweets, key=popularity),
        'most_controversial_tweet' : max(tweets, key=controversiality),
        'related_hashtag' : related_hashtags(tweets),
        'related_user' : related_users(tweets),
        'volume_line_graph': volume_by_interval(tweets, INTERVALS),
        'radar_graph': sentiment_totals(tweets),
        'stream_graph': keywords_by_interval(tweets, INTERVALS),
    }


def related_hashtags(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the hashtags that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    hashtag_occurences = {}
    for tweet in tweets:
        for hashtag in tweet.hashtag_mentions:
            if hashtag in hashtag_occurences:
                hashtag_occurences[hashtag] += 1
            else:
                hashtag_occurences[hashtag] = 1

    return [{
        'id' : hashtag,
        'label' : hashtag,
        'value' : occurences,
        'color' : HSL1} for hashtag, occurences in hashtag_occurences.items()]


def related_users(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the users that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    user_occurences = {}
    for tweet in tweets:
        for screen_name in tweet.user_mentions:
            if screen_name in user_occurences:
                user_occurences[screen_name] += 1
            else:
                user_occurences[screen_name] = 1

    return  [{
        'id' : user,
        'label' : user,
        'value' : occurences,
        'color' : HSL1} for user, occurences in user_occurences.items()]


def sentiment_totals(tweets: [Tweet]) -> dict:
    ''' Function takes a list of tweets and returns the average qualities about
    them using NLTK SentimentIntensityAnalyzer.

    Returns a format that, when jsonified, it renderable by this react
    component:
        http://nivo.rocks/#/radar
    '''
    compound_total = neg_total = pos_total = neu_total = 0
    for tweet in tweets:
        compound_total += MODEL.polarity_scores(tweet.cleaned_text)['compound']
        neg_total += MODEL.polarity_scores(tweet.cleaned_text)['neg']
        pos_total += MODEL.polarity_scores(tweet.cleaned_text)['pos']
        neu_total += MODEL.polarity_scores(tweet.cleaned_text)['neu']
    return [
        {
            "type": "compound",
            "sentiment": (compound_total / len(tweets)),
        },
        {
            "type": "negative",
            "sentiment": (neg_total / len(tweets)),
        },
        {
            "type": "positive",
            "sentiment": (pos_total / len(tweets)),
        },
        {
            "type": "neutral",
            "sentiment": (neu_total / len(tweets)),
        },
    ]


def popularity(tweet: Tweet) -> int:
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def controversiality(tweet: Tweet) -> float:
    ''' Function takes a tweet and returns how controversial a tweet is.
    '''
    return MODEL.polarity_scores(tweet.cleaned_text)['neg']


def volume_by_interval(tweets: [Tweet], intervals: int) -> [dict]:
    ''' This function takes a list of tweets and locates the newest and oldest
    tweets in the bunch. It then breaks the length of time between these into
    intervals and returns the average sentiment of tweets per interval.

    What it returns is a dictionary that, when jsonified renders this React
    component.
     http://nivo.rocks/#/line
    '''
    favorites_by_interval = {
        'id': 'Favorites',
        'color': HSL1,
        'data': []
    }
    retweets_by_interval = {
        'id': 'Retweets',
        'color': HSL2,
        'data': []
    }
    totals_by_interval = {
        'id': 'Totals',
        'color': HSL3,
        'data': []
    }
    tweets.sort(key=lambda tweet: tweet.time)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_favorites_tally = current_retweets_tally = 0
    for tweet in tweets:
        if tweet.time > current_interval:
            favorites_by_interval['data'].append({
                'color': HSL1,
                'x': (current_interval - (interval_length / 2)),
                'y': current_favorites_tally,
            })
            retweets_by_interval['data'].append({
                'color': HSL2,
                'x': (current_interval - (interval_length / 2)),
                'y': current_retweets_tally,
            })
            totals_by_interval['data'].append({
                'color': HSL3,
                'x': (current_interval - (interval_length / 2)),
                'y': (current_favorites_tally + current_retweets_tally),
            })
            current_interval += interval_length
            current_favorites_tally = current_retweets_tally = 0
        current_favorites_tally += tweet.favorites
        current_retweets_tally += tweet.retweets
    return [
        favorites_by_interval,
        retweets_by_interval,
        totals_by_interval,
    ]


def keywords_by_interval(tweets: [Tweet], intervals: int) -> [dict]:
    ''' This function takes a tweets, groups the tweets by intervals of time,
    extracts the keywords from the text and stores the keywords that occured
    in each interval.

    It returns is a dictionary that, when jsonified renders this:
     http://nivo.rocks/#/stream
    React component.
    '''
    all_keywords_by_interval = []
    keywords_to_track = highest_keywords(tweets)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_interval_keywords = {keyword: 0 for keyword in keywords_to_track}
    for tweet in tweets:
        if tweet.time > current_interval:
            all_keywords_by_interval.append(current_interval_keywords)
            current_interval += interval_length
            current_interval_keywords = {
                keyword: 0 for keyword in keywords_to_track}
        keywords = [word for word, pos in pos_tag(tweet.cleaned_text.split()) \
                 if pos == 'NNP']
        for keyword in keywords:
            for tracked_keyword in keywords_to_track:
                if is_similar(keyword, tracked_keyword):
                    current_interval_keywords[tracked_keyword] += 1
                    break
    return all_keywords_by_interval


def highest_keywords(tweets: [Tweet], number_of_keywords=25) -> dict:
    ''' This function takes a tweets, rake them for keywords and determines the
    n strongest keywords from this document. pos=part of speech
    '''
    pos_tag_sents = [pos_tag(tweet.cleaned_text.split()) for tweet in tweets]
    keywords = {}
    for tagged_sentence in pos_tag_sents:
        for word, pos in tagged_sentence:
            if pos != 'NNP':
                continue
            if word.lower() in keywords:
                keywords[word.lower()] += 1
            else:
                keywords[word.lower()] = 1
    top_keywords = sorted(
        keywords.items(),
        key=operator.itemgetter(1))[-number_of_keywords:]
    return [word for word, score in top_keywords]


def is_similar(str1: str, str2: str) -> bool:
    ''' This function takes two strings and determines if they are similar by
    laying them over each other and counting pairwise matches. Probably slow,
    but only used on small strings. Strings are considered similar if in some
    orientation, they match at atleast len(longer_string) / 2 places.
    '''
    short_string, long_string = sorted([str1, str2], key=len)
    iterations = (len(long_string) - len(short_string))
    best_matches = 0
    for _ in range(iterations):
        matches = 0
        for char1, char2 in zip(long_string, short_string):
            if char1 == char2:
                matches += 1
        best_matches = matches if matches > best_matches else best_matches
        long_string = long_string[1:]
    if best_matches > (len(long_string) / 2):
        return True
    return False
