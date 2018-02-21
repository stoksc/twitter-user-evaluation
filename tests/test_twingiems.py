''' This module provides integration testing for the app.
'''
import pytest

import twingiems


@pytest.fixture
def app():
    yield twingiems.app


@pytest.fixture
def client(app):
    return app.test_client()


def test_user(client):
    client.get('/?user=realdonaldtrump',
               follow_redirects=True)


def test_hashtag(client):
    client.get('/?hashtag=spacex',
               follow_redirects=True)
