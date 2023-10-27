#!/usr/bin/env sh

KEY=!!!!enter your key here to unseal vault!!!!!

echo "Starting unsealer"
while true
do
    status=$(curl -s http://vault:8200/v1/sys/seal-status | jq '.sealed')
    if [ true = "$status" ]
    then
        echo "Unsealing"
        curl -s --request PUT --data "{\"key\": \"$KEY\"}" http://vault:8200/v1/sys/unseal
        exit 0
    fi
    sleep 10
done
