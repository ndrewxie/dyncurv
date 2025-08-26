#pragma once

#include <iostream>

#include "support.hpp"

template<typename Metric, typename SupportRepn>
float compute_dH(
    const vector<SupportRepn>& flock_1, const vector<SupportRepn>& flock_2, 
    float sd_1, float sd_2, 
    Metric metric
) {
    int n_iters = flock_1.size() * flock_2.size();

    vector<float> nn_flock1(flock_1.size(), numeric_limits<float>::infinity());
    vector<float> nn_flock2(flock_2.size(), numeric_limits<float>::infinity());
    #pragma omp parallel
    {
        vector<float> local_nn_flock1(flock_1.size(), numeric_limits<float>::infinity());
        vector<float> local_nn_flock2(flock_2.size(), numeric_limits<float>::infinity());
        #pragma omp for schedule(static)
        for (int iter = 0; iter < n_iters; iter++) {
            int i = iter % flock_1.size();
            int j = iter / flock_1.size();
            float dist = metric(
                flock_1[i], flock_2[j], 
                sd_1, sd_2
            );
            local_nn_flock1[i] = min(local_nn_flock1[i], dist);
            local_nn_flock2[j] = min(local_nn_flock2[j], dist);
        }
        #pragma omp critical
        {
            for (int iter = 0; iter < flock_1.size(); iter++) {
                nn_flock1[iter] = min(nn_flock1[iter], local_nn_flock1[iter]);
            }
            for (int iter = 0; iter < flock_2.size(); iter++) {
                nn_flock2[iter] = min(nn_flock2[iter], local_nn_flock2[iter]);
            }
        }
    }           
    float d_hausdorff = 0.0;
    for (float d : nn_flock1) { d_hausdorff = max(d_hausdorff, d); }
    for (float d : nn_flock2) { d_hausdorff = max(d_hausdorff, d); }
    return d_hausdorff;
}
