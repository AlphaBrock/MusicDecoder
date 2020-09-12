# -*- coding=utf-8 -*-
"""
从豆瓣获取歌曲信息
"""
import random
import re
from ipaddress import IPv4Address
from pprint import pprint
from urllib.parse import urlencode

import execjs
import requests


class get_music_metadata(object):

    def __init__(self, search_text):
        self.search_text = search_text
        self.cover_url = None

    def search_music(self):
        params = {
            "search_text": "{}".format(self.search_text),
            "cat": 1003
        }
        url = "https://search.douban.com/music/subject_search?{}".format(urlencode(params))

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': '{}'.format(url),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            'Host': 'search.douban.com',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        response = requests.request("GET", url, headers=headers)

        with open('douban_bundle.js', 'r', encoding='utf-8') as f:
            decrypt_bundle_js = f.read()
        f.close()
        ctx = execjs.compile(decrypt_bundle_js)
        encrypt_text = re.search('window.__DATA__ = "([^"]+)"', response.text).group(1)
        try:
            self.decryppt_text = ctx.call('decrypt', encrypt_text)
            pprint(self.decryppt_text)
        except Exception as e:
            return None

    def download_cover_pic(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        response = requests.request("GET", self.cover_url, headers=headers)
        return response.status_code, response.content


