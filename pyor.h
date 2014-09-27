#ifndef PYOR_H
#define PYOR_H

#include <vector>

PyObject* loan_coverage_function_object();
void unloan_coverage_function_object(PyObject* obj);

/*
 * fin     : Name of input text file containing graph
 * s       : Source node index
 * t       : Target node index
 * ebudget : Edge weight budget (maximum sum of edge weights on the path)
 * tlim    : Time limit of solver in seconds
 */
std::vector<int> get_path(PyObject* funcPyObj, const char *fin, int s, int t, float ebudget, float tlim);

#endif
