#!/bin/sh
set -e

# Test nginx configuration
nginx -t || exit 1

# Test if service is responding
curl --fail http://localhost:80/health || exit 1

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
if [ $(echo "$MEMORY_USAGE > 90" | bc -l) -eq 1 ]; then
    exit 1
fi

exit 0
