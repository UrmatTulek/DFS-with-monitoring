#!/bin/bash

LOG_FILE="../report/checksum_log.txt"
NODES=("node-a" "node-b" "node-c")

mkdir -p "../report"
echo "DockerFS Resource Monitor started at $(date)" > "$LOG_FILE"

get_files(){
    FILES=()
    for NODE in "${NODES[@]}"; do
        STATUS=$(docker inspect --format='{{.State.Status}}' "$NODE" 2>/dev/null)
        if [ "$STATUS" == "running" ]; then
            NODE_FILES=$(docker exec "$NODE" ls /app/storage 2>/dev/null)
            for FILE in ${NODE_FILES}; do
                if [[ ! " ${FILES[*]} " =~ " ${FILE} " ]]; then
                    FILES+=("$FILE")
                fi
            done
        fi
    done
}

get_checksum(){
    NODE=$1
    FILENAME=$2
    CHECKSUM=$(docker exec "$NODE" md5sum "/app/storage/$FILENAME" 2>/dev/null | awk '{print $1}')
    echo "$CHECKSUM"
}

check_consistency(){
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP]" >> "$LOG_FILE"
    echo "Checking $1..." >> "$LOG_FILE"

    FILENAME=$1
    CHECKSUMS=()
    CHECKED_NODES=()

    for NODE in "${NODES[@]}"; do
        STATUS=$(docker inspect --format='{{.State.Status}}' "$NODE" 2>/dev/null)
        if [ "$STATUS" == "running" ]; then
            EXISTS=$(docker exec "$NODE" test -f "/app/storage/$FILENAME" 2>/dev/null; echo $?)
            if [ "$EXISTS" == "0" ]; then
                CHECKSUM=$(get_checksum "$NODE" "$FILENAME")
                CHECKSUMS+=("$CHECKSUM")
                CHECKED_NODES+=("$NODE")
                echo "  $NODE -> $CHECKSUM" >> "$LOG_FILE"
                echo "  $NODE -> $CHECKSUM"
            fi
        fi
    done

    FIRST="${CHECKSUMS[0]}"
    CONSISTENT=true

    for CHECKSUM in "${CHECKSUM[@]}"; do
        if [ "$CHECKSUM" != "$FIRST" ]; then
            CONSISTENT=false
            break
        fi
    done

    if [ "$CONSISTENT" == true ]; then
        echo " $FILENAME -- MATCHED" >> "$LOG_FILE"
        echo " $FILENAME -- MATCHED"
    else
        echo " $FILENAME -- NOT MATCHED" >> "$LOG_FILE"
        echo " $FILENAME -- NOT MATCHED"
    fi
}

echo "Starting checksum monitor (Ctrl + C to stop)"
echo "Logging to $LOG_FILE"

while true; do
    get_files

    if [ ${#FILES[@]} -eq 0 ]; then
        echo "No files were found in DFS"
    else
        echo "Checking ${#FILES[@]} files..."
        for FILE in "${FILES[@]}"; do
            check_consistency "$FILE"
        done
    fi
    sleep 10
done