#include <Python.h>
#include "NcmCrypt/ncmcrypt.h"
#include <stdexcept>

static PyObject *
MusicDecrypt(PyObject *self, PyObject *args)
{
    const char *directory;
  if (!PyArg_ParseTuple(args, "s", &directory)) {
    return nullptr;
  }
  try {
      clock_t startTime, endTime;
      startTime = clock();
      NeteaseCrypt crypt(directory);
      crypt.Dump();
      endTime = clock();
      double const covert_time = (double)(endTime - startTime) / CLOCKS_PER_SEC;
      return Py_BuildValue("d", covert_time);
  } catch (std::invalid_argument e) {
      return Py_BuildValue("s", e.what());
  } catch (...) {
      return Py_BuildValue("s", "unexcept exception!");
  }
}

static PyMethodDef NetEaseMusicDecoderMethods[] = {
    {"decrypt", (PyCFunction) MusicDecrypt, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef DecoderModule = {
    PyModuleDef_HEAD_INIT,
    "NetEaseMusicDecrypt",
    "fastest decode ncm file",
    -1,
    NetEaseMusicDecoderMethods
};

PyMODINIT_FUNC
PyInit_NetEaseMusicDecrypt(void) {
  return PyModule_Create(&DecoderModule);
}