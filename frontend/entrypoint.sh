#!/bin/sh
# Create runtime config file from environment variable
echo "{
  \"apiBaseUrl\": \"${vite-api-base-url}\"
}" > /usr/share/nginx/html/config.json

# Start Nginx
exec nginx -g "daemon off;"