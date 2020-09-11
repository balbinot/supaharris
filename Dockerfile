FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1

LABEL maintainer="Timo Halbesma <timo@halbesma.com>"

# Install system packages
WORKDIR /supaharris
RUN set -ex \
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
RUN set -ex && \
    pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /supaharris/requirements.txt \
\
    # Because pygraphviz has to be installed with additional flags
    && pip install --install-option="--include-path=/usr/local/include/" \
        --install-option="--library-path=/usr/local/lib/" pygraphviz

# NB, we link the repo at runtime (which 'overwrites' files copied in on build)
# But production (when we run from image without linking the repo in) does use
# the files copied in!
COPY . /supaharris
COPY tlrh/ /supaharris
RUN chown -R supaharris:supaharris /supaharris

USER supaharris

ENTRYPOINT ["/supaharris/entrypoint.sh"]
