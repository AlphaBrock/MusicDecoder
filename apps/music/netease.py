# -*- coding=utf-8 -*-
"""
从网易云获取歌曲信息，不到万部得以不使用这货，目前只能通过代理池来绕开反爬
所以还是放弃治疗吧，基本不会用这玩意，大致上QQ音乐就够了，QQ音乐没有会使用豆瓣音乐
"""
import base64
import binascii
import json
import math
import random
from ipaddress import IPv4Address
from urllib.parse import urlencode

import requests
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from apps.config.logger import setup_log

logger = setup_log()


def rsa_encrypt(text, pub_key, modulus):
    """
    此处模拟RSA加密，需要注意的是，网易云对传入加密文本字符串数组是做了倒序处理的，所以我们也要倒序一下
    :param text:
    :param pub_key:
    :param modulus:
    :return:
    """
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16),
             int(pub_key, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def create_secret_key(size):
    """
    创建rsa加密密钥，a-zA-Z0-9随机16位字符串
    :param size:
    :return:
    """
    # return binascii.hexlify(os.urandom(size))[:16]
    b = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    c = ''
    for _ in range(size):
        e = random.random() * len(b)
        e = math.floor(e)
        c += b[e]
    return str.encode(c)


def aes_encrypt(text, sec_key):
    """
    模拟网易云的AES加密方式
    :param text:
    :param sec_key:
    :return:
    """
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(sec_key, 2, b'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def create_params_and_seckey(text, pub_key, MODULUS, nonce):
    """
    这里就是创建params和enSecKey的地方
    :param text:
    :return:
    """
    try:
        sec_key = create_secret_key(16)  # 第二次加密使用的密匙
        result = aes_encrypt(text, nonce)  # 第一次使用默认密匙加密的结果
        enc_text = aes_encrypt(result, sec_key)  # 加密第一次的结果为params
        enc_sec_key = rsa_encrypt(sec_key, pub_key, MODULUS)
        return enc_text, enc_sec_key
    except Exception as e:
        logger.exception("create_params_and_seckey 抛出异常:{}".format(e))


def dict_loop(array, dict):
    """
    简单做下汉字匹配字符，用于function_d函数传参，此处本可以直接用固定参数，因为从调试结果来看，这是个常量
    不过还是实现下网易云的代码，要是哪天常量也被改了呢
    :param array:
    :param dict:
    :return:
    """
    encrypted_data = []
    for i in array:
        encrypted_data.append(dict.get(i))
    # 这里做下字符转换
    return "".join(encrypted_data)


def obtain_params_and_seckey(body):
    # 字典表，用于匹配字符串
    DICTIONARY = {
        "色": "00e0b",
        "流感": "509f6",
        "这边": "259df",
        "弱": "8642d",
        "嘴唇": "bc356",
        "亲": "62901",
        "开心": "477df",
        "呲牙": "22677",
        "憨笑": "ec152",
        "猫": "b5ff6",
        "皱眉": "8ace6",
        "幽灵": "15bb7",
        "蛋糕": "b7251",
        "发怒": "52b3a",
        "大哭": "b17a8",
        "兔子": "76aea",
        "星星": "8a5aa",
        "钟情": "76d2e",
        "牵手": "41762",
        "公鸡": "9ec4e",
        "爱意": "e341f",
        "禁止": "56135",
        "狗": "fccf6",
        "亲亲": "95280",
        "叉": "104e0",
        "礼物": "312ec",
        "晕": "bda92",
        "呆": "557c9",
        "生病": "38701",
        "钻石": "14af6",
        "拜": "c9d05",
        "怒": "c4f7f",
        "示爱": "0c368",
        "汗": "5b7a4",
        "小鸡": "6bee2",
        "痛苦": "55932",
        "撇嘴": "575cc",
        "惶恐": "e10b4",
        "口罩": "24d81",
        "吐舌": "3cfe4",
        "心碎": "875d3",
        "生气": "e8204",
        "可爱": "7b97d",
        "鬼脸": "def52",
        "跳舞": "741d5",
        "男孩": "46b8e",
        "奸笑": "289dc",
        "猪": "6935b",
        "圈": "3ece0",
        "便便": "462db",
        "外星": "0a22b",
        "圣诞": "8e7",
        "流泪": "01000",
        "强": "1",
        "爱心": "0CoJU",
        "女孩": "m6Qyw",
        "惊恐": "8W8ju",
        "大笑": "d"
    }
    # 加密文本信息
    MD_ARRAY = ["色", "流感", "这边", "弱", "嘴唇", "亲", "开心", "呲牙", "憨笑", "猫", "皱眉", "幽灵", "蛋糕", "发怒", "大哭", "兔子", "星星", "钟情",
                "牵手", "公鸡",
                "爱意", "禁止", "狗", "亲亲", "叉", "礼物", "晕", "呆", "生病", "钻石", "拜", "怒", "示爱", "汗", "小鸡", "痛苦", "撇嘴", "惶恐",
                "口罩", "吐舌",
                "心碎", "生气", "可爱", "鬼脸", "跳舞", "男孩", "奸笑", "猪", "圈", "便便", "外星", "圣诞"]
    params, encSecKey = create_params_and_seckey(body, dict_loop(["流泪", "强"], DICTIONARY),
                                                 dict_loop(MD_ARRAY, DICTIONARY),
                                                 bytes(dict_loop(["爱心", "女孩", "惊恐", "大笑"], DICTIONARY),
                                                       encoding="utf8"))
    return params, encSecKey


class get_music_metadata_from_netease(object):

    def __init__(self, search_text):
        self.search_text = search_text
        self.cover_url = None

    def searchMusic(self):
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Referer': 'https://music.163.com/search/',
            'Origin': 'https://music.163.com',
            'X-Forwarded-For': str(IPv4Address(random.getrandbits(32)))
        }
        body = {
            "hlpretag": "",
            "hlposttag": "",
            "s": "{}".format(self.search_text),
            "type": "1",
            "offset": "0",
            "total": "true",
            "limit": "30"
        }
        body = json.dumps(body).encode('utf-8')
        params, encSecKey = obtain_params_and_seckey(body)
        payload = {
            'params': params,
            'encSecKey': encSecKey
        }
        response = requests.request("POST", url=url, headers=headers, data=payload)
        logger.info("搜索网易云音乐正常，返回结果:{}".format(response.text))
        rsp = json.loads(response.text)
        try:
            if rsp['msg'] == "Cheating":
                print("Ops, 网易云发现你在爬取数据了!")
                logger.error("Ops, 网易云发现你在爬取数据了!")
            return rsp
        except Exception as e:
            logger.exception("搜索网易云音乐异常，抛出:{}".format(e))

    def getSongDetail(self):
        params = {
            "id": "4875036"
        }
        url = "https://music.163.com/song?{}".format(urlencode(params))

        headers = {
            'Referer': 'https://music.163.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }

        response = requests.request("GET", url, headers=headers)
        logger.info("获取网易云音乐歌曲图片和发行时间，返回结果:{}".format(response.text))
        try:
            song_detail = BeautifulSoup(response.text, 'lxml').find('script').string
            song_detail = json.loads(song_detail)
            images = song_detail['images']
            pubDate = song_detail['pubDate']
            logger.info("获取网易云音乐歌曲图片和发行时间正常，专辑封面:{}，发行时间:{}".format(response.text, images, pubDate))
            return images, pubDate
        except Exception as e:
            logger.exception("获取网易云音乐歌曲图片和发行时间异常，抛出:{}".format(e))
