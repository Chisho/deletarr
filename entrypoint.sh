#!/bin/sh

CONFIG_FILE="/config/config.yml"
LOG_FILE="/var/log/deletarr_cron.log"
CRON_SCHEDULE="0 0 * * *" # Default: daily at midnight

# Try to extract schedule from config.yml if present
echo "Checking for config at $CONFIG_FILE"
if [ -f "$CONFIG_FILE" ]; then
    SCHEDULE_LINE=$(grep '^schedule:' "$CONFIG_FILE" | head -n1)
    if [ -n "$SCHEDULE_LINE" ]; then
        # Extract the full cron expression after 'schedule:'
        CRON_SCHEDULE=$(echo "$SCHEDULE_LINE" | sed -E 's/schedule:[[:space:]]*"?([^"\r\n]*)"?/\1/')
    fi
fi

echo "Running deletarr once at startup..."
deletarr run

echo "Using cron schedule: $CRON_SCHEDULE"
echo "$CRON_SCHEDULE deletarr run >> $LOG_FILE 2>&1" > /etc/cron.d/deletarr
chmod 0644 /etc/cron.d/deletarr
crontab /etc/cron.d/deletarr

# Start cron in the background
cron

# Keep container running and show log
touch $LOG_FILE
tail -f $LOG_FILE
