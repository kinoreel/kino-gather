FROM python:3
RUN apt-get update -y
RUN apt-get install -y gcc
ARG KAFKA_BROKER
ARG TABLE_NAME
ENV KAFKA_BROKER $KAFKA_BROKER
ENV TABLE_NAME $TABLE_NAME
COPY  . /code
WORKDIR /code
RUN pip3 install -r requirements.py
CMD ["python3", "kafka_kino_inserts.py"]