#!/bin/bash

docker build -t slur-counter .

docker run -it --rm --name slur \
-v /opt/docker/slur/config:/config \
-v /opt/docker/slur/data:/data \
-v /opt/docker/slur/logs:/logs \
slur-counter