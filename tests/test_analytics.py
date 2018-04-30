''' This module provides unit testing for the analytics module.
'''
import json
import pickle
import pytest
import os

from jsonschema import FormatChecker, validate
import twitter_user_evaluation
from twitter_user_evaluation.tools.analytics import analyze_tweets


DATA_DIR = os.path.join(os.getcwd(), 'tests', 'test_data')
SCHEMA_DIR = os.path.join(os.getcwd(), 'tests', 'react_chart_schemas')
SCHEMA_FILES = {
    'scatter_graph': 'scatter_schema.json',
    'volume_line_graph': 'line_schema.json',
    'related_hashtag': 'pie_schema.json',
    'related_user': 'pie_schema.json',
    'named_entity_bar_graph': 'bar_schema.json',
}


def test_chart_schemas():
    ''' Tests the API's response against the schema to be expected by the
    matching React component
    '''
    for data_file in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, data_file), 'rb') as f:
            charts = analyze_tweets(pickle.load(f))
        for chart, schema_file in SCHEMA_FILES.items():
            with open(os.path.join(SCHEMA_DIR, schema_file)) as f:
                chart_schema = json.load(f)
                validate(charts[chart],
                         chart_schema,
                         format_checker=FormatChecker())
