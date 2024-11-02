#!/bin/bash

# Build the Docker image
docker build -t text-editor-api .

# Run the Docker container, mounting the work directories
docker run -d -p 9191:9191 -v ./work_dir:/app/work_dir text-editor-api
