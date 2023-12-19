#!/bin/bash

if [ "$#" -gt 2 ]; then
  echo "Too many arguments provided.
Arguments: num_images(int) build(string) | build(string) | No arguments"
  exit 1
fi

filename="docker-compose.yml"

sudo service docker start

if [ "$#" -eq 0 ]; then
  if [ -s "$filename" ]; then
    sudo docker-compose up --remove-orphans
  else
    echo "Error: docker-compose.yml is empty or it doesn't exist"
    exit 1
  fi
fi

if [ -n "$1" ]; then
  if [[ "$1" =~ ^[0-9]+$ ]]; then
    
    if [ -e "$filename" ]; then
      rm "$filename"
      echo "Remove previous docker-compose.yml"
    fi
    touch "$filename"
    if [ -n "$filename" ]; then
      echo "Created new docker-compose.yml"
    fi

    echo "version: '3'" >> "$filename"
    echo "services:" >> "$filename"

    # Loop to generate images
    for ((i=1; i<=$1; i++)); do
      echo "  myapp$i:" >> "$filename"
      echo "    image: app" >> "$filename"
      echo "    networks:" >> "$filename"
      echo "      - mynetwork" >> "$filename"
    done

    echo "networks:" >> "$filename"
    echo "  mynetwork:" >> "$filename"

    if [ "$#" -eq 1 ]; then
      sudo docker-compose up --remove-orphans
    fi

  elif [[ "$1" == "build" && "$#" -eq 1 ]]; then
    sudo docker build -t app .
    sudo docker-compose up --remove-orphans
  else
    echo "Incorrect arguments: num_images(int) build | build | No arguments"
    exit 1
  fi
fi

if [ -n "$2" ]; then
  if [ "$2" == "build" ]; then
    sudo docker build -t app .
    sudo docker-compose up --remove-orphans
  else
    echo "Incorrect arguments: num_images(int) build | build | No arguments"
    exit 1
  fi
fi




