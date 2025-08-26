#pragma once

#include <iostream>
#include <string>

#include "support.hpp"

template<typename Metric, typename SupportRepn>
vector<vector<double>> compute_dH(
    const vector<vector<SupportRepn>>& supports,
    const vector<double>& scale_deltas,
    Metric metric,
    const string& metric_name
) {
    int n_files = supports.size();
    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));

    for (int flock_1 = 0; flock_1 < n_files; flock_1++) {
        for (int flock_2 = flock_1 + 1; flock_2 < n_files; flock_2++) {
            int n_flock_1 = supports[flock_1].size();
            int n_flock_2 = supports[flock_2].size();
            int n_iters = n_flock_1 * n_flock_2;

            vector<double> nn_flock1(n_flock_1, numeric_limits<double>::infinity());
            vector<double> nn_flock2(n_flock_2, numeric_limits<double>::infinity());
            #pragma omp parallel
            {
                vector<double> local_nn_flock1(n_flock_1, numeric_limits<double>::infinity());
                vector<double> local_nn_flock2(n_flock_2, numeric_limits<double>::infinity());
                #pragma omp for schedule(static)
                for (int iter = 0; iter < n_iters; iter++) {
                    int i = iter % n_flock_1;
                    int j = iter / n_flock_1;
                    double dist = metric(
                        supports[flock_1][i], supports[flock_2][j], 
                        scale_deltas[flock_1], scale_deltas[flock_2]
                    );
                    local_nn_flock1[i] = min(local_nn_flock1[i], dist);
                    local_nn_flock2[j] = min(local_nn_flock2[j], dist);
                }
                #pragma omp critical
                {
                    for (int iter = 0; iter < n_flock_1; iter++) {
                        nn_flock1[iter] = min(nn_flock1[iter], local_nn_flock1[iter]);
                    }
                    for (int iter = 0; iter < n_flock_2; iter++) {
                        nn_flock2[iter] = min(nn_flock2[iter], local_nn_flock2[iter]);
                    }
                }
            }           
            double d_hausdorff = 0.0;
            for (double d : nn_flock1) { d_hausdorff = max(d_hausdorff, d); }
            for (double d : nn_flock2) { d_hausdorff = max(d_hausdorff, d); }
            
            d2_matrix[flock_1][flock_2] = d_hausdorff;
            d2_matrix[flock_2][flock_1] = d_hausdorff;
            cout << "\tComputed " << metric_name << "(" << flock_1 << ", " << flock_2 << ") = " << d_hausdorff << endl;
        }
    }

    return d2_matrix;
}
