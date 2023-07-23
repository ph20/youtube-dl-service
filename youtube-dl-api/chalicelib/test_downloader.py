#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from chalicelib.downloader import get_payload, get_video_info


class DownloaderTestCase(unittest.TestCase):
    def test_get_info(self):
        payload = get_payload('https://www.youtube.com/watch?v=9bZkp7q19f0')
        info = get_video_info(payload)
        print(info)


if __name__ == '__main__':
    unittest.main()
