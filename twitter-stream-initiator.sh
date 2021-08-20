#!/bin/bash
export BEARER_TOKEN=###Your encrypted bearer token here####
/usr/bin/python3 /path_to_your_streamer.py/streamer.py >> /var/log/twitter-streamer.log &
jobid=$(echo $!)
while [ -n "$jobid" ];
        do
                if [ -n "$jobid" -a -e /proc/$jobid ];
                then
                        echo "twitter stream is up" > /dev/null
                        sleep 1
                else
                        echo "twitter stream is down! $(date)" >> /var/log/twitter-streamer.log
                        break
                fi
        done
