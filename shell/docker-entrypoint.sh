#!/bin/bash

function update() {
    cd /jd_scripts;
    git pull;
    pip install -r requirements.txt;
}



exec "$@"