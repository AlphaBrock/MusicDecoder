#include "ncmcrypt.h"
#include "../Base64/base64.h"

#include <stdexcept>
#include <string>

const unsigned char NeteaseCrypt::sCoreKey[17]   = {0x68, 0x7A, 0x48, 0x52, 0x41, 0x6D, 0x73, 0x6F, 0x35, 0x6B, 0x49, 0x6E, 0x62, 0x61, 0x78, 0x57, 0};
const unsigned char NeteaseCrypt::sModifyKey[17] = {0x23, 0x31, 0x34, 0x6C, 0x6A, 0x6B, 0x5F, 0x21, 0x5C, 0x5D, 0x26, 0x30, 0x55, 0x3C, 0x27, 0x28, 0};

const unsigned char NeteaseCrypt::mPng[8] = {0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A};

static void aesEcbDecrypt(const unsigned char *key, std::string& src, std::string& dst) {
    int n, i;

    unsigned char out[16];

    n = src.length() >> 4;

    dst.clear();

    AES aes(key);

    for (i = 0; i < n-1; i++) {
        aes.decrypt((unsigned char*)src.c_str() + (i << 4), out);
        dst += std::string((char*)out, 16);
    }

    aes.decrypt((unsigned char*)src.c_str() + (i << 4), out);
    char pad = out[15];
    if (pad > 16) {
        pad = 0;
    }
    dst += std::string((char*)out, 16-pad);
}

static void replace(std::string& str, const std::string& from, const std::string& to) {
    if(from.empty())
        return;
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}

NeteaseMusicMetadata::~NeteaseMusicMetadata() {
    cJSON_Delete(mRaw);
}

NeteaseMusicMetadata::NeteaseMusicMetadata(cJSON* raw) {
    if (!raw) {
        return;
    }

    cJSON *swap;
    int artistLen, i;

    mRaw = raw;

    swap = cJSON_GetObjectItem(raw, "musicName");
    if (swap) {
        mName = std::string(cJSON_GetStringValue(swap));
    }

    swap = cJSON_GetObjectItem(raw, "album");
    if (swap) {
        mAlbum = std::string(cJSON_GetStringValue(swap));
    }

    swap = cJSON_GetObjectItem(raw, "artist");
    if (swap) {
        artistLen = cJSON_GetArraySize(swap);

        i = 0;
        for (i = 0; i < artistLen-1; i++) {
            mArtist += std::string(cJSON_GetStringValue(cJSON_GetArrayItem(cJSON_GetArrayItem(swap, i), 0)));
            mArtist += "/";
        }
        mArtist += std::string(cJSON_GetStringValue(cJSON_GetArrayItem(cJSON_GetArrayItem(swap, i), 0)));
    }

    swap = cJSON_GetObjectItem(raw, "bitrate");
    if (swap) {
        mBitrate = swap->valueint;
    }

    swap = cJSON_GetObjectItem(raw, "duration");
    if (swap) {
        mDuration = swap->valueint;
    }

    swap = cJSON_GetObjectItem(raw, "format");
    if (swap) {
        mFormat = std::string(cJSON_GetStringValue(swap));
    }
}

bool NeteaseCrypt::openFile(std::string const& path) {
    try {
        mFile.open(path, std::ios::in | std::ios::binary);
    } catch (...) {
        return false;
    }
    return true;
}

bool NeteaseCrypt::isNcmFile() {
    unsigned int header;

    mFile.read(reinterpret_cast<char *>(&header), sizeof(header));
    if (header != (unsigned int)0x4e455443) {
        return false;
    }

    mFile.read(reinterpret_cast<char *>(&header), sizeof(header));
    if (header != (unsigned int)0x4d414446) {
        return false;
    }

    return true;
}

int NeteaseCrypt::read(char *s, std::streamsize n) {
    mFile.read(s, n);

    int gcount = mFile.gcount();

    if (gcount <= 0) {
        throw std::invalid_argument("can't read file");
    }

    return gcount;
}

void NeteaseCrypt::buildKeyBox(unsigned char *key, int keyLen) {
    int i;
    for (i = 0; i < 256; ++i) {
        mKeyBox[i] = (unsigned char)i;
    }

    unsigned char swap = 0;
    unsigned char c = 0;
    unsigned char last_byte = 0;
    unsigned char key_offset = 0;

    for (i = 0; i < 256; ++i)
    {
        swap = mKeyBox[i];
        c = ((swap + last_byte + key[key_offset++]) & 0xff);
        if (key_offset >= keyLen) key_offset = 0;
        mKeyBox[i] = mKeyBox[c]; mKeyBox[c] = swap;
        last_byte = c;
    }
}

