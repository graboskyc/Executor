#!/bin/bash

# Trim whitespace from environment variables
REQUIREDAUTHHEADER=$(echo "$REQUIREDAUTHHEADER" | tr -d '[:space:]')
JWTOVERRIDE=$(echo "$JWTOVERRIDE" | tr -d '[:space:]')
export REQUIREDAUTHHEADER JWTOVERRIDE

# Substitute environment variables in nginx config
envsubst '${REQUIREDAUTHHEADER} ${JWTOVERRIDE}' < /etc/nginx/sites-available/default.template > /etc/nginx/sites-available/default

# Start nginx
exec nginx -g 'daemon off;'
