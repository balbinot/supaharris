FROM nginx:1.17-alpine

LABEL maintainer="Timo Halbesma <Halbesma@MPA-Garching.MPG.DE>"

# Remove the default configuration files
RUN set -ex \
    && apk add --no-cache curl bash htop \
    && rm /etc/nginx/conf.d/*

# Insert our own configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf/ /etc/nginx/conf.d/
COPY apps/ /etc/nginx/apps/

# HEALTHCHECK --interval=2m --timeout=3s \
#     CMD curl -I -k --fail -H "Host: supaharris.com" -k https://localhost || exit 1
