#!/bin/bash

cwd=$(pwd)
docker rm --force redis
docker pull redis
docker run -d \
--name redis \
-p 6379:6379 \
-v $cwd/docker/data:/data \
-v $cwd/docker:/usr/local/etc/redis \
redis \
redis-server /usr/local/etc/redis/redis.conf

docker inspect redis -f "{{json .NetworkSettings.Networks }}"
