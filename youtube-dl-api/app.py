#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chalice import Chalice

app = Chalice(app_name='youtube-dl-api')


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.route('/')
def index():
    return "Hello World!"

