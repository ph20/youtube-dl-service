#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from uuid import uuid4
from chalice import Chalice
from urllib.parse import parse_qs
import boto3
from botocore.exceptions import ClientError
import simplejson as json
from chalicelib.downloader import get_payload, get_video_info, download_video
from chalicelib.downloader import YoutubeDLDownloadError
from chalicelib.utils import json_to_base64_gzip_compressed, base64_gzip_compressed_to_json


app = Chalice(app_name='youtube-dl-api')
# Create a low-level service clients
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')


def put_video_data(url: str, info: dict):
    """
    Puts video information into DynamoDB.
    """
    # generate a unique UUID for each new video info
    dynamodb_client = boto3.resource('dynamodb')
    table = dynamodb_client.Table('videosInfo')
    info = dict(info)
    if 'uuid' in info:
        uuid_str = info['uuid']
        del info['uuid']
    else:
        uuid_str = str(uuid4())
    value = json.dumps(info)
    # put the item in the table
    table.put_item(
       Item={
            'uuid': uuid_str,
            'url': url,
            'value': value  # new attribute
        }
    )
    return uuid_str


def get_video_data(uuid_str: str):
    """
    Retrieves video information from DynamoDB using uuid.
    """
    dynamodb_client = boto3.resource('dynamodb')
    table = dynamodb_client.Table('videosInfo')

    try:
        response = table.get_item(Key={'uuid': uuid_str})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    else:
        item = response.get('Item', {})
        data = json.loads(item.get('value', '{}'))
        data.update({'uuid': item.get('uuid', '')})
        return data


@app.route('/')
def index():
    return "Hello World!"


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.lambda_function(name='download-video')
def download_video_api(event, context):
    video_payload = base64_gzip_compressed_to_json(event['video_payload'])

    # update video status to 'downloading'
    info = get_video_data(event['uuid'])
    info['status'] = 'downloading'
    put_video_data(info['url'], info)

    files_list = download_video(video_payload)
    for file_path in files_list:
        s3_client.upload_file(file_path, 'youtube-dl-service', os.path.basename(file_path))

    # update video status to 'downloading'
    info = get_video_data(event['uuid'])
    info['status'] = 'downloaded'
    put_video_data(info['url'], info)

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
    uuid_str = put_video_data(video_url, info.dict())
    response = lambda_client.invoke(
        FunctionName='youtube-dl-api-dev-download-video',
        InvocationType='Event',
        Payload=json.dumps({'video_payload': json_to_base64_gzip_compressed(video_payload),
                            'uuid': uuid_str,
                            })
    )
    data = info.dict()
    data['uuid'] = uuid_str
    return {'status': 'ok', 'data': data}


@app.route('/video/{uuid}', methods=['GET'])
def get_video_api(uuid):
    """
    Retrieves video information from DynamoDB using uuid.
    """
    data = get_video_data(uuid)
    if not data:
        return {'status': 'error', 'message': 'video not found'}
    return {'status': 'ok', 'data': data}