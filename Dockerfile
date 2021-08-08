FROM python:3.7-alpine
MAINTAINER Milos Acimovac

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev

RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN apk add --update --no-cache g++ gcc libxml2 libxslt-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
COPY ./app /app
WORKDIR /app

RUN chmod -R 777 /app
RUN chmod -R 777 /app/logs