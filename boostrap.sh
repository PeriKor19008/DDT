#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

if [ "$1" -lt 3 ]; then
    echo "Error: <number> must be greater than or equal to 3"
    exit 1
fi

end=$1


for ((i=3; i<=end; i++)); do
    # url="http://172.18.0.$i:5000/bootstrap"
    # command="curl -X POST -d 'http://172.18.0.2:5000/' $url"
    url="http://172.19.0.$i:5000/bootstrap"
    command="curl -X POST -d 'http://172.19.0.2:5000/' $url"
    echo $command
    eval $command
    sleep 1
done