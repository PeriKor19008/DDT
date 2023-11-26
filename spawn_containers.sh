#!/bin/bash

# Check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num_containers> <start_port>"
    exit 1
fi

# Get command-line arguments
num_containers=$1
start_port=$2

# Set the name of your Docker image
image_name="app"

# Calculate the end port based on the number of containers
end_port=$((start_port + num_containers - 1))

# Loop to create containers with different ports
for ((port=start_port; port<=end_port; port++)); do
    docker run -d -p $port:5000 $image_name
done

echo "$num_containers containers created on ports $start_port to $end_port."