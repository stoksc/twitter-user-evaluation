''' reference: https://medium.com/@thoszymkowiak/how-to-implement-sentiment-analysis-using-word-embedding-and-convolutional-neural-networks-on-keras-163197aef623
'''
from __future__ import print_function

import os
import sys

import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.layers import Dense, Input, GlobalMaxPooling1D
from keras.layers import Conv1D, MaxPooling1D, Embedding, Flatten, Dropout
from keras.models import Model
from keras.models import model_from_json

from preprocess_data import get_data


BASE_DIR = ''
TRAINED_MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')
GLOVE_DIR = os.path.join(BASE_DIR, 'glove.6B')
MAX_SEQUENCE_LENGTH = 1000
MAX_NUM_WORDS = 20000
EMBEDDING_DIM = 100
VALIDATION_SPLIT = 0.2


print('gather data')
texts, labels = get_data()

print('vectorizing texts')
tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

print('prepare data')
data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
labels = to_categorical(np.asarray(labels))
print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', labels.shape)

print('test/val split')
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]
num_validation_samples = int(VALIDATION_SPLIT * data.shape[0])
# x_train = data[:-num_validation_samples]
# y_train = labels[:-num_validation_samples]
# x_val = data[-num_validation_samples:]
# y_val = labels[-num_validation_samples:]
x_train = data[:5000]
y_train = labels[:5000]
x_val = data[5000:5500]
y_val = labels[5000:5500]

print('preparing model')
sequence_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
embedded_sequences = Embedding(MAX_NUM_WORDS,
                               EMBEDDING_DIM,
                               input_length=MAX_SEQUENCE_LENGTH)(sequence_input)
x = Conv1D(128, 5, activation='relu')(embedded_sequences)
x = MaxPooling1D(5)(x)
x = Conv1D(128, 5, activation='relu')(x)
x = MaxPooling1D(5)(x)
x = Conv1D(128, 5, activation='relu')(x)
x = GlobalMaxPooling1D()(x)
x = Dense(128, activation='relu')(x)
preds = Dense(2, activation='softmax')(x)

model = Model(sequence_input, preds)
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['acc'])

print('training model')
model.fit(x_train, y_train,
          batch_size=128,
          epochs=10,
          validation_data=(x_val, y_val))

print('saving model')
model_json = model.to_json()
with open(os.path.join(TRAINED_MODELS_DIR, "conv_gmp_model.json"), "w") as f:
    f.write(model_json)
model.save_weights(os.path.join(TRAINED_MODELS_DIR, "conv_gmp_model.h5"))
