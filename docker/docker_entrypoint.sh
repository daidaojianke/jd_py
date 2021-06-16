#!/bin/sh
crontab -l > conf && echo "0 1 * * * python /jd_scripts/jd_sign_collection.py >> /dev/null 2>&1" >> conf && crontab conf && rm -f conf