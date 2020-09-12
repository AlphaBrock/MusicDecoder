# -*- coding:utf-8 -*-
"""
可能是python版最快的解码速度了
"""
import os
import platform
import QQMusicDecrypt
import NetEaseMusicDecrypt


class decryptAudio(object):
    """
    解密音频文件
    """
    def __init__(self, audioDir):
        if not os.path.isdir(audioDir):
            raise Exception("哥，要求输入的是文件夹，不是其他的")
        if not os.path.exists(audioDir):
            raise Exception("哥，你输入的文件夹不存在")
        self.audioDir = audioDir
        self.audioFileList = os.listdir(self.audioDir)
        self.allowedFormat = ['qmcogg', 'qmcflac', 'qmc0', 'ncm']
        self.sysStr = platform.system()

    def decrypt(self):
        global musicFilePath
        for audioFile in self.audioFileList:
            fileSuffix = audioFile.split('.')[-1]
            if fileSuffix not in self.allowedFormat:
                print("文件:{}, 不需要解密, 跳过".format(audioFile))
            else:
                if self.audioDir[-1] == "/" or self.audioDir[-1] == "\\":
                    musicFilePath = self.audioDir + audioFile
                else:
                    if self.sysStr == "Windows":
                        musicFilePath = self.audioDir + "\\" + audioFile
                    if self.sysStr == "Linux" or self.sysStr == "Darwin":
                        musicFilePath = self.audioDir + "/" + audioFile

                if fileSuffix == "ncm":
                    covertCost = NetEaseMusicDecrypt.decrypt(musicFilePath)
                    print("文件:{}, 解密耗时:{}".format(audioFile, covertCost))
                else:
                    covertCost = QQMusicDecrypt.decrypt(musicFilePath)
                    print("文件:{}, 解密耗时:{}".format(audioFile, covertCost))
