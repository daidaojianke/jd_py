#!/bin/bash
echo -e "if [ -t 1 ]; then\n    exec zsh\nfi" >> /etc/profile
echo -e "0 1 * * * python /jd_scripts/jd_sign_collection.py >> /dev/null 2>&1" >> /etc/crontab