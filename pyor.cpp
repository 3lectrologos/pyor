#include <iostream>
#include <python2.7/Python.h>
#include <vector>

PyObject* loan_coverage_function_object()
{
  Py_Initialize();

  PyObject* name = PyString_FromString("cpp");

  PyObject* module = PyImport_Import(name);
  Py_DECREF(name);
  if (!module)
  {
    std::cout << "# ERROR: cpp script cannot be imported. Check that the PYTHONPATH environment variable includes the directory that contains the cpp script." << std::endl;
    return 0;
  }

  PyObject* dict = PyModule_GetDict(module);
  Py_DECREF(module);

  PyObject* function = PyDict_GetItemString(dict, "get_path");
  Py_DECREF(dict);

  return function;
}

void unloan_coverage_function_object(PyObject* obj)
{
  Py_DECREF(obj);
  Py_Finalize();
}

std::vector<int> get_path(PyObject* funcPyObj, const char *fin, int s, int t, float ebratio, float tlim)
{
  char types[] = "siiff";
  PyObject* res = PyObject_CallFunction(funcPyObj, types, fin, s, t, ebratio, tlim);
  Py_ssize_t len = PyList_Size(res);
  std::vector<int> path(len);
  for(Py_ssize_t i = 0; i < len; i++) {
    path[i] = PyInt_AsLong(PyList_GetItem(res, i));
  }

  Py_DECREF(res);

  return path;
}
