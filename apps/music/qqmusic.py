# -*- coding=utf-8 -*-
"""
从QQ音乐获取歌曲信息
"""
import json
import random
import re
from ipaddress import IPv4Address
from urllib.parse import urlencode

import requests

from apps.config.logger import setup_log

logger = setup_log()


class get_music_metadata_from_qq(object):

    def __init__(self, search_text):
        self.search_text = search_text
        self.search_music()

    def search_music(self):
        """
        获取三个值 mid album time_public
        分别是 打开歌曲网页id 专辑名称 发行时间
        :return:
        """
        params = {
            "ct": 24,
            "qqmusic_ver": 1298,
            "new_json": 1,
            "remoteplace": "txt.yqq.top",
            "n": 10,
            "w": "{}".format(self.search_text),
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "platform": "yqq.json",
        }
        url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?{}".format(urlencode(params))

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            'Cookie': 'RK=MVRBAVZ3Za; ptcz=2f577c778ee0052b7632ef713126e2e45ae5ae88ac01e70177db07ad46dae826; pgv_pvid=8144015660; eas_sid=G1K5397379Z5o5Z5g4I8F7u6O9; ied_qq=o0528327016; pgv_pvi=7295406080; ptui_loginuin=528327016; tvfe_boss_uuid=7f7c7cc972a9bba0; ts_uid=3856897600; pac_uid=0_15174fbc09396; ts_refer=www.google.com/; yqq_stat=0; pgv_si=s5413747712; pgv_info=ssid=s6815006848; userAction=1; psrf_qqrefresh_token=2FD53678E1B1D0E1E60B4580149FFC23; psrf_qqunionid=; psrf_qqaccess_token=E5519680D3BBD2EB9C30BC99E4925908; uin=528327016; psrf_musickey_createtime=1599920966; psrf_qqopenid=19C359F2B1BD3B98D554EF318D55A7A3; qm_keyst=Q_H_L_2OqsSz50eKs80MZxKUd_xCrTMBhOl6J_H5LT2w90xC8r8Mc9w6NT-Gw85QqLol1; psrf_access_token_expiresAt=1607696966; qqmusic_key=Q_H_L_2OqsSz50eKs80MZxKUd_xCrTMBhOl6J_H5LT2w90xC8r8Mc9w6NT-Gw85QqLol1; euin=7K-Foi-loe6s; tmeLoginType=2; ts_last=y.qq.com/portal/search.html',
            'Referer': 'https://y.qq.com/portal/search.html',
            'Origin': 'https://y.qq.com',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        response = requests.request("GET", url, headers=headers)
        try:
            rsp = json.loads(response.text)
            self.song_mid = rsp['data']['song']['list'][0]['mid']
            self.song_album = rsp['data']['song']['list'][0]['album']['name']
            self.song_time_public = rsp['data']['song']['list'][0]['time_public']
        except Exception as e:
            logger.exception("搜索QQ音乐获取歌曲网页地址，专辑，发行时间异常，抛出:{}".format(e))

    def get_song_detail(self):
        """
        单独网页获取歌曲专辑封面以及流派
        :return:
        """
        url = "https://y.qq.com/n/yqq/song/{}.html".format(self.song_mid)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'https://y.qq.com/portal/search.html',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32))),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers)
        song = []
        try:
            song_pic = re.compile('<img src=\"//([^\"]+)\"\s+onerror=').search(response.text).group(1).replace(
                "300x300", "500x500")
            song_info = re.compile('info : (.*)').search(response.text).group(1)
            song_info = json.loads(song_info)
            try:
                genre = song_info['genre']['content'][0]['value']
            except Exception as e:
                logger.warning("文件:{}，获取流派失败，抛出异常:{}".format(self.search_text, e))
                genre = ""
            song = [self.song_album, self.song_time_public, song_pic, genre]
            logger.info(
                "文件:{}，获取歌曲信息成功,专辑:{},发行时间:{},专辑封面:{},流派:{}".format(self.search_text, self.song_album, self.song_time_public, song_pic, genre))
        except Exception as e:
            logger.exception("文件:{}，QQ音乐获取歌曲流派以及专辑封面异常，抛出:{}".format(self.search_text, e))
        finally:
            return song


if __name__ == '__main__':
    search_text = "张宇-趁早"
    a = get_music_metadata_from_qq(search_text=search_text)
    a.get_song_detail()
