FROM python:3.7-alpine
MAINTAINER CP-finances

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./start-server.sh /start-server.sh
RUN apk add --update --no-cache postgresql-client jpeg-dev postgresql-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
    nginx vim gcc python3-dev

RUN mkdir /app

# install nginx
COPY nginx.finances /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


WORKDIR /app
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps


COPY ./app /app

# -p for subdirectories
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user

#Deployment config
EXPOSE 80
STOPSIGNAL SIGTERM  