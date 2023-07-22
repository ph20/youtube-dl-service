#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from contextlib import contextmanager

import chalice.cli

CHALICE_APP_DIR_ENV_NAME = 'CHALICE_APP_DIR'


@contextmanager
def change_dir(destination):
    try:
        cwd = os.getcwd()  # get current directory
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)  # change back to original directory


def run_local(chalice_app_dir):
    sys.argv = ['chalice', 'local', '--port', '5001', '--stage', 'dev']
    # change working directory to the
    with change_dir(chalice_app_dir):
        chalice.cli.main()


if __name__ == '__main__':
    if CHALICE_APP_DIR_ENV_NAME not in os.environ:
        print(f'Environment variable {CHALICE_APP_DIR_ENV_NAME} not set', file=sys.stderr)
        exit(1)
    run_local(chalice_app_dir=os.environ[CHALICE_APP_DIR_ENV_NAME])
