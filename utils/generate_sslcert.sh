#!/bin/bash
set -e

STORAGE=${SUPAHARRIS_STORAGE-./storage/}certbot


echo "### Creating self-signed certificate for localhost ..."
mkdir -p "${STORAGE}/conf/live/supaharris.com"  # On the Docker host
LE_PATH="/etc/letsencrypt/live/supaharris.com"  # Inside the container
docker-compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:1024 -days 1\
        -keyout '${LE_PATH}/privkey.pem' \
        -out '${LE_PATH}/fullchain.pem' \
        -subj '/CN=localhost'" certbot
echo
