#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import uuid
import os
from glob import glob

import youtube_dl
from youtube_dl.utils import DownloadError as YoutubeDLDownloadError

DOWNLOAD_DIR = '/tmp/youtube-dl'
CACHE_DIR = '/tmp/youtube-dl-cache'

VIDEO_NOT_DOWNLOADED = 'not downloaded'
VIDEO_DOWNLOADING = 'downloading'
VIDEO_DOWNLOADED = 'downloaded'
VIDEO_STATUSES = [
    VIDEO_NOT_DOWNLOADED,
    VIDEO_DOWNLOADING,
    VIDEO_DOWNLOADED,
]


@dataclasses.dataclass
class VideoInfo:
    uuid: str
    title: str
    description: str
    duration: int
    url: str
    status: str

    def dict(self):
        return dataclasses.asdict(self)


def get_payload(url):
    ydl = youtube_dl.YoutubeDL(params={'cachedir': CACHE_DIR})
    payload = ydl.extract_info(url, download=False, process=False)
    return payload


def get_video_info(payload) -> VideoInfo:
    video_info = VideoInfo(
        uuid=str(uuid.uuid4()),
        title=payload['title'],
        description=payload['description'],
        duration=payload['duration'],
        url=payload['webpage_url'],
        status=VIDEO_NOT_DOWNLOADED
    )
    return video_info


def download_video(payload):
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    cwd = os.getcwd()
    os.chdir(DOWNLOAD_DIR)
    ydl = youtube_dl.YoutubeDL(params={'cachedir': CACHE_DIR})
    _ = ydl.process_ie_result(payload, download=True)
    downloaded_files = glob(DOWNLOAD_DIR + '/*.mp4')
    os.chdir(cwd)
    return downloaded_files
