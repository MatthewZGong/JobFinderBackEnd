#!/bin/bash

export FLASK_ENV=development
export PROJ_DIR=$PWD
export DEBUG=1

ENV_FILE=$(ls .env* 2> /dev/null | grep -v 'example.env')

if [ -z "$ENV_FILE" ]; then
    echo "Error: No .env file (other than example.env) found in the current directory."
    exit 1
fi

# Load environment variables from the .env file
export $(grep -v '^#' "$ENV_FILE" | xargs)

echo "Environment variables exported from $ENV_FILE."


# run our server locally:
PYTHONPATH=$(pwd):$PYTHONPATH
FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000

