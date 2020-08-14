#!/bin/bash

set -e

git pull
./manage.py migrate
./manage.py collectstatic --noinput --clear
sudo systemctl restart uwsgi
sudo systemctl restart voctoconf-daphne
