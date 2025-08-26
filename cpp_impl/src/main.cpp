#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <vector>
#include <random>
#include <omp.h>
#include <chrono>
#include <ctime>

#include "support.hpp"
#include "d2.hpp"
#include "dE.hpp"
#include "dH.hpp"
#include "diag_arr.hpp"

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

    vector<float> scale_deltas;
    vector<DynPointCloud> data;
    vector<vector<Support>> supports;
    for (int argv_index = 5; argv_index < argc; argv_index++) {
        ifstream in_file(argv[argv_index]);
        if (!in_file.is_open()) {
            cout << "Error: cannot open " << argv[argv_index] << endl;
            return 1;
        }
        float scale_delta;
        vector<float> torus_bound(2, 0.0);
        int n_pts;
        in_file >> n_pts >> scale_delta >> torus_bound[0] >> torus_bound[1];
        string line;
        getline(in_file, line);
        
        DynPointCloud dyn_point_cloud;
        while (getline(in_file, line)) {
            stringstream ss(line);
            Point p;
            float coord_val;
            while (ss >> coord_val) {
                p.push_back(coord_val);
            }
            if (p.size() == 0) { continue; }

            if (dyn_point_cloud.size() == 0 || dyn_point_cloud.back().size() == n_pts) {
                dyn_point_cloud.push_back(PointCloud());
            }

            dyn_point_cloud.back().push_back(p);
        }
        vector<Support> pc_supports = { Support(dyn_point_cloud.size()) };

        cout << "Read file: " 
             << n_pts << " per frame, "
             << dyn_point_cloud.size() << " frames, " 
             << "scale_delta = " << scale_delta << ", " 
             << "bounds = (" << torus_bound[0] << ", " << torus_bound[1] << ")" << endl;

        std::random_device rand_dev;
        uint32_t global_seed = rand_dev();
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();

            vector<Support> local_pc_supports;
            vector<int> chosen_indices;
            vector<float> scratch_distances;
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

                Support subsample_support = Support(subsample, torus_bound, scratch_distances);
                if (subsample_support.indices.size() > 0) {
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

        cout << "\t\tDone sampling " << pc_supports.size() << " preliminary supports" << endl;

        vector<Support> k_center_supports;
        vector<float> k_center_dists(pc_supports.size(), std::numeric_limits<float>::infinity());
        for (int i = 0; i < min(pc_supports.size(), (size_t)target_n_samples); i++) {
            if (i % 100 == 0) { cout << "\t\tIteration " << i << " of k-center" << endl; }
            int max_index = max_element(k_center_dists.begin(), k_center_dists.end()) - k_center_dists.begin();
            Support max_supp = pc_supports[max_index];
            k_center_supports.push_back(max_supp);
            #pragma omp parallel for schedule(static)
            for (int j = 0; j < k_center_dists.size(); j++) {
                k_center_dists[j] = min(k_center_dists[j], compute_d2(max_supp, pc_supports[j], scale_delta, scale_delta));
            }
        }
        float k_center_approx_error = *std::max_element(k_center_dists.begin(), k_center_dists.end());

        int n_sparse = 0;
        int n_sparse_max = 0;
        for (auto& s : k_center_supports) { n_sparse += s.indices.size(); n_sparse_max += s.size() * s.size(); }
        cout << "\tAverage sparsity: " << 2.0 * (float)n_sparse / (float)n_sparse_max << endl;

        scale_deltas.push_back(scale_delta);
        data.push_back(dyn_point_cloud);
        supports.push_back(k_center_supports);
        cout << "\tSampled " << k_center_supports.size() << " supports with approximation error " << k_center_approx_error << endl;
    }

    int n_files = supports.size();

    auto curr_time = chrono::system_clock::now();
    time_t current_time_t = chrono::system_clock::to_time_t(curr_time);
    cout << "Done sampling at: " << ctime(&current_time_t)  << endl;
    
    cout << "Computing pairwise d2..." << endl;
    chrono::steady_clock::time_point d2_begin = chrono::steady_clock::now();
    for (int flock_1 = 0; flock_1 < n_files; flock_1++) {
        for (int flock_2 = flock_1 + 1; flock_2 < n_files; flock_2++) {
            float d_hausdorff = compute_dH(
                supports[flock_1], supports[flock_2], 
                scale_deltas[flock_1], scale_deltas[flock_2],
                compute_d2
            );
            out_file << d_hausdorff << "\t";
            cout << d_hausdorff << "\t";
        }
        out_file << endl;
        cout << endl;
    }
    chrono::steady_clock::time_point d2_end = chrono::steady_clock::now();
    cout << "Done computing pairwise d2 in " 
         << chrono::duration_cast<chrono::microseconds>(d2_end - d2_begin).count() << endl;

    out_file << endl;

    cout << "Computing pairwise dE..." << endl;
    chrono::steady_clock::time_point dE_begin = chrono::steady_clock::now();
    for (int flock_1 = 0; flock_1 < n_files; flock_1++) {
        for (int flock_2 = flock_1 + 1; flock_2 < n_files; flock_2++) {
            auto flock_1_repn = dE_cvt_supps(supports, scale_deltas, flock_1);
            auto flock_2_repn = dE_cvt_supps(supports, scale_deltas, flock_2);
            float d_hausdorff = compute_dH(
                flock_1_repn, flock_2_repn, 
                scale_deltas[flock_1], scale_deltas[flock_2],
                compute_dE_quadratic
            );
            out_file << d_hausdorff << "\t";
            cout << d_hausdorff << "\t";
        }
        out_file << endl;
        cout << endl;
    }
    chrono::steady_clock::time_point dE_end = chrono::steady_clock::now();
    cout << "Done computing pairwise dE in " 
         << chrono::duration_cast<chrono::microseconds>(dE_end - dE_begin).count() << endl;

    out_file.close();
    return 0;
}

