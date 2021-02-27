FROM python:3.6-alpine

COPY  . /code
WORKDIR /code

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements-api.txt --no-cache-dir && \
 apk --purge del .build-deps

CMD ["python3", "./gather_api.py"]