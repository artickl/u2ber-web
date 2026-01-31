#!/bin/bash
cd "$(dirname "$0")"

#if from cronjob, remove output redirection
if [[ ! -t 0 ]]; then
    docker compose up --build -d >/dev/null 2>&1
else
    docker compose up --build -d
fi

#check status
docker compose ps