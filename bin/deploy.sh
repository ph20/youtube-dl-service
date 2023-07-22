#!/usr/bin/env bash

# Check if CHALICE_APP_DIR is set
if [ -z "$CHALICE_APP_DIR" ]; then
  echo "Environment variable CHALICE_APP_DIR is not set. Exiting."
  exit 1
fi

# chalice requires UTF-8 encoding
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export LC_CTYPE=C.UTF-8

# region is required for chalice build
export AWS_DEFAULT_REGION=us-east-1

pushd $CHALICE_APP_DIR
chalice deploy
popd