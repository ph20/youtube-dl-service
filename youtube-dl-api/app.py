#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chalice import Chalice
from urllib.parse import parse_qs

from chalicelib.downloader import get_payload, get_video_info, YoutubeDLDownloadError

app = Chalice(app_name='youtube-dl-api')


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.route('/video',
           methods=['POST'],
           content_types=['application/x-www-form-urlencoded'],
           )
def video_add():
    parsed = parse_qs(app.current_request.raw_body.decode())
    video_urls = parsed.get('url')
    if not video_urls:
        return {'status': 'error', 'message': 'url parameter is required'}
    if len(video_urls) > 1:
        return {'status': 'error', 'message': 'only one url parameter is allowed'}
    video_url = video_urls[0]
    try:
        payload = get_payload(video_url)
    except YoutubeDLDownloadError as e:
        return {'status': 'error', 'message': str(e)}
    info = get_video_info(payload)
    return {'status': 'ok', 'data': info.dict()}


@app.route('/')
def index():
    return "Hello World!"

