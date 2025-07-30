#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <vector>
#include <filesystem>

#include "support.hpp"
#include "d2.hpp"
#include "dE.hpp"

using namespace std;
namespace fs = std::filesystem;

// Ty chatgpt
vector<string> get_file_paths(const string& folder_path) {
    vector<string> file_paths;
    for (const auto& entry : fs::directory_iterator(folder_path)) {
        if (fs::is_regular_file(entry.status())) {
            file_paths.push_back(entry.path().string());
        }
    }
    return file_paths;
}


int main(int argc, char* argv[]) {
    if (argc != 4) {
        // cout << "Usage: " << argv[0] << " <output_file> <in_file_1> ..." << endl;
        cout << "Usage: " << argv[0] << " <output_file> <in_folder_1> <in_folder_2>" << endl;
        return 1;
    }
    // cout << "Reading data and computing supports..." << endl;

    ofstream out_file(argv[1]);
    vector<vector<string>> in_filenames = {get_file_paths(argv[2]), get_file_paths(argv[3])};
    
    vector<vector<double>> scale_deltas(2);
    vector<vector<DynPointCloud>> data(2);
    vector<vector<Support>> supports(2);
    for (int in_file_index = 0; in_file_index < 2; in_file_index++) {
        for (string filename : in_filenames[in_file_index]) {
            ifstream in_file(filename);
            if (!in_file.is_open()) {
                cout << "Error: cannot open " << filename << endl;
                return 1;
            }
            double scale_delta;
            int n_pts;
            vector<int> bounds(2, 0);
            in_file >> n_pts >> bounds[0] >> bounds[1] >> scale_delta;
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
    
            scale_deltas[in_file_index].push_back(scale_delta);
            data[in_file_index].push_back(dyn_point_cloud);
            supports[in_file_index].push_back(compute_support(dyn_point_cloud, bounds));
        }
    }

    // cout << "Computing pairwise d2..." << endl;

    int n = in_filenames[0].size();
    int m = in_filenames[1].size();
    vector<vector<double>> d2_matrix(n, vector<double>(m, 0.0));
    for (int i = 0; i < n; i++) {
        // cout << "Computing distances for " << i << endl;
        for (int j = 0; j < m; j++) {
            double dist = compute_d2(supports[0][i], supports[1][j], scale_deltas[0][i], scale_deltas[1][j]);
            d2_matrix[i][j] = dist;
            // d2_matrix[j][i] = dist;
        }
    }

    for (const auto& row : d2_matrix) {
        for (const auto& elem : row) {
            out_file << elem << "\t";
        }
        out_file << endl;
    }

    // cout << "Computing pairwise dE..." << endl;

    // vector<vector<double>> dE_matrix(n, vector<double>(m, 0.0));
    // for (int i = 0; i < n; i++) {
    //     // cout << "Computing distances for " << i << endl;
    //     for (int j = 0; j < m; j++) {
    //         double dist = compute_dE(supports[0][i], supports[1][j], scale_deltas[0][i], scale_deltas[1][j]);
    //         dE_matrix[i][j] = dist;
    //         // dE_matrix[j][i] = dist;
    //     }
    // }

    // for (const auto& row : dE_matrix) {
    //     for (const auto& elem : row) {
    //         out_file << elem << "\t";
    //     }
    //     out_file << endl;
    // }

    out_file.close();
    return 0;
}