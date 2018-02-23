FROM python:3.6-slim

WORKDIR /twingiems

ADD . /twingiems

RUN pip install .

EXPOSE 80

ENV FLASK_APP twingiems
ENV FLASK_DEBUG false

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
