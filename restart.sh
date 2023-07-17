#!/bin/bash

cp -r /scu/*.json /root/sentences/sentences/
sleep 2
redis-cli -a "your redis passwd" --no-auth-warning flushall
pm2 restart 0 # pm2中语录系统的id，一般是固定的，也可直接写name
time=$(date "+%Y%m%d-%H:%M:%S")
echo "${time}"
