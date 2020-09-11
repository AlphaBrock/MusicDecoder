from os import path

from setuptools import setup, Extension, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

module = Extension('QQMusicDecrypt',
                   extra_compile_args=['-std=c++11'],
                   sources=['QQMusicDecoder.cpp'])

setup(name='QQMusicDecrypt',
      version='1.0',
      author='AlphaBrock',
      author_email='jcciam@outlook.com',
      keywords='QQMusic, MusicDecoder, MusicDecrypt, MusicCovert',
      description="fastest way to covert qmc file",
      license="MIT License",
      url='https://github.com/rizhiyi/MusicDecoder/',
      long_description=long_description,
      long_description_content_type="text/markdown",
      ext_modules=[module],
      packages=find_packages()
      )
