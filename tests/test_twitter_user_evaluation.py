''' This module provides integration testing for the app.
'''
import pytest

import twitter_user_evaluation


USERS_WITH_TWEETS = [
    'realdonaldtrump',
    'gvanrossum',
]

USER_WITHOUT_TWEETS = 'stoked_'

USER_ROUTE = '/?user={}'
BAD_ROUTE = '/badroute'
BAD_REQUEST = '/?badrequest=something'

OK_RESPONSE = '200 OK'
BAD_RESPONSE = '400 BAD REQUEST'
BAD_ROUTE = '404 NOT FOUND'


@pytest.fixture
def app():
    ''' Generates our flask app.
    '''
    yield twitter_user_evaluation.app


@pytest.fixture
def client(app):
    ''' Return a test client.
    '''
    return app.test_client()


def test_user_request(client):
    ''' Tests the API with user requests.
    '''
    for user in USERS_WITH_TWEETS:
        response = client.get(USER_ROUTE.format(user),
                              follow_redirects=True)
        assert response.status == OK_RESPONSE


def test_bad_route(client):
    ''' Tests the API's response given a bad route.
    '''
    response = client.get(BAD_ROUTE,
                         follow_redirects=True)
    assert response.status == BAD_ROUTE


def test_bad_request(client):
    ''' Tests the API's response given a bad request argument.
    '''
    response = client.get(BAD_REQUEST,
                         follow_redirects=True)
    assert response.status == BAD_RESPONSE


def test_bad_query(client):
    ''' Tests the API's response given a null query request.
    '''
    response = client.get(USER_ROUTE.format(USER_WITHOUT_TWEETS))
    assert response.status == BAD_RESPONSE
