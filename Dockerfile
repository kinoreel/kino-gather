FROM python:3.6-slim
RUN apt-get update -y
RUN apt-get install -y gcc libpq-dev
ARG KAFKA_BROKER=localhost:9092
ARG API_NAME=omdb
ARG API_KEY=sorry
ENV KAFKA_BROKER ${KAFKA_BROKER}
ENV API_NAME ${API_NAME}
ENV API_KEY ${API_KEY}
COPY  /py/* /code
COPY requirements.py /code
WORKDIR /code
RUN pip3 install -r requirements.txt
CMD ["python3 kafka_handler.py"]