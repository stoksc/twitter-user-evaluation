FROM python:3.6-slim

WORKDIR /twitter_user_evaluation

ADD . /twitter_user_evaluation

RUN pip install .

EXPOSE 80

ENV FLASK_APP twitter_user_evaluation
ENV FLASK_DEBUG false

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
