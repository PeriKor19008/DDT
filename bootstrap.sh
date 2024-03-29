#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <octet1>.<octet2>.<octet3> <number>"
    exit 1
fi

octets=$1
end=$2

if [ "$end" -lt 1 ]; then
    echo "Error: <number> must be greater than 1"
    exit 1
fi

IFS='.' read -r -a octet_array <<< "$octets"
octet1=${octet_array[0]}
octet2=${octet_array[1]}
octet3=${octet_array[2]}

for ((i=3; i<=end+1; i++)); do
    url="http://$octets.$i:5000/bootstrap"
    command="curl -X POST -d 'http://$octets.2:5000/' $url & wait"
    echo $command
    eval $command
    sleep 1
done


