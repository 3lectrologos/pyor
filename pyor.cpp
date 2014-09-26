#include <python2.7/Python.h>
#include <vector>
#include <cstdio>

using namespace std;


vector<int> get_path(const char *fin, int s, int t, float ebratio, float tlim) {
  Py_Initialize();
  PyObject *name, *module, *dict, *function;
  name = PyString_FromString("cpp");
  module = PyImport_Import(name);
  dict = PyModule_GetDict(module);
  function = PyDict_GetItemString(dict, "get_path");
  
  PyObject *res;
  char types[] = "siiff";
  res = PyObject_CallFunction(function, types, fin, s, t, ebratio, tlim);
  Py_ssize_t len = PyList_Size(res);
  vector<int> path(len);
  for(Py_ssize_t i = 0; i < len; i++) {
    path[i] = PyInt_AsLong(PyList_GetItem(res, i));
  }

  Py_DECREF(module);
  Py_DECREF(name);
  Py_Finalize();

  return path;
}
