#!/bin/bash

echo
echo "+================================"
echo "| START: Executor Portal"
echo "+================================"
echo

source backend/.env

datehash=`date | md5sum | cut -d" " -f1`
abbrvhash=${datehash: -8}
echo "Using conn string ${MDBCONNSTR}"

echo 
echo "Building container using tag ${abbrvhash}"
echo
docker build -t graboskyc/executor:latest -t graboskyc/executor:${abbrvhash} .

EXITCODE=$?

if [ $EXITCODE -eq 0 ]
    then

    echo 
    echo "Starting container"
    echo
    docker stop executor
    docker rm executor
    docker run -t -i -d -p 8000:8000 --name executor -e "MDBCONNSTR=${MDBCONNSTR}" --restart unless-stopped graboskyc/executor:${abbrvhash}

    echo
    echo "+================================"
    echo "| END:  Executor Portal"
    echo "+================================"
    echo
else
    echo
    echo "+================================"
    echo "| ERROR: Build failed"
    echo "+================================"
    echo
fi