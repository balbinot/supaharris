FROM nginx:1.17-alpine

# Remove the default configuration file
RUN rm /etc/nginx/conf.d/*

# Insert our own configuration files
COPY conf/ /etc/nginx/conf.d/
COPY apps/ /etc/nginx/apps/
