#!/bin/bash

json_file="cs_to.json"

cat "$json_file" | jq -c '.[]' | while read -r entry; do

  curl_command="curl -X POST -H \"Content-Type: application/json\" -d '$entry' http://172.19.0.2:5000/insert_data"

  eval "$curl_command"
  echo "$curl_command"
  sleep 1
done
