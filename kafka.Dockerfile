FROM python:3.6-slim

COPY  . /code
WORKDIR /code

RUN pip3 install -r requirements.txt

CMD ["python3", "kafka_actor.py"]