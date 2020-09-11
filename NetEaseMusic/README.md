## 前言

这个库是专门用于解密网易云音乐加密音频

这里感谢: [https://github.com/anonymous5l/ncmdump](https://github.com/anonymous5l/ncmdump) 大佬的解密算法，由于python处理的硬伤，处理效率低下，故使用C++封装了个python库供调用以解决该问题

## 功能说明

该库定义了一个函数 **decrypt**，用于负责解密文件，且只能对单个文件做解密，因为传参要注意

使用方法

```python
from NetEaseMusicDecrypt import decrypt
MusicFile = "/Users/rizhiyi/github/MusicDecoder/music/张宇-趁早.ncm"
CovertTime = decrypt(MusicFile)
# 单位秒
print(CovertTime)
```

## 返回信息

- 解密正常时返回double型耗时时间
- 解密异常则返回相关错误信息

## TODO

- [ ] 支持直接解密指定目录文件



