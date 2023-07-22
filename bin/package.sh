#!/usr/bin/env bash

DIST_DIR=$1
ARTIFACT_DIR_NAME=$2

# Check if CHALICE_APP_DIR is set
if [ -z "$CHALICE_APP_DIR" ]; then
  echo "Environment variable CHALICE_APP_DIR is not set. Exiting."
  exit 1
fi

if [ -z "$DIST_DIR" ]; then
  DIST_DIR="./dist"
fi

if [ -z "$ARTIFACT_DIR_NAME" ]; then
  ARTIFACT_DIR_NAME="$CHALICE_APP_DIR-lambda"
fi

# chalice requires UTF-8 encoding
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export LC_CTYPE=C.UTF-8

# region is required for chalice build
export AWS_DEFAULT_REGION=us-east-1

pushd $CHALICE_APP_DIR
chalice package --pkg-format=terraform $DIST_DIR/$ARTIFACT_DIR_NAME
popd