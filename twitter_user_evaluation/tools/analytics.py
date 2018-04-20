''' This module provides functions for analyzing tweets.
'''
from typing import List
import operator

from gensim.models import Doc2Vec
from gensim.models import Word2Vec
from gensim.models.doc2vec import TaggedDocument
import nltk
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tag import pos_tag
import numpy as np
from rake_nltk import Rake
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

from .retrieval import Tweet


TOKENIZER = RegexpTokenizer(r'\w+')
STOPWORD_SET = set(stopwords.words('english'))

nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')

HSL1 = "hsl(280, 70%, 50%)"
HSL2 = "hsl(15, 70%, 50%, 1)"
HSL3 = "hsl(175, 70%, 50%, 1)"
INTERVALS = 15
MODEL = SentimentIntensityAnalyzer()
RAKE = Rake()


def analyze_tweets(tweets: List[Tweet]):
    ''' This function takes a group of tweets and returns statistics
    on them like average sentiment and related hashtags.
    '''
    return {
        'most_popular_tweet': max(tweets, key=popularity),
        'most_controversial_tweet': max(tweets, key=controversiality),
        'related_hashtag': related_hashtags(tweets),
        'related_user': related_users(tweets),
        'volume_line_graph': volume_by_interval(tweets, INTERVALS),
        'radar_graph': sentiment_totals(tweets),
        'stream_graph': keywords_by_interval(tweets, INTERVALS),
        'scatter_graph': generate_tsne_visualized_word_embedding(tweets),
        # 'scatter_graph2': generate_tsne_visualized_doc_embedding(tweets),
        'word_occurence_pie_graph': all_word_occurences(tweets),
    }


