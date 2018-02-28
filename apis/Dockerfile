FROM python:3.6-slim

COPY  . /code
WORKDIR /code

RUN pip3 install -r requirements.py

CMD ["python3", "kafka_actor.py"]