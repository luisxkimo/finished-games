FROM python:3.7.1

LABEL title "Finished-Games"
LABEL maintainer "Diego / Kartones"
LABEL url "https://kartones.net"
LABEL twitter "@kartones"

# Define environment vars to expose to container here
# ENV <key> <value>

# Env vars sent from docker-compose or docker build
ARG uid=1000
ARG gid=1000

RUN getent group $gid || groupadd --gid $gid finished-games
RUN getent passwd $uid || useradd -m -u $uid -g $gid finished-games

RUN chown -R $uid:$gid /usr/local

USER $uid

COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
