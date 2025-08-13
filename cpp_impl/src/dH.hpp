#pragma once

#include <iostream>
#include <string>

#include "support.hpp"

pair<int, int> unflatten_distance_pairs(int n_files, int index) {
    int i = 0;
    int row_length = n_files - 1;
    while (index >= row_length) {
        index -= row_length;
        i++;
        row_length--;
    }
    int j = i + 1 + index;
    return make_pair(i, j);
}

template<typename Metric>
vector<vector<double>> compute_dH(
    const vector<vector<Support>>& supports,
    const vector<double>& scale_deltas,
    Metric metric,
    const string& metric_name
) {
    int n_files = supports.size();
    vector<vector<double>> d2_matrix(n_files, vector<double>(n_files, 0.0));

    #pragma omp parallel for schedule(dynamic)
    for (int index = 0; index < n_files * (n_files - 1) / 2; index++) {
        pair<int, int> unpacked = unflatten_distance_pairs(n_files, index);
        int flock_1 = unpacked.first;
        int flock_2 = unpacked.second;

        vector<double> nn_flock1(supports[flock_1].size(), std::numeric_limits<double>::infinity());
        vector<double> nn_flock2(supports[flock_2].size(), std::numeric_limits<double>::infinity());
        
        for (int i = 0; i < supports[flock_1].size(); i++) {
            for (int j = 0; j < supports[flock_2].size(); j++) {
                double dist = metric(
                    supports[flock_1][i], supports[flock_2][j], 
                    scale_deltas[flock_1], scale_deltas[flock_2]
                );
                nn_flock1[i] = min(nn_flock1[i], dist);
                nn_flock2[j] = min(nn_flock2[j], dist);
            }
        }

        double d_hausdorff = 0.0;
        for (double d : nn_flock1) { d_hausdorff = max(d_hausdorff, d); }
        for (double d : nn_flock2) { d_hausdorff = max(d_hausdorff, d); }
        
        d2_matrix[flock_1][flock_2] = d_hausdorff;
        d2_matrix[flock_2][flock_1] = d_hausdorff;
        #pragma omp critical
        {
            cout << "\tComputed " << metric_name << "(" << flock_1 << ", " << flock_2 << ") = " << d_hausdorff << endl;
        }
    }

    return d2_matrix;
}
