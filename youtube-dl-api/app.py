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

S3_BUCKET_NAME = 'youtube-dl-service'


app = Chalice(app_name='youtube-dl-api')
# Create a low-level service clients
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
dynamodb_client = boto3.resource('dynamodb')
table = dynamodb_client.Table('videosInfo')


def generate_resigned_url(object_key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None

    return response


def put_video_data(info: dict, dump_uri: str = ''):
    """
    Puts video information into DynamoDB.
    """
    # generate a unique UUID for each new video info
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
            'dump_uri': dump_uri,
            'value': value  # new attribute
        }
    )
    return uuid_str


def get_video_data(uuid_str: str):
    """
    Retrieves video information from DynamoDB using uuid.
    """

    try:
        response = table.get_item(Key={'uuid': uuid_str})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    else:
        item = response.get('Item', {})
        data = json.loads(item.get('value', '{}'))
        data.update({'uuid': item.get('uuid', '')})
        return data, item.get('dump_uri', '')


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
    uuid_str = event['uuid']
    info, _ = get_video_data(uuid_str)
    info['status'] = 'downloading'
    put_video_data(info)

    files_list = download_video(video_payload)
    dump_uri = ''
    for file_path in files_list:
        dump_uri = uuid_str + '/' + os.path.basename(file_path)
        s3_client.upload_file(file_path, S3_BUCKET_NAME, dump_uri)

    # update video status to 'downloading'
    info, _ = get_video_data(event['uuid'])
    info['status'] = 'downloaded'
    put_video_data(info, dump_uri=dump_uri)

    return {'status': 'ok', 'data': {'dump_uri': dump_uri}}


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
    uuid_str = put_video_data(info.dict())
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
    data, _ = get_video_data(uuid)
    if not data:
        return {'status': 'error', 'message': 'video not found'}
    return {'status': 'ok', 'data': data}


@app.route('/video/{uuid}/status', methods=['GET'])
def get_video_status_api(uuid):
    """
    Retrieves video information from DynamoDB using uuid.
    """
    data, _ = get_video_data(uuid)
    if not data:
        return {'status': 'error', 'message': 'video not found'}
    return {'status': 'ok', 'data': {'status': data['status'], 'uuid': data['uuid']}}


@app.route('/video/{uuid}/download', methods=['GET'])
def get_videos_download_api(uuid):
    """
    Retrieves video information from DynamoDB using uuid.
    """
    data, dump_uri = get_video_data(uuid)
    if not data:
        return {'status': 'error', 'message': 'video not found'}
    if dump_uri:
        dump_uri = generate_resigned_url(dump_uri)
    return {'status': 'ok', 'data': {'download_url': dump_uri or None}}


@app.route('/video/{uuid}', methods=['DELETE'])
def delete_video_api(uuid):
    """
    Retrieves video information from DynamoDB using uuid.
    """
    data, dump_video = get_video_data(uuid)
    if dump_video:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=dump_video)
    if not data:
        return {'status': 'error', 'message': 'video not found'}
    table.delete_item(Key={'uuid': uuid})
    return {'status': 'ok', 'message': 'video deleted'}
