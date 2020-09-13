# -*- coding:utf-8 -*-
from ipaddress import IPv4Address
import random

import requests

from apps.config.logger import setup_log
from apps.audio.getAudioInfo import GetAudioInfo, prepare
from apps.audio.modifyAudioInfo import modifyAudioInfo
from apps.music.qqmusic import get_music_metadata_from_qq as qqmusic
from apps.music.netease import get_music_metadata_from_netease as neteasemusic

import os

logger = setup_log()


def downloadCover(cover_url):
    url = "https://"+cover_url
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
    }
    try:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        logger.exception("cover_url:{}下载异常，抛出:{}".format(cover_url, e))
        return None


def main(audioDir):
    if not os.path.isdir(audioDir):
        raise Exception("哥，要求输入的是文件夹，不是其他的")
    if not os.path.exists(audioDir):
        raise Exception("哥，你输入的文件夹不存在")
    audioFileList = os.listdir(audioDir)

    for audioFile in audioFileList:
        if audioFile != ".DS_Store":
            try:
                # 从文件名中获取歌手和歌曲名用于后续判断解密出来的信息是否异常
                audioFileName = os.path.basename(audioFile).replace(" ", "").split("-")
                audioFileSinger = audioFileName[0]
                audioFileTitle = audioFileName[1]
                fileSuffix = audioFile.split('.')[-1]
            except Exception as e:
                logger.error("文件:{} 异常，跳过".format(audioFile))
                continue

            # 目前只做mp3 flac的修改
            if fileSuffix in allowedAudioSuffix:
                newAudioFile = audioDir + '/' + audioFile
                # 从音频中读取metadata
                audioInfo = GetAudioInfo(newAudioFile)
                audioTitle = audioInfo.getTitle()
                audioArtist = audioInfo.getArtist()
                audioAlbum = audioInfo.getAlbum()
                audioPubDate = audioInfo.getPubDate()
                audioGenre = audioInfo.getGenre()
                checkPicStatus = prepare(newAudioFile).checkIsHasPic()
                logger.info(
                    "歌曲:{}, 获取METADATA信息如下:{} {} {} {} {} {}".format(audioFile, audioTitle, audioArtist, audioAlbum,
                                                                     audioPubDate,
                                                                     audioGenre, checkPicStatus))
                # 先从QQ音乐获取到相关信息
                songDetail = qqmusic(audioFile.split('.')[0]).get_song_detail()
                if len(songDetail) == 0:
                    logger.warning("歌曲:{} 歌手:{}, 从QQ音乐获取信息失败".format(audioFileTitle, audioFileSinger))
                else:
                    songAlbum = songDetail[0]
                    songTimePublic = songDetail[1]
                    songPic = songDetail[2]
                    songGenre = songDetail[3]
                    picContent = downloadCover(songPic)
                    if picContent is None:
                        logger.info("歌曲:{} 歌手:{}, 下载歌曲图片异常".format(audioFileTitle, audioFileSinger))
                    else:
                        modify = modifyAudioInfo(newAudioFile, picContent)
                        if audioTitle == "":
                            modify.addTitle(audioFileTitle)
                            logger.info("文件:{}，检测到需要添加歌曲名称".format(audioFile))
                        if audioArtist == "":
                            modify.addArtist(audioFileSinger)
                            logger.info("文件:{}，检测到需要添加歌手".format(audioFile))
                        if audioPubDate == "":
                            modify.addDate(songTimePublic)
                            logger.info("文件:{}，检测到需要添加发行时间".format(audioFile))
                        if audioAlbum == "":
                            modify.addAlbum(songAlbum)
                            logger.info("文件:{}，检测到需要添加专辑名称".format(audioFile))
                        if audioGenre == "":
                            modify.addType(songGenre)
                            logger.info("文件:{}，检测到需要添加流派".format(audioFile))
                        if checkPicStatus is False:
                            modify.addCover()
                            logger.info("文件:{}，检测到需要添加专辑封面".format(audioFile))
            else:
                logger.info("歌曲:{} 歌手:{}, 无需修改音频信息".format(audioFileTitle, audioFileSinger))


if __name__ == '__main__':
    allowedAudioSuffix = ['mp3', 'MP3', 'FLAC', 'flac']
    audioDir = "/Users/rizhiyi/Music/网易云音乐"
    main(audioDir)
