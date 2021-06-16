#!/bin/sh
echo -e "\nsource $CODE_DIR/venv/bin/activate" >> /root/.bashrc
echo -e "if [ -t 1 ]; then\n    exec bash\nfi" >> /etc/profile
echo -e "0 1 * * * python /jd_scripts/jd_sign_collection.py >> /dev/null 2>&1" >> /etc/crontab