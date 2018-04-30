from setuptools import setup

setup(
    name='twitter_user_evaluation',
    packages=['twitter_user_evaluation', 'twitter_user_evaluation/tools'],
    include_package_data=True,
    install_requires=[
        'tensorflow',
        'flask',
        'keras',
        'nltk',
        'tweepy',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'jsonschema',
    ],
)
