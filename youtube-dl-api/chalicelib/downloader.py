#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses
import youtube_dl
from youtube_dl.utils import DownloadError as YoutubeDLDownloadError

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
    title: str
    description: str
    duration: int
    url: str
    status: str
    id: int = None

    def dict(self):
        return dataclasses.asdict(self)


def get_payload(url):
    ydl = youtube_dl.YoutubeDL(params={'cachedir': '/tmp/youtube-dl-cache'})
    payload = ydl.extract_info(url, download=False, process=False)
    return payload


def get_video_info(payload) -> VideoInfo:
    video_info = VideoInfo(
        title=payload['title'],
        description=payload['description'],
        duration=payload['duration'],
        url=payload['webpage_url'],
        status=VIDEO_NOT_DOWNLOADED
    )
    return video_info
