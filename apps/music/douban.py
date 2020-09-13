# -*- coding=utf-8 -*-
"""
从豆瓣获取歌曲信息
"""
import random
import re
from ipaddress import IPv4Address
from pprint import pprint
from urllib.parse import urlencode
from apps.config.logger import setup_log

import execjs
import requests

logger = setup_log()


class get_music_metadata(object):

    def __init__(self, search_text):
        self.cover_url = None
        self.search_text = search_text
        self.search_music()

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
        try:
            encrypt_text = re.search('window.__DATA__ = "([^"]+)"', response.text).group(1)
            self.decryppt_text = ctx.call('decrypt', encrypt_text)
            logger.exception("搜索内容:{}，解密豆瓣URL成功，body为:{}".format(self.search_text, self.decryppt_text))
        except Exception as e:
            logger.exception("搜索内容:{}，解密豆瓣URL失败，抛出异常:{}".format(self.search_text, e))
            return None

    def get_metadata(self):
        """
        由于豆瓣没有专辑信息，所以只取了歌手 发行时间 流派和专辑封面信息
        :return:
        """
        song_detail = []
        try:
            items = self.decryppt_text['payload']['items']

            for item in items:
                pprint(item)
                abstract = item['abstract'].replace(" ", "").split("/")
                if len(abstract) == 5:
                    singer = abstract[0]
                    pubDate = abstract[1]
                    genre = abstract[4]
                    cover_url = item['cover_url']
                    logger.info("搜索内容:{}，读取歌曲明细成功，歌手:{}，发行时间:{}，流派:{}，专辑封面:{}".format(self.search_text, singer, pubDate, genre, cover_url))
                    song_detail = [singer, pubDate, genre, cover_url]
                    break
        except Exception as e:
            logger.exception("搜索内容:{}，读取歌曲明细出错，抛出异常:{}".format(self.search_text, e))
        finally:
            return song_detail

    def download_cover_pic(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        response = requests.request("GET", self.cover_url, headers=headers)
        return response.status_code, response.content


if __name__ == '__main__':
    search_text = "陈翔 - 烟火"
    a = get_music_metadata(search_text=search_text)
    a.get_metadata()

