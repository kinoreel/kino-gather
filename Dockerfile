FROM python:3.6-slim
RUN apt-get update -y
RUN apt-get install -y gcc libpq-dev
COPY  /py/* /code
COPY requirements.py /code
WORKDIR /code
RUN pip3 install -r requirements.txt
CMD ["python3 kafka_handler.py"]