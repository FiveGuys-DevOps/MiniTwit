#!/bin/bash

template_file='tools/scripts/load_balancer_template.conf'
output_file='tools/tmp/load_balancer.conf'

rm $output_file &>/dev/null
cp $template_file $output_file

rows=$(terraform output -raw minitwit-swarm-leader-ip-address)
rows+=' '
rows+=$(terraform output -json minitwit-swarm-manager-ip-address | jq -r .[])
rows+=' '
rows+=$(terraform output -json minitwit-swarm-worker-ip-address | jq -r .[])

for ip in $rows; do
    sed -i "/upstream backend {/a server $ip:8080;" $output_file
done