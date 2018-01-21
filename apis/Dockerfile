FROM python:3.6-slim

ARG KAFKA_BROKER
ARG API_NAME
ARG API_KEY

ENV KAFKA_BROKER $KAFKA_BROKER
ENV API_NAME $API_NAME
ENV API_KEY $API_KEY

COPY  . /code
WORKDIR /code

RUN pip3 install -r requirements.py

CMD ["python3", "kafka_apis.py"]