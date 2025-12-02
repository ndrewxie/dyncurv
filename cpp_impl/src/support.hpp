#pragma once

#include <vector>
#include <string>
#include <cmath>
#include <limits>

#include "diag_arr.hpp"

using namespace std;

typedef vector<float> Point;
typedef vector<Point> PointCloud;
typedef vector<PointCloud> DynPointCloud;

class Support {
public:
    vector<pair<int, int>> indices;

    Support(int n_time) : mat(n_time, make_pair(0.0, 0.0)) {};
    Support(DynPointCloud& dpc, vector<float>& bounds, vector<float>& distances);

    int size() const { return mat.size(); }
    pair<float, float>& at(int i, int j) { return mat.at(i, j); }
    const pair<float, float>& at (int i, int j) const { return mat.at(i, j); }
private:
    DiagonalMatrix<pair<float, float>> mat;

    void build_indices();
};