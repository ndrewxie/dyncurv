#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <vector>
#include <random>
#include <omp.h>

#include "support.hpp"
#include "d2.hpp"
#include "dE.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 4) {
        cout << "Usage: " << argv[0] << " <k> <n_samples> <output_file> <in_file_1> ..." << endl;
        return 1;
    }
    cout << "Reading data and computing supports..." << endl;

    int homology_dim = atoi(argv[1]);
    int n_samples = atoi(argv[2]);

    ofstream out_file(argv[3]);

    vector<double> scale_deltas;
    vector<DynPointCloud> data;
    vector<vector<Support>> supports;
    for (int argv_index = 4; argv_index < argc; argv_index++) {
        ifstream in_file(argv[argv_index]);
        if (!in_file.is_open()) {
            cout << "Error: cannot open " << argv[argv_index] << endl;
            return 1;
        }
        double scale_delta;
        vector<double> torus_bound(2, 0.0);
        int n_pts;
        in_file >> n_pts >> scale_delta >> torus_bound[0] >> torus_bound[1];
        string line;
        getline(in_file, line);

        cout << "Read file: " << n_pts << ", " 
             << scale_delta << ", " 
             << torus_bound[0] << ", " << torus_bound[1] << endl;

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
        vector<Support> pc_supports;
        bool has_sampled_empty = false;

        int global_count = 0;
        #pragma omp parallel
        {
            bool local_has_sampled_empty = false;
            vector<Support> local_pc_supports;
            vector<int> chosen_indices;
            vector<double> scratch_distances;
            DynPointCloud subsample;
            int local_count = 0;

            std::random_device rand_dev;
            std::mt19937 gen(rand_dev());
            std::uniform_int_distribution<> dist(0, n_pts - 1);

            #pragma omp for schedule(static)
            for (int sample_index = 0; sample_index < n_samples; sample_index++) {
                if (local_count == 100) {
                    #pragma omp critical
                    {
                        global_count += local_count;
                        local_count = 0;
                        cout << "\tSampling " << global_count << " / " << n_samples << endl;
                    }
                }
                local_count++;
                chosen_indices.clear();
                for (int i = 0; i < 2 * homology_dim + 2; i++) {
                    chosen_indices.push_back(dist(gen));
                }

                subsample.clear();
                for (auto& sample_frame : dyn_point_cloud) {
                    PointCloud subsample_frame;
                    for (auto& indx : chosen_indices) {
                        subsample_frame.push_back(sample_frame[indx]);
                    }
                    subsample.push_back(subsample_frame);
                }

                Support subsample_support = compute_support(subsample, torus_bound, scratch_distances);
                bool is_empty = is_support_empty(subsample_support);
                if (!is_empty) {
                    local_pc_supports.push_back(subsample_support);
                }
                local_has_sampled_empty |= is_empty;
            }
            #pragma omp critical
            {
                pc_supports.insert(
                    pc_supports.end(),
                    local_pc_supports.begin(),
                    local_pc_supports.end()
                );
                has_sampled_empty |= local_has_sampled_empty;
            }
        }
        if (has_sampled_empty) {
            pc_supports.push_back(init_support(dyn_point_cloud.size()));
        }
        scale_deltas.push_back(scale_delta);
        data.push_back(dyn_point_cloud);
        supports.push_back(pc_supports);
    }

    cout << "Non-empty support sizes:" << endl;
    for (auto& sup : supports) {
        cout << sup.size() << "\t";
    }
    cout << endl;

    int n_files = data.size();
    
    cout << "Computing pairwise d2..." << endl;
    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));
    for (int flock_1 = 0; flock_1 < n_files; flock_1++) {
        for (int flock_2 = flock_1+1; flock_2 < n_files; flock_2++) {
            double d_hausdorff = 0.0;
            #pragma omp parallel reduction(max:d_hausdorff)
            for (int i = 0; i < supports[flock_1].size(); i++) {
                double d_closest = std::numeric_limits<double>::infinity();
                for (int j = 0; j < supports[flock_2].size(); j++) {
                    double dist = compute_d2(
                        supports[flock_1][i], supports[flock_2][j], 
                        scale_deltas[flock_1], scale_deltas[flock_2]
                    );
                    d_closest = min(dist, d_closest);
                }
                d_hausdorff = max(d_hausdorff, d_closest);
            }

            d2_matrix[flock_1][flock_2] = d_hausdorff;
            d2_matrix[flock_2][flock_1] = d_hausdorff;
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
    for (int flock_1 = 0; flock_1 < n_files; flock_1++) {
        for (int flock_2 = flock_1+1; flock_2 < n_files; flock_2++) {
            double d_hausdorff = 0.0;
            #pragma omp parallel reduction(max:d_hausdorff)
            for (int i = 0; i < supports[flock_1].size(); i++) {
                double d_closest = std::numeric_limits<double>::infinity();
                for (int j = 0; j < supports[flock_2].size(); j++) {
                    double dist = compute_dE(
                        supports[flock_1][i], supports[flock_2][j], 
                        scale_deltas[flock_1], scale_deltas[flock_2]
                    );
                    d_closest = min(dist, d_closest);
                }
                d_hausdorff = max(d_hausdorff, d_closest);
            }

            dE_matrix[flock_1][flock_2] = d_hausdorff;
            dE_matrix[flock_2][flock_1] = d_hausdorff;
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