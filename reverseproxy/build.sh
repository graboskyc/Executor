#!/bin/bash

echo
echo "+================================"
echo "| START: Executor Portal Reverse Proxy"
echo "+================================"
echo

source .env

datehash=`date | md5sum | cut -d" " -f1`
abbrvhash=${datehash: -8}

printf "using REQUIREDAUTHHEADER: ${REQUIREDAUTHHEADER}\n"
printf "using JWTOVERRIDE: ${JWTOVERRIDE}\n"

echo 
echo "Building container using tag ${abbrvhash}"
echo
docker build -t graboskyc/executorrp:latest -t graboskyc/executorrp:${abbrvhash} .

EXITCODE=$?

if [ $EXITCODE -eq 0 ]
    then

    echo 
    echo "Starting container"
    echo
    docker stop executorrp
    docker rm executorrp
    docker run -t -i -d -p 8888:80 --name executorrp -e "REQUIREDAUTHHEADER=${REQUIREDAUTHHEADER}" -e "JWTOVERRIDE=${JWTOVERRIDE}" --restart unless-stopped graboskyc/executorrp:${abbrvhash}

    echo
    echo "+================================"
    echo "| END:  Executor Portal Reverse Proxy"
    echo "+================================"
    echo
else
    echo
    echo "+================================"
    echo "| ERROR: Build failed"
    echo "+================================"
    echo
fi