void NeteaseCrypt::Dump() {
    int n, i;
    n = 0x8000;
    unsigned char buffer[n];

    size_t lastPath = mFilepath.find_last_of("/\\");
    std::string path = mFilepath.substr(lastPath+1);
    size_t lastExt = path.find_last_of(".");

    std::string::size_type idx = mFilepath.find("/");
    if (idx != std::string::npos)
    {
        mDumpFilepath = mFilepath.substr(0, lastPath)+"/"+path.substr(0, lastExt);
    }
    else{
        mDumpFilepath = mFilepath.substr(0, lastPath)+"\\"+path.substr(0, lastExt);
    }

    std::ofstream output;

    while (!mFile.eof()) {
        n = read((char*)buffer, n);

        for (i = 0; i < n; i++) {
            int j = (i + 1) & 0xff;
            buffer[i] ^= mKeyBox[(mKeyBox[j] + mKeyBox[(mKeyBox[j] + j) & 0xff]) & 0xff];
        }

        if (!output.is_open()) {
            // identify format
            // ID3 format mp3
            if (buffer[0] == 0x49 && buffer[1] == 0x44 && buffer[2] == 0x33) {
                mDumpFilepath += ".mp3";
                mFormat = NeteaseCrypt::MP3;
            } else {
                mDumpFilepath += ".flac";
                mFormat = NeteaseCrypt::FLAC;
            }
            output.open(mDumpFilepath, output.out | output.binary);
        }
        output.write((char*)buffer, n);
    }
    output.flush();
    output.close();
}

NeteaseCrypt::~NeteaseCrypt() {
    if (mMetaData != NULL) {
        delete mMetaData;
    }

    mFile.close();
}

NeteaseCrypt::NeteaseCrypt(std::string const& path) {
    if (!openFile(path)) {
        throw std::invalid_argument("can't open file");
    }

    if (!isNcmFile()) {
        throw std::invalid_argument("not netease protected file");
    }

    if (!mFile.seekg(2, mFile.cur)) {
        throw std::invalid_argument("can't seek file");
    }
    mFilepath = path;

    int i;

    unsigned int n;
    read(reinterpret_cast<char *>(&n), sizeof(n));

    if (n <= 0) {
        throw std::invalid_argument("broken ncm file");
    }

    char keydata[n];
    read(keydata, n);

    for (i = 0; i < n; i++) {
        keydata[i] ^= 0x64;
    }

    std::string rawKeyData(keydata, n);
    std::string mKeyData;

    aesEcbDecrypt(sCoreKey, rawKeyData, mKeyData);

    buildKeyBox((unsigned char*)mKeyData.c_str()+17, mKeyData.length()-17);

    read(reinterpret_cast<char *>(&n), sizeof(n));

    if (n <= 0) {
        printf("[Warn] `%s` missing metadata infomation can't fix some infomation!\n", path.c_str());

        mMetaData = NULL;
    } else {
        char modifyData[n];
        read(modifyData, n);

        for (i = 0; i < n; i++) {
            modifyData[i] ^= 0x63;
        }

        std::string swapModifyData;
        std::string modifyOutData;
        std::string modifyDecryptData;

        swapModifyData = std::string(modifyData + 22, n - 22);

        // escape `163 key(Don't modify):`
        Base64::Decode(swapModifyData, modifyOutData);

        aesEcbDecrypt(sModifyKey, modifyOutData, modifyDecryptData);

        // escape `music:`
        modifyDecryptData = std::string(modifyDecryptData.begin()+6, modifyDecryptData.end());

        // std::cout << modifyDecryptData << std::endl;

        mMetaData = new NeteaseMusicMetadata(cJSON_Parse(modifyDecryptData.c_str()));
    }

    // skip crc32 & unuse charset
    if (!mFile.seekg(9, mFile.cur)) {
        throw std::invalid_argument("can't seek file");
    }

    read(reinterpret_cast<char *>(&n), sizeof(n));

    if (n > 0) {
        char *imageData = (char*)malloc(n);
        read(imageData, n);

        mImageData = std::string(imageData, n);
    } else {
        printf("[Warn] `%s` missing album can't fix album image!\n", path.c_str());
    }
}
