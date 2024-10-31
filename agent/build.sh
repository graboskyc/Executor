#!/bin/bash

echo
echo "+================================"
echo "| START: Executor Agent"
echo "+================================"
echo

source .env

datehash=`date | md5sum | cut -d" " -f1`
abbrvhash=${datehash: -8}
echo "Using portal ${PORTAL}"

echo 
echo "Building container using tag ${abbrvhash}"
echo
docker build -t graboskyc/executoragent:latest -t graboskyc/executoragent:${abbrvhash} .

EXITCODE=$?

if [ $EXITCODE -eq 0 ]
    then

    echo 
    echo "Starting container"
    echo
    docker stop executoragent
    docker rm executoragent
    docker run -t -i -d --name executoragent -e "PORTAL=${PORTAL}" graboskyc/executoragent:${abbrvhash}

    echo
    echo "+================================"
    echo "| END:  Executor Agent"
    echo "+================================"
    echo
else
    echo
    echo "+================================"
    echo "| ERROR: Build failed"
    echo "+================================"
    echo
fi