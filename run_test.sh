#!/usr/bin/env bash

function run_minio_server() {
    if [ ! -f tests/minio ]; then
        wget --quiet --output-document tests/minio https://dl.min.io/server/minio/release/linux-amd64/minio
        chmod +x tests/minio
    fi

    export MINIO_ACCESS_KEY=minio
    export MINIO_SECRET_KEY=minio123
    export MINIO_ADDRESS=0.0.0.0:9002
    tests/minio server /tmp/fs --address $MINIO_ADDRESS >tests/minio.log 2>&1 &
}

function run_mongo() {
   docker run --name awesome-mongo --rm -p 27000:27017 -d mongo:4.4.10
}

if [ -z ${SERVER_ENDPOINT+x} ]; then
    run_minio_server
    MINIO_PID=$!
    trap 'kill -9 ${MINIO_PID} 2>/dev/null' INT
    trap 'docker rm -f awesome-mongo' INT
    run_mongo
fi

pytest --cov=awesome_sso tests --cov-report term-missing
if [ -n "$MINIO_PID" ]; then
    kill -9 "$MINIO_PID" 2>/dev/null
    docker rm -f awesome-mongo
fi