def related_hashtags(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the hashtags that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    hashtag_occurences = {}
    for tweet in tweets:
        for hashtag in tweet.hashtag_mentions:
            if hashtag in hashtag_occurences:
                hashtag_occurences[hashtag][0] += 1
                hashtag_occurences[hashtag][1].append(tweet.tweet_id)
            else:
                hashtag_occurences[hashtag] = [1, [tweet.tweet_id]]
    return [{
        'id': hashtag,
        'label': hashtag,
        'value': occurences,
        'color': HSL1,
        'tweet_ids': ids,
        } for hashtag, (occurences, ids) in hashtag_occurences.items()]


def related_users(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the users that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    user_occurences = {}
    for tweet in tweets:
        for screen_name in tweet.user_mentions:
            if screen_name in user_occurences:
                user_occurences[screen_name][0] += 1
                user_occurences[screen_name][1].append(tweet.tweet_id)
            else:
                user_occurences[screen_name] = [1, [tweet.tweet_id]]
    return [{
        'id': user,
        'label': user,
        'value': occurences,
        'color': HSL1,
        'tweet_ids': ids,
        } for user, (occurences, ids) in user_occurences.items()]


def sentiment_totals(tweets: List[Tweet]):
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


def popularity(tweet: Tweet):
    ''' Function takes a tweet and returns how popular the tweet is.
    '''
    return tweet.favorites + tweet.retweets


def controversiality(tweet: Tweet):
    ''' Function takes a tweet and returns how controversial a tweet is.
    '''
    return MODEL.polarity_scores(tweet.cleaned_text)['neg']


def volume_by_interval(tweets: List[Tweet], intervals: int):
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
        'data': [],
    }
    retweets_by_interval = {
        'id': 'Retweets',
        'color': HSL2,
        'data': [],
    }
    totals_by_interval = {
        'id': 'Totals',
        'color': HSL3,
        'data': [],
    }
    tweets.sort(key=lambda tweet: tweet.time)
    interval_length = (tweets[-1].time - tweets[0].time) / intervals
    current_interval = tweets[0].time + interval_length
    current_favorites_tally = current_retweets_tally = 0
    for tweet in tweets:
        if tweet.time > current_interval:
            favorites_by_interval['data'].append({
                'color': HSL1,
                'x': str(current_interval - (interval_length / 2)),
                'y': current_favorites_tally,
            })
            retweets_by_interval['data'].append({
                'color': HSL2,
                'x': str(current_interval - (interval_length / 2)),
                'y': current_favorites_tally,
            })
            totals_by_interval['data'].append({
                'color': HSL3,
                'x': str(current_interval - (interval_length / 2)),
                'y': current_favorites_tally,
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


def keywords_by_interval(tweets: List[Tweet], intervals: int):
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
        keywords = [word for word, pos in pos_tag(tweet.cleaned_text.split())
                    if pos == 'NNP']
        for keyword in keywords:
            for tracked_keyword in keywords_to_track:
                if is_similar(keyword, tracked_keyword):
                    current_interval_keywords[tracked_keyword] += 1
                    break
    return all_keywords_by_interval


def highest_keywords(tweets: List[Tweet], number_of_keywords=6):
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


def is_similar(str1: str, str2: str):
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


def generate_tsne_visualized_word_embedding(tweets: List[Tweet]):
    ''' This function takes tweets and generates a word embedding from these
    tweets. After this, it uses t-SNE to generate a visualization of the word
    embedding to be displayed by this React component:
        http://nivo.rocks/#/scatterplot/
    '''
    sentences = [tweet.cleaned_text.split() for tweet in tweets]
    model = Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
    vocab = {}
    for word in model.wv.vocab:
        vocab[word] = model[word]
    tsne_model = TSNE(perplexity=40,
                      n_components=2,
                      init='pca',
                      n_iter=2500,
                      random_state=23)
    tsne_values = tsne_model.fit_transform([x for x in vocab.values()])
    scale = max(max(tsne_values, key=lambda x: max(x)))
    return [{
        'id': label,
        'data': [{
            'id': index,
            'x': int(scale * np.float64(value[0])),
            'y': int(scale * np.float64(value[1])),
        }]} for index, (label, value) in enumerate(zip(vocab.keys(),
                                                       tsne_values))]


def generate_tsne_visualized_doc_embedding(tweets: List[Tweet]):
    ''' This function takes tweets and generates a doc2vec embedding from these
    tweets. After this, it uses t-SNE to generate a visualization of the word
    embedding to be displayed by this React component:
        http://nivo.rocks/#/scatterplot/
    '''
    # preprocess data and train model
    print('preprocess')
    it = LabeledLineSentence({
        tweet.time: tweet.cleaned_text for tweet in tweets
    })
    model = Doc2Vec(vector_size=125,
                    min_count=0,
                    alpha=0.025,
                    min_alpha=0.025)
    model.build_vocab(it)
    for epoch in range(10):
        print('iteration ' + str(epoch+1), end=' ')
        model.train(it, total_examples=model.corpus_count, epochs=model.epochs)
        model.alpha -= 0.002
        model.min_alpha = model.alpha

    # make 2d visualization
    print('2d visualization')
    tsne_model = TSNE(perplexity=40,
                      n_components=2,
                      init='pca',
                      n_iter=100,
                      random_state=23)
    tsne_values = tsne_model.fit_transform(model.docvecs)

    # find clusters
    print('clustering')
    scores = []
    inertia_list = np.empty(8)
    for i in range(2, 8):
        kmeans = KMeans(n_clusters=i)
        kmeans.fit(tsne_values)
        inertia_list[i] = kmeans.inertia_
        scores.append(silhouette_score(tsne_values, kmeans.labels_))
    clusterer = KMeans(n_clusters=max(scores),
                       random_state=50).fit(tsne_values)
    centers = clusterer.cluster_centers_
    c_preds = clusterer.predict(tsne_values)

    # make chart
    print('make chart')
    scatter_chart = [{
        'id': str(i),
        'data': [],
        } for i in range(len(centers))]
    scale = max(max(tsne_values, key=lambda x: max(x)))
    for tweet, tsne_value, group in zip(tweets, tsne_values, c_preds):
        scatter_chart[str(group)]['data'].append({
            'id': tweet.raw_text,
            'x': int(scale * np.float64(tsne_value[0])),
            'y': int(scale * np.float64(tsne_value[1])),
        })
    scatter_chart.append([{
        'id': 'center',
        'data': [{
            'id': str(ci),
            'x': int(scale * c[1]),
            'y': int(scale * c[0]),
        } for ci, c in enumerate(centers)]}])
    return scatter_chart


class LabeledLineSentence(object):
    ''' This class is defined to take a dictionary of {text_title: text} and
    yields TaggedDocuments for gensim.models.Doc2Vec to consume and train on.
    '''
    def __init__(self, corpus):
        self.corpus = corpus

    def __iter__(self):
        for key, doc in self.corpus.items():
            yield TaggedDocument(words=doc, tags=[key])

    @staticmethod
    def nlp_clean(data: List[str]):
        ''' This method takes a list of texts and returns a list of lists of
        tokens.
        '''
        tokenized_texts = []
        for text in data:
            new_str = text.lower()
            tokenized_text = TOKENIZER.tokenize(new_str)
            tokenized_text = list(set(tokenized_text).difference(STOPWORD_SET))
            tokenized_texts.append(tokenized_text)
        return tokenized_texts


def all_word_occurences(tweets: List[Tweet]):
    ''' Function takes a list of tweets and returns the hashtags that appear.

    What it returns is a list of dictionaries that, when jsonified, renders as
    this React comonent:
        http://nivo.rocks/#/pie
    '''
    word_occurences = {}
    for tweet in tweets:
        cleaned_text = LabeledLineSentence.nlp_clean([tweet.raw_text])[0]
        for word in cleaned_text:
            if word in word_occurences:
                word_occurences[word][0] += 1
                word_occurences[word][1].append(tweet.tweet_id)
            else:
                word_occurences[word] = [1, [tweet.tweet_id]]
    return [{
        'id': word,
        'label': word,
        'value': occurences,
        'color': HSL1,
        'tweet_ids': ids,
        } for word, (occurences, ids) in word_occurences.items()]
