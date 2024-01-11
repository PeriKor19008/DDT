#!/bin/bash

json_file="cs_to.json"

# Define the two IPs
ip1="172.19.0.2"
ip2="172.17.159.9"

# Loop through each entry in the JSON file
cat "$json_file" | jq -c '.[]' | while read -r entry; do
  # Generate a random number (0 or 1) to choose between the two IPs
  random_number=$((RANDOM % 2))
  
  # Choose the IP based on the random number
  chosen_ip=""
  if [ "$random_number" -eq 0 ]; then
    chosen_ip="$ip1"
  else
    chosen_ip="$ip2"
  fi

  # Construct the curl command
  curl_command="curl -X POST -H \"Content-Type: application/json\" -d '$entry' http://$chosen_ip:5000/insert_data"

  # Execute the curl command
  eval "$curl_command"

  # Add a newline for better readability
  echo ""
  sleep "2"
done
