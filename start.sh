#!/bin/bash

docker build -t editor-service .
docker run -it -p 9191:9191 -v $(pwd)/work_dir:/app/work_dir editor-service