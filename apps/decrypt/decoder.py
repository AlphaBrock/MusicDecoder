# -*- coding=utf-8 -*-
"""
该方式解密已经不使用了，目前使用C++方式把解密工作封装成python库了
"""
import os
import time
from multiprocessing import Pool
import ctypes


class QQMusicDecoder(object):
    """
    解密算法
    """

    def __init__(self):
        self.x = -1
        self.y = 8
        self.dx = 1
        self.index = -1
        self.seedMap = [[0x4a, 0xd6, 0xca, 0x90, 0x67, 0xf7, 0x52], [0x5e, 0x95, 0x23, 0x9f, 0x13, 0x11, 0x7e],
                        [0x47, 0x74, 0x3d, 0x90, 0xaa, 0x3f, 0x51], [0xc6, 0x09, 0xd5, 0x9f, 0xfa, 0x66, 0xf9],
                        [0xf3, 0xd6, 0xa1, 0x90, 0xa0, 0xf7, 0xf0], [0x1d, 0x95, 0xde, 0x9f, 0x84, 0x11, 0xf4],
                        [0x0e, 0x74, 0xbb, 0x90, 0xbc, 0x3f, 0x92], [0x00, 0x09, 0x5b, 0x9f, 0x62, 0x66, 0xa1]]

    def next_mask(self):
        self.index += 1
        if self.x < 0:
            self.dx = 1
            self.y = (8 - self.y) % 8
            ret = 0xc3
        elif self.x > 6:
            self.dx = -1
            self.y = 7 - self.y
            ret = 0xd8
        else:
            ret = self.seedMap[self.y][self.x]

        self.x += self.dx
        if self.index == 0x8000 or (self.index > 0x8000 and (self.index + 1) % 0x8000 == 0):
            return self.next_mask()
        return ret


class multiDecode(QQMusicDecoder):
    """
    线程池有问题
    """
    def __init__(self, file_path):
        super().__init__()
        self.check_file_path(file_path)
        self.worker = 10
        self.futures = []
        self.allowedFormat = ['qmcogg', 'qmcflac', 'qmc0']
        self.file_list = os.listdir(file_path)
        self.suffix_map = {"qmcogg": "ogg",
                           "qmcflac": "flac",
                           "qmc0": "mp3"
                           }
        self.decoder = ctypes.cdll.LoadLibrary("/Users/rizhiyi/github/QQMusicDecoder/src/QQMusicDecoder.so")

    def check_file_path(self, file_path):
        if file_path[-1] == "/":
            self.file_path = file_path
        else:
            self.file_path = file_path + "/"

    def save_file(self, music_data, file):
        file_name = file.split('.')[0]
        file_suffix = file.split('.')[-1]
        path = self.file_path + file_name + '.' + self.suffix_map.get(file_suffix)
        with open(path, 'wb') as f:
            f.write(music_data)

    def qmc_file_decrypt(self, file):
        """
        :type file: object
        """
        print('Run task %s (%s)...' % (file, os.getpid()))
        start_time = time.time()
        music_file_path = self.file_path + file
        with open(music_file_path, 'rb') as f:
            data = bytearray(f.read())
        for i in range(len(data)):
            data[i] ^= super().next_mask()
        self.save_file(data, file)
        end_time = time.time()
        print('finish task {} ,cost {.2f}'.format(file, end_time - start_time))

    def run(self):
        pool = Pool(self.worker)
        for i in range(len(self.file_list)):
            file_suffix = self.file_list[i].split('.')[-1]
            if file_suffix not in self.allowedFormat:
                print('文件:{} 不需要解密，跳过'.format(self.file_list[i]))
            else:
                music = bytes(self.file_path+self.file_list[i], encoding='utf-8')
                pool.apply_async(self.decoder.sub_process, args=(music,))
        pool.close()
        pool.join()


if __name__ == '__main__':
    file_path = "/Users/rizhiyi/github/QQMusicDecoder/music/"
    a = multiDecode(file_path)
    a.run()
