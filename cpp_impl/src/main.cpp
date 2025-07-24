#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <vector>

#include "support.hpp"
#include "d2.hpp"
#include "dE.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Usage: " << argv[0] << " <output_file> <in_file_1> ..." << endl;
        return 1;
    }
    cout << "Reading data and computing supports..." << endl;

    ofstream out_file(argv[1]);

    vector<double> scale_deltas;
    vector<DynPointCloud> data;
    vector<Support> supports;
    for (int argv_index = 2; argv_index < argc; argv_index++) {
        ifstream in_file(argv[argv_index]);
        if (!in_file.is_open()) {
            cout << "Error: cannot open " << argv[argv_index] << endl;
            return 1;
        }
        double scale_delta;
        int n_pts;
        in_file >> n_pts >> scale_delta;
        string line;
        getline(in_file, line);

        DynPointCloud dyn_point_cloud;
        while (getline(in_file, line)) {
            stringstream ss(line);
            Point p;
            double coord_val;
            while (ss >> coord_val) {
                p.push_back(coord_val);
            }
            if (p.size() == 0) { continue; }

            if (dyn_point_cloud.size() == 0 || dyn_point_cloud.back().size() == n_pts) {
                dyn_point_cloud.push_back(PointCloud());
            }

            dyn_point_cloud.back().push_back(p);
        }

        scale_deltas.push_back(scale_delta);
        data.push_back(dyn_point_cloud);
        supports.push_back(compute_support(dyn_point_cloud));
    }

    cout << "Computing pairwise d2..." << endl;

    int n_files = data.size();
    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));
    for (int i = 0; i < n_files; i++) {
        cout << "Computing distances for " << i << endl;
        for (int j = i+1; j < n_files; j++) {
            double dist = compute_d2(supports[i], supports[j], scale_deltas[i], scale_deltas[j]);
            d2_matrix[i][j] = dist;
            d2_matrix[j][i] = dist;
        }
    }

    for (const auto& row : d2_matrix) {
        for (const auto& elem : row) {
            out_file << elem << "\t";
        }
        out_file << endl;
    }

    cout << "Computing pairwise dE..." << endl;

    vector<vector<double>> dE_matrix(n_files, vector<double>(n_files, 0.0));
    for (int i = 0; i < n_files; i++) {
        cout << "Computing distances for " << i << endl;
        for (int j = i+1; j < n_files; j++) {
            double dist = compute_dE(supports[i], supports[j], scale_deltas[i], scale_deltas[j]);
            dE_matrix[i][j] = dist;
            dE_matrix[j][i] = dist;
        }
    }

    for (const auto& row : dE_matrix) {
        for (const auto& elem : row) {
            out_file << elem << "\t";
        }
        out_file << endl;
    }

    out_file.close();
    return 0;
}