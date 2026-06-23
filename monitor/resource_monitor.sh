#!/bin/bash

LOG_FILE="../report/resource_log.txt"
INTERVAL=5
CONTAINERS=("nameserver" "node-a" "node-b" "node-c")

mkdir -p "../report"
echo "DockerFS Resource Monitor started at $(date)" > "$LOG_FILE"
echo "Monitoring containers: ${CONTAINERS[*]}" >> "$LOG_FILE"

echo "Starting resource monitor (Ctrl+C to stop)..."
echo "Logging to $LOG_FILE"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP]" >> "$LOG_FILE"

    for CONTAINER in "${CONTAINERS[@]}"; do
        STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER" 2>/dev/null)

        if [ "$STATUS" == "running" ]; then
            STATS=$(docker stats --no-stream --format \
                "CPU={{.CPUPerc}} MEM={{.MemUsage}} MEM_PERC={{.MemPerc}}" \
                "$CONTAINER")
            echo "  $CONTAINER | $STATS" >> "$LOG_FILE"
            echo "  $CONTAINER | $STATS"
        else
            echo "  $CONTAINER | STATUS=down" >> "$LOG_FILE"
            echo "  $CONTAINER | STATUS=down"
        fi
    done

    sleep "$INTERVAL"
done