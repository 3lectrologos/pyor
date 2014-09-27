#include <iostream>
#include <python2.7/Python.h>
#include "pyor.h"

int main(int argc, char *argv[])
{
  PyObject* function = loan_coverage_function_object();

  std::vector<int> path = get_path(function, "data.txt", 0, 1, 1.5, 1.0);

  std::cout << "path = [";
  for(std::vector<int>::size_type i = 0; i < path.size() - 1; i++) {
    std::cout << path[i] << ", ";
  }
  std::cout << path[path.size() - 1] << "]" << std::endl;

  unloan_coverage_function_object(function);

  return 0;
}
