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

if [ -z ${SERVER_ENDPOINT+x} ]; then
    run_minio_server
    MINIO_PID=$!
    trap 'kill -9 ${MINIO_PID} 2>/dev/null' INT
fi

pytest --cov=awesome_sso tests/ --cov-report term-missing
if [ -n "$MINIO_PID" ]; then
    kill -9 "$MINIO_PID" 2>/dev/null
fi
