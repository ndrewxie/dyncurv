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
#include "dH.hpp"

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 5) {
        cout << "Usage: " << argv[0] << " <k> <target_n_samples> <max_n_samples> <output_file> <in_file_1> ..." << endl;
        return 1;
    }
    cout << "Reading data and computing supports..." << endl;

    int homology_dim = atoi(argv[1]);
    int target_n_samples = atoi(argv[2]);
    int max_n_samples = atoi(argv[3]);

    ofstream out_file(argv[4]);

    vector<double> scale_deltas;
    vector<DynPointCloud> data;
    vector<vector<Support>> supports;
    for (int argv_index = 5; argv_index < argc; argv_index++) {
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
        vector<Support> pc_supports = { init_support(dyn_point_cloud.size()) };

        std::random_device rand_dev;
        uint32_t global_seed = rand_dev();
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();

            vector<Support> local_pc_supports;
            vector<int> chosen_indices;
            vector<double> scratch_distances;
            DynPointCloud subsample;

            std::mt19937 gen(global_seed + tid);
            std::uniform_int_distribution<> dist(0, n_pts - 1);

            #pragma omp for schedule(static)
            for (int sample_index = 0; sample_index < max_n_samples; sample_index++) {
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
            }
            #pragma omp critical
            {
                pc_supports.insert(
                    pc_supports.end(),
                    local_pc_supports.begin(),
                    local_pc_supports.end()
                );
            }
        }

        vector<Support> k_center_supports;
        vector<double> k_center_dists(pc_supports.size(), std::numeric_limits<double>::infinity());
        for (int i = 0; i < min(pc_supports.size(), (size_t)target_n_samples); i++) {
            int max_index = max_element(k_center_dists.begin(), k_center_dists.end()) - k_center_dists.begin();
            Support max_supp = pc_supports[max_index];
            k_center_supports.push_back(max_supp);
            #pragma omp parallel for schedule(static)
            for (int j = 0; j < k_center_dists.size(); j++) {
                k_center_dists[j] = min(k_center_dists[j], compute_d2(max_supp, pc_supports[j], scale_delta, scale_delta));
            }
        }
        double k_center_approx_error = *std::max_element(k_center_dists.begin(), k_center_dists.end());

        scale_deltas.push_back(scale_delta);
        data.push_back(dyn_point_cloud);
        supports.push_back(k_center_supports);
        cout << "\tSampled " << k_center_supports.size() << " supports with approximation error " << k_center_approx_error << endl;
    }

    int n_files = data.size();
    
    cout << "Computing pairwise d2..." << endl;
    vector<vector<double>> d2_matrix = compute_dH(supports, scale_deltas, compute_d2, "d2");
    for (const auto& row : d2_matrix) {
        for (const auto& elem : row) {
            out_file << elem << "\t";
        }
        out_file << endl;
    }

    /*
 *     cout << "Computing pairwise dE..." << endl;
 *         vector<vector<double>> dE_matrix = compute_dH(supports, scale_deltas, compute_dE, "dE");
 *             for (const auto& row : dE_matrix) {
 *                     for (const auto& elem : row) {
 *                                 out_file << elem << "\t";
 *                                         }
 *                                                 out_file << endl;
 *                                                     }
 *                                                         */

    out_file.close();
    return 0;
}

