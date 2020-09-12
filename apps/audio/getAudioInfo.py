# -*- coding=utf-8 -*-
"""
读取解密后音频信息
"""
import os

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import MP3


class prepare(object):
    def __init__(self, audioFile):
        if not isinstance(audioFile, str):
            raise TypeError("哥，请正确输入需要读取的文件路径")
        if not os.path.exists(audioFile):
            raise TypeError("哥，文件不存在啊")
        self.file = audioFile
        self.getFileSuffix()
        self.chooseReadType()

    def getFileSuffix(self):
        fileName = os.path.basename(self.file)
        self.fileSuffix = fileName.split('.')[-1]

    def checkIsHasPic(self):
        if len(self.songFile.pictures) == 0:
            return False
        else:
            return True

    def chooseReadType(self):
        if self.fileSuffix == "mp3":
            self.songFile = MP3(self.file, ID3=ID3)
            self.songFile.tags.update_to_v24()
            # 歌曲名称
            self.tagTitle = "TIT2"
            # 歌手
            self.tagArtist = "TPE1"
            # 歌曲专辑
            self.tagAlbum = "TALB"
            # 歌曲发行时间
            self.tagDate = "TDRC"
            # 歌曲流派
            self.tagType = "TCON"
        elif self.fileSuffix == "flac":
            self.songFile = FLAC(self.file)
            # 歌曲名称
            self.tagTitle = "TITLE"
            # 歌手
            self.tagArtist = "ARTIST"
            # 歌曲专辑
            self.tagAlbum = "ALBUM"
            # 歌曲发行时间
            self.tagDate = "DATE"
            # 歌曲流派
            self.tagType = "GENRE"


class GetAudioInfo(prepare):
    def __init__(self, file):
        super(GetAudioInfo, self).__init__(file)

    def getTitle(self):
        """
        获取歌曲名
        """
        try:
            title = str(self.songFile.tags[self.tagTitle])
        except Exception as e:
            # filename = os.path.basename(self.file)
            title = ''
        return title

    def getArtist(self):
        """
        获取歌手名
        """
        try:
            artist = str(self.songFile.tags[self.tagArtist])
        except Exception as e:
            artist = ''
        return artist

    def getAlbum(self):
        """
        获取专辑名
        """
        try:
            album = str(self.songFile.tags[self.tagAlbum])
        except Exception as e:
            album = ''
        return album

    def getDate(self):
        """
        获取专辑名
        """
        try:
            album = str(self.songFile.tags[self.tagDate])
        except Exception as e:
            album = ''
        return album

    def getType(self):
        """
        获取专辑名
        """
        try:
            album = str(self.songFile.tags[self.tagType])
        except Exception as e:
            album = ''
        return album

    def getLength(self):
        """
        获取文件播放时时长
        """
        timeLength = int(self.songFile.info.length)
        mintime = timeLength // 60
        sectime = timeLength % 60
        if sectime < 10:
            sectime = '0' + str(sectime)
        else:
            sectime = str(sectime)
        length = str(mintime) + ":" + sectime
        return length