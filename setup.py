from setuptools import setup

setup(
    name='twingiems',
    packages=['twingiems', 'twingiems/tools'],
    include_package_data=True,
    install_requires=[
        'flask',
        'nltk',
        'tweepy',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
