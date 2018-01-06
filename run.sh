#! /usr/bin/env bash

docker container rm uyp
docker run --name -d uyp -v "$(pwd)/volume:/USP Yellow Pages/volume" uyp
