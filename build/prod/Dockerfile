FROM finished-games:base

ARG uid=1000
ARG gid=1000

# USER root

USER $uid

VOLUME /code
WORKDIR /code/finishedgames

# generate the statics
# WORKDIR /code
# RUN python manage.py collectstatic
