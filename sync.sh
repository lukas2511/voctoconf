#!/bin/bash

cd /home/lukas2511/Projects/voctoconf/
rsync --archive voctoconf@10.20.131.112:/opt/voctoconf/ /home/lukas2511/Projects/voctoconf/ --exclude '.git*' --exclude '/sync.sh' --delete
git status
