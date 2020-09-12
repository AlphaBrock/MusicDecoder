# -*- coding=utf-8 -*-
"""
给解密后的音频文件插入专辑信息
"""
from mutagen import id3
from mutagen.flac import Picture
from mutagen.id3 import APIC, TIT2, TPE1, TALB, TDRC, TCON

from apps.audio.getAudioInfo import prepare


class modifyAudioInfo(prepare):

    def __init__(self, audioFile, audioPic):
        super().__init__(audioFile)
        self.audioPic = audioPic
        if self.audioPic.endswith("png"):
            self.mime = 'image/png'
        elif self.audioPic.endswith("jpg"):
            self.mime = 'image/jpeg'
        else:
            raise TypeError("哥，图片格式不对，只支持jpg和png的")

    def readPic(self):
        with open(self.audioPic,'rb') as f:
            self.albumart = f.read()
        f.close()

    def addCover(self):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                APIC(
                    encoding=3,
                    mime=self.mime,
                    type=3,
                    desc="Cover",
                    data=self.albumart
                )
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            image = Picture()
            image.type = id3.PictureType.COVER_FRONT
            image.mime = self.mime
            image.desc = "Cover"
            image.data = self.albumart
            image.width = 500
            image.height = 500
            image.depth = 16
            self.songFile.add_picture(image)
        self.songFile.save()

    def addTitle(self, audioTitle):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                TIT2(encoding=3, text=audioTitle)
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            self.songFile['title'] = audioTitle
        self.songFile.save()

    def addArtist(self, audioArtist):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                TPE1(encoding=3, text=audioArtist)
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            self.songFile['artist'] = audioArtist
        self.songFile.save()

    def addAlbum(self, audioAlbum):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                TALB(encoding=3, text=audioAlbum)
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            self.songFile['album'] = audioAlbum
        self.songFile.save()

    def addDate(self, audioDate):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                TDRC(encoding=3, text=audioDate)
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            self.songFile['date'] = audioDate
        self.songFile.save()

    def addType(self, audioType):
        if self.fileSuffix == "mp3" or self.fileSuffix == "MP3":
            self.songFile.tags.add(
                TCON(encoding=3, text=audioType)
            )
        elif self.fileSuffix == "flac" or self.fileSuffix == "FLAC":
            self.songFile['genre'] = audioType
        self.songFile.save()
