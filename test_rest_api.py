#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pprint

REST_API_URL = 'https://uz5za5g872.execute-api.us-east-1.amazonaws.com/api/video'
VIDEO_URL = 'https://www.youtube.com/watch?v=seaBeltaKhw'


def test_rest_api():
    # add a new video
    payload = {'url': VIDEO_URL}
    print('HTTP POST', REST_API_URL, payload)
    video_json = requests.post(REST_API_URL, data=payload)
    video_obj = video_json.json()
    video_obj['data']['description'] = video_obj['data']['description'][:100]
    pprint.pprint(video_obj)
    print('')
    video_obj_url = REST_API_URL + '/' + video_obj['data']['uuid']

    print('HTTP GET ', video_obj_url)
    video_info_resp = requests.get(video_obj_url)
    video_info = video_info_resp.json()
    video_info['data']['description'] = video_info['data']['description'][:100]
    pprint.pprint(video_info)
    print('')

    status_url = video_obj_url + '/status'
    while True:
        video_status_resp = requests.get(status_url)
        print('HTTP GET ', status_url)
        video_status = video_status_resp.json()
        status = video_status['data']['status']
        pprint.pprint(video_status)
        if status == 'downloaded':
            break
        print('')

    download_url = video_obj_url + '/download'
    print('HTTP GET ', download_url)
    video_download_resp = requests.get(download_url)
    video_download_ = video_download_resp.json()
    pprint.pprint(video_download_)
    print('')

    print('HTTP DELETE ', video_obj_url)
    r = requests.delete(video_obj_url)
    pprint.pprint(r.json())
    assert video_json.status_code == 200


if __name__ == '__main__':
    test_rest_api()
