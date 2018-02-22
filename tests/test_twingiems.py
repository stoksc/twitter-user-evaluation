''' This module provides integration testing for the app.
'''
import pytest

import twingiems

USERS = [
    'realdonaldtrump',
    'stoked_',
    'gvanrossum',
]

HASHTAGS = [
    'metoo',
    'dumptrump',
    'notahashtagthatanyoneuseskkk',
]


@pytest.fixture
def app():
    ''' Generates our flask app.
    '''
    yield twingiems.app


@pytest.fixture
def client(app):
    ''' Return a test client.
    '''
    return app.test_client()


def test_user_request(client):
    ''' Tests the API with user requests.
    '''
    for user in USERS:
        client.get('/?user=%s' % user,
                   follow_redirects=True)


def test_hashtag_request(client):
    ''' Tests the API with hashtag requests.
    '''
    for hashtag in HASHTAGS:
        client.get('/?hashtag=%s' % hashtag,
                   follow_redirects=True)


def test_bad_route(client):
    ''' Tests the API's response given a bad route.
    '''
    client.get('/badthing',
               follow_redirects=True)


def test_bad_request(client):
    ''' Tests the API's response given a bad request argument.
    '''
    client.get('/?badrequest=ok',
               follow_redirects=True)
