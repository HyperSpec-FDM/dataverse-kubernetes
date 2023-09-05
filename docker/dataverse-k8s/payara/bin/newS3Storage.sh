#!/bin/bash

variable1=("$@")

for option in "${variable1[@]}"; do
    asadmin --user=admin --passwordfile=/secrets/asadmin/passwordFile create-jvm-options "$option"
done
