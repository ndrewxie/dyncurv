#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <iomanip>

#include "support.hpp"
#include "d2.hpp"

using namespace std;

void print_matrix(const std::vector<std::vector<double>>& matrix) {
    for (const auto& row : matrix) {
        for (const auto& elem : row) {
            std::cout << std::setw(8) << std::fixed << std::setprecision(2) << elem << " ";
        }
        std::cout << std::endl;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Usage: " << argv[0] << " <n_files> <file1> ..." << endl;
        return 1;
    }

    int n_files = stoi(argv[1]);

    vector<DynPointCloud> data;
    vector<Support> supports;
    for (int file_index = 0; file_index < n_files; file_index++) {
        ifstream in_file(argv[file_index+2]);
        if (!in_file.is_open()) {
            cout << "Error: cannot open " << argv[file_index+2] << endl;
            return 1;
        }
        int n_timesteps, n_pts, dim;
        in_file >> n_timesteps >> n_pts >> dim;

        DynPointCloud dyn_point_cloud;
        for (int t = 0; t < n_timesteps; t++) {
            PointCloud point_cloud;
            for (int i = 0; i < n_pts; i++) {
                Point point = vector<double>(dim);
                for (int j = 0; j < dim; j++) { in_file >> point[j]; }
                point_cloud.push_back(point);
            }
            dyn_point_cloud.push_back(point_cloud);
        }

        data.push_back(dyn_point_cloud);
        supports.push_back(compute_support(dyn_point_cloud));
    }

    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));
    for (int i = 0; i < n_files; i++) {
        for (int j = i+1; j < n_files; j++) {
            double dist = compute_d2(supports[i], supports[j], 0.01);
            d2_matrix[i][j] = dist;
            d2_matrix[j][i] = dist;
        }
    }

    print_matrix(d2_matrix);
    return 0;
}