#include <vector>

using namespace std;

/*
 * fin     : Name of input text file containing graph
 * s       : Source node index
 * t       : Target node index
 * ebudget : Edge weight budget (maximum sum of edge weights on the path)
 * tlim    : Time limit of solver in seconds
 */
vector<int> get_path(const char *fin, int s, int t, float ebudget, float tlim);
