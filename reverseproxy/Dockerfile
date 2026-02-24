FROM ubuntu:focal

RUN apt update && apt install -y nginx gettext-base

# Copy nginx config as template (will be processed at runtime)
COPY ./default /etc/nginx/sites-available/default.template

# Copy entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]