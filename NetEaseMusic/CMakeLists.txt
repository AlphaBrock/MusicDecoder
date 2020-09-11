cmake_minimum_required(VERSION 2.8)
project(NetEaseMusicDecoder)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if (MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++17")
else(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -pipe -std=c++11")
endif()

set(CMAKE_BUILD_TYPE Debug)

if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static -pthread -static-libgcc -static-libstdc++")
endif()


add_executable(NetEaseMusicDecoder main.cpp cJSON/cJSON.cpp NcmCrypt/ncmcrypt.cpp Aes/aes.cpp)