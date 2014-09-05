#include <iostream>
#include <vector>
#include "pyor.h"

using namespace std;


int main(int argc, char *argv[]) {
  vector<int> path = get_path("data.txt", 0, 142, 20.0, 3.0);

  cout << "path = [";
  for(vector<int>::size_type i = 0; i < path.size() - 1; i++) {
    cout << path[i] << ", ";
  }
  cout << path[path.size() - 1] << "]" << endl;

  return 0;
}
