#!/bin/bash
# Run cron_trigger.py every 60 seconds in background
(
  while true; do
    sleep 60
    python /usr/src/app/app/cron_trigger.py >> /var/log/cron.log 2>&1
  done
) &

# Start the main FastAPI app
exec python /usr/src/app/main.py
