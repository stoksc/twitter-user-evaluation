export FLASK_APP=twitter_user_evaluation
export FLASK_DEBUG=false
export FLASK_THREADED=false

pip3 install -e .

flask run
