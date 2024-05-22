#!/bin/bash

# Default values
START_PORT=7101
NUM_PROCESSES=$1
PIDS=()

# Check if the number of processes is provided
if [ -z "$NUM_PROCESSES" ]; then
    echo "Usage: $0 <number_of_processes>"
    exit 1
fi

# Function to kill background processes
cleanup() {
    echo "Cleaning up..."
    for PID in "${PIDS[@]}"; do
        kill $PID 2>/dev/null
    done
}

# Trap SIGINT (Ctrl-C) and call cleanup
trap cleanup SIGINT

# Start the processes
for (( i=0; i<$NUM_PROCESSES; i++ ))
do
    PORT=$((START_PORT + i))
    if [ $i -lt $((NUM_PROCESSES - 1)) ]; then
        echo "Starting app_server.py on port $PORT"
        python app_server.py --port=$PORT &
        PIDS+=($!)
    else
        echo "Starting app_server.py on port $PORT"
        python app_server.py --port=$PORT
    fi
done

# Wait for the last process to finish
wait

echo "$NUM_PROCESSES instances of app_server.py have been started."
