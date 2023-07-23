#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from chalice import Chalice
from urllib.parse import parse_qs
import boto3
import simplejson as json
from chalicelib.downloader import get_payload, get_video_info, download_video
from chalicelib.downloader import YoutubeDLDownloadError
from chalicelib.utils import json_to_base64_gzip_compressed, base64_gzip_compressed_to_json

app = Chalice(app_name='youtube-dl-api')
# Create a low-level service clients
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')


@app.route('/')
def index():
    return "Hello World!"


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.lambda_function(name='download-video')
def download_video_api(event, context):
    video_payload = base64_gzip_compressed_to_json(event['video_payload'])
    files_list = download_video(video_payload)
    for file_path in files_list:
        s3_client.upload_file(file_path, 'youtube-dl-service', os.path.basename(file_path))
    return {'status': 'ok', 'data': {'files': files_list}}


@app.route('/video',
           methods=['POST'],
           content_types=['application/x-www-form-urlencoded'],
           )
def video_add_api():
    parsed = parse_qs(app.current_request.raw_body.decode())
    video_urls = parsed.get('url')
    if not video_urls:
        return {'status': 'error', 'message': 'url parameter is required'}
    if len(video_urls) > 1:
        return {'status': 'error', 'message': 'only one url parameter is allowed'}
    video_url = video_urls[0]
    try:
        video_payload = get_payload(video_url)
    except YoutubeDLDownloadError as e:
        return {'status': 'error', 'message': str(e)}
    info = get_video_info(video_payload)
    response = lambda_client.invoke(
        FunctionName='youtube-dl-api-dev-download-video',
        InvocationType='Event',
        Payload=json.dumps({'video_payload': json_to_base64_gzip_compressed(video_payload)})
    )
    return {'status': 'ok', 'data': info.dict()}
