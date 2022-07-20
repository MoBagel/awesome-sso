#!/usr/bin/env bash

function run_mongo() {
   docker run --name awesome-mongo --rm -p 27000:27017 -d mongo:4.4.10
}

if [ -z ${SERVER_ENDPOINT+x} ]; then
    trap 'docker rm -f awesome-mongo' INT
    run_mongo
fi

export MONGODB_DNS=mongodb://localhost:27000/beanie_db
pytest --cov=awesome_sso tests --cov-report term-missing
docker rm -f awesome-mongo

