''' Mostly taken from: http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
'''
import os
import pickle

from preprocess_data import get_data
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

VALIDATION_SPLIT = 0.2
TRAINED_MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')

print('gather data and train-val split')
texts, labels = get_data(clean_stopwords=True, lemmatize=True)
num_validation_samples = int(VALIDATION_SPLIT * len(texts))
x_train = texts[:-num_validation_samples]
y_train = labels[:-num_validation_samples]
x_val = texts[-num_validation_samples:]
y_val = labels[-num_validation_samples:]

print('prepare MultinomialNB')
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(x_train)
tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

print('train MultinomialNB')
clf = MultinomialNB().fit(X_train_tfidf, y_train)

print('validate MultinomialNB')
X_new_counts = count_vect.transform(x_val)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
y_pred = clf.score(X_new_tfidf, y_val)
print(y_pred)

print('save model')
pickle.dump(clf, open(os.path.join(TRAINED_MODELS_DIR,
                                   'MultinomialNB.pickle'), 'wb'))
