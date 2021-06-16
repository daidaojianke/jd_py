#!/bin/sh
echo -e "0 1 * * * python /jd_scripts/jd_sign_collection.py >> /dev/null 2>&1" >> /etc/crontab