#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <vector>

#include "support.hpp"
#include "d2.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Usage: " << argv[0] << " <n_files> <file1> ..." << endl;
        return 1;
    }

    int n_files = stoi(argv[1]);

    cout << "Reading data and computing supports..." << endl;

    vector<double> scale_deltas;
    vector<DynPointCloud> data;
    vector<Support> supports;
    for (int file_index = 0; file_index < n_files; file_index++) {
        ifstream in_file(argv[file_index+2]);
        if (!in_file.is_open()) {
            cout << "Error: cannot open " << argv[file_index+2] << endl;
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

    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));
    for (int i = 0; i < n_files; i++) {
        for (int j = i+1; j < n_files; j++) {
            double dist = compute_d2(supports[i], supports[j], scale_deltas[i], scale_deltas[j]);
            d2_matrix[i][j] = dist;
            d2_matrix[j][i] = dist;
        }
    }

    for (const auto& row : d2_matrix) {
        for (const auto& elem : row) {
            std::cout << std::setw(8) << std::fixed << std::setprecision(2) << elem << " ";
        }
        std::cout << std::endl;
    }
    return 0;
}