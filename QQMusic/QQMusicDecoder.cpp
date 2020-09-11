#include <Python.h>
#include <iostream>
#include <memory>
#include <regex>

#include "DecryptionAlgorithm.hpp"

#if defined(__cplusplus) && __cplusplus >= 201703L && defined(__has_include)
#endif

using namespace std;

void close_file(std::FILE* fp) { std::fclose(fp); }
using smartFilePtr = std::unique_ptr<std::FILE, decltype(&close_file)>;

enum class openMode { read, write };
/**
 * @brief open a file
 *
 * @param aDir
 * @param aOpenMode
 * @return smartFilePtr
 */
smartFilePtr openFile(const std::string& aPath, openMode aOpenMode) {
#ifndef _WIN32
  std::FILE* fp =
      fopen(aPath.c_str(), aOpenMode == openMode::read ? "rb" : "wb");
#else
  std::wstring aPath_w;
  aPath_w.resize(aPath.size());
  int newSize = MultiByteToWideChar(CP_UTF8, 0, aPath.c_str(), aPath.length(),
                                    const_cast<wchar_t*>(aPath_w.c_str()),
                                    aPath_w.size());
  aPath_w.resize(newSize);
  std::FILE* fp = NULL;
  _wfopen_s(&fp, aPath_w.c_str(), aOpenMode == openMode::read ? L"rb" : L"wb");
#endif
  return smartFilePtr(fp, &close_file);
}

static const std::regex mp3_regex{"\\.(qmc3|qmc0)$"};
static const std::regex ogg_regex{"\\.qmcogg$"};
static const std::regex flac_regex{"\\.qmcflac$"};

double sub_process(const char *dir) {
  std::string outloc(reinterpret_cast<const char*>(dir));

  auto mp3_outloc = regex_replace(outloc, mp3_regex, ".mp3");
  auto flac_outloc = regex_replace(outloc, flac_regex, ".flac");
  auto ogg_outloc = regex_replace(outloc, ogg_regex, ".ogg");

  if (mp3_outloc != outloc)
    outloc = mp3_outloc;
  else if (flac_outloc != outloc)
    outloc = flac_outloc;
  else
    outloc = ogg_outloc;

  auto infile = openFile(dir, openMode::read);

  if (infile == nullptr) {
//    std::cerr << "failed to read file: " << outloc << std::endl;
    return -1;
  }

  int res = fseek(infile.get(), 0, SEEK_END);
  if (res != 0) {
//    std::cerr << dir << " "seek failed << std::endl;
    return -2;
  }

  auto len = ftell(infile.get());
  fseek(infile.get(), 0, SEEK_SET);

  std::unique_ptr<char[]> buffer(new (std::nothrow) char[len]);
  if (buffer == nullptr) {
//    std::cerr << "create buffer error" << std::endl;
    return -3;
  }

  auto fres = fread(buffer.get(), 1, len, infile.get());
  if (fres != len) {
//    std::cerr<< dir << " read error" << std::endl;
    return -4;
  }

  qmc_decoder::seed seed_;
  clock_t startTime, endTime;
  startTime = clock();
  for (int i = 0; i < len; ++i) {
    buffer[i] = seed_.next_mask() ^ buffer[i];
  }

  auto outfile = openFile(outloc, openMode::write);

  if (outfile == nullptr) {
//    std::cerr << "failed to write file: " << outloc << std::endl;
    return -5;
  }

  fres = fwrite(buffer.get(), 1, len, outfile.get());
  if (fres != len) {
//    std::cerr << dir << " write file error" << std::endl;
    return -6;
  }
  endTime = clock();
  double const cost = (double)(endTime - startTime) / CLOCKS_PER_SEC;
//  std::cout << dir << " covert time:"<< cost << "s" <<std::endl;
  return cost;
}

static PyObject *
MusicDecrypt(PyObject *self, PyObject *args)
{
  const char *directory;
  double covert_time;
  if (!PyArg_ParseTuple(args, "s", &directory)) {
    return nullptr;
  }

  covert_time = sub_process(directory);

  return Py_BuildValue("d", covert_time);
}

static PyMethodDef QQMusicDecoderMethods[] = {
    {"decrypt", (PyCFunction) MusicDecrypt, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef DecoderModule = {
    PyModuleDef_HEAD_INIT,
    "QQMusicDecrypt",
    "fastest decrypt qmc file",
    -1,
    QQMusicDecoderMethods
};

PyMODINIT_FUNC
PyInit_QQMusicDecrypt(void) {
  return PyModule_Create(&DecoderModule);
}
