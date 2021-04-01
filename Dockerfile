# syntax = docker/dockerfile:experimental
FROM python:3.9-slim-buster
ENV PYTHONUNBUFFERED 1

LABEL maintainer="Timo Halbesma <timo@halbesma.com>"

# Install system packages
WORKDIR /supaharris
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,mode=0755,target=/var/cache/apt --mount=type=cache,mode=0755,target=/var/lib/apt set -ex \
    && apt-get update \
\
    # Install Build/Runtime dependencies ...
    && apt-get install -y --no-install-recommends \
\
        # ... a compiler (build)
        build-essential gcc \
        # ... for a proper editor (runtime)
        vim \
        # ... for the healthcheck (runtime)
        curl \
        # ... for monitoring (runtime)
        htop \
        # ... for Django translations (runtime)
        gettext \
        # ... for 'graph_models' (django-extensions) cmd to visualise db schema (runtime)
        graphviz graphviz-dev \
        # ... for internal routing of uWSGI (runtime)
        libpcre3 libpcre3-dev \
        # ... for communication with the database (runtime)
        mariadb-client libmariadb-dev-compat \
\
    # Create supaharris user to run uWSGI as non-root
    && groupadd -g 1000 supaharris \
    && useradd -r -u 1000 -g supaharris supaharris -s /bin/bash -d /supaharris

# Install python packages for Django
COPY requirements.txt /supaharris/requirements.txt
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip set -ex && \
    pip install --upgrade pip \
    && pip install --upgrade pip \
    && pip install -r /supaharris/requirements.txt

# NB, we link the repo at runtime (which 'overwrites' files copied in on build)
# But production (when we run from image without linking the repo in) does use
# the files copied in!
COPY . /supaharris
COPY tlrh/ /supaharris
RUN chown -R supaharris:supaharris /supaharris

USER supaharris

ENTRYPOINT ["/supaharris/entrypoint.sh"]
