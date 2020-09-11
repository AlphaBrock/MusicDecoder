from os import path

from setuptools import setup, Extension, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

module = Extension('NetEaseMusicDecrypt',
                   sources=['main.cpp', 'cJSON/cJSON.cpp', 'NcmCrypt/ncmcrypt.cpp', 'Aes/aes.cpp'])

setup(name='NetEaseMusicDecrypt',
      version='1.0',
      author='AlphaBrock',
      author_email='jcciam@outlook.com',
      keywords='NetEaseMusic, MusicDecoder, MusicDecrypt, MusicCovert',
      description="fastest way to covert ncm file",
      license="MIT License",
      url='https://github.com/rizhiyi/MusicDecoder/',
      long_description=long_description,
      long_description_content_type="text/markdown",
      ext_modules=[module],
      packages=find_packages()
      )
