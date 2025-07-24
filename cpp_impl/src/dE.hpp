#pragma once

#include <array>
#include <algorithm>
#include <limits>
#include <cmath>
#include <assert.h>

#include "support.hpp"

using namespace std;

vector<vector<vector<bool>>> mask(Support& v, double scaleDelta){ 
    int n = v.size();
    int m = v[0].size();

    vector<vector<vector<bool>>> a(n, vector<vector<bool>>(n, vector<bool>(m, 0)));
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            for(int k = 0; k < m; k++){
                a[i][j][k] = ( (v[i][j].first <= k * scaleDelta) && (k * scaleDelta <= v[i][j].second) );
            }
        }
    }

    return a;

}

double compute_dE(Support& sup_v, Support& sup_w, double sd_v, double sd_w){

    assert(sup_v.size() == sup_v[0].size());
    assert(sup_v.size() == sup_w.size());
    assert(sd_v == sd_w);

    int n = sup_v.size();
    double sd = sd_v;
    vector<vector<vector<bool>>> mask_v = mask(sup_v, sd_v);
    vector<vector<vector<bool>>> mask_w = mask(sup_w, sd_w);
    int m = mask_v[0][0].size();

    vector<vector<vector<int>>> down_v(n, vector<vector<int>>(n, vector<int>(m, 0)));
    vector<vector<vector<int>>> down_w(n, vector<vector<int>>(n, vector<int>(m, 0)));
    for(int i = n-1; i >= 0; i--){
        for(int j = i; j < n; j++){
            for(int k = 0; k < m; k++){
                if(k > 0){
                    if(mask_v[i][j][k] && !mask_w[i][j][k]){
                        down_v[i][j][k] = down_v[i+1 < j ? i+1 : i][i != j ? j-1 : j][k-1] + 1;
                    }
                    if(!mask_v[i][j][k] && mask_w[i][j][k]){
                        down_w[i][j][k] = down_w[i+1 < j ? i+1 : i][i != j ? j-1 : j][k-1] + 1;
                    }
                }
            }
        }
    }

    vector<vector<vector<int>>> up_v(n, vector<vector<int>>(n, vector<int>(m, 0)));
    vector<vector<vector<int>>> up_w(n, vector<vector<int>>(n, vector<int>(m, 0)));
    for(int i = 0; i < n; i++){
        for(int j = n-1; j >= i; j--){
            for(int k = m-1; k >= 0; k--){
                if(k < m-1){
                    if(mask_v[i][j][k] && !mask_w[i][j][k]){
                        up_v[i][j][k] = up_v[i > 0 ? i-1 : 0][j < n-1 ? j+1 : j][k+1] + 1;
                    }
                    if(!mask_v[i][j][k] && mask_w[i][j][k]){
                        up_w[i][j][k] = up_w[i > 0 ? i-1 : 0][j < n-1 ? j+1 : j][k+1] + 1;
                    }
                }
            }
        }
    }

    vector<vector<vector<int>>> suff_v(n, vector<vector<int>>(n, vector<int>(m, 0)));
    vector<vector<vector<int>>> suff_w(n, vector<vector<int>>(n, vector<int>(m, 0)));
    for(int i = 0; i < n; i++){
        for(int j = n-1; j >= i; j--){
            for(int k = m-1; k >= 0; k--){
                int imax_v = i > 0 ? suff_v[i-1][j][k] : up_v[i][j][k];
                int jmax_v = j < n-1 ? suff_v[i][j+1][k] : up_v[i][j][k];
                int kmax_v = k < m-1 ? suff_v[i][j][k+1] : up_v[i][j][k];
                int imax_w = i > 0 ? suff_w[i-1][j][k] : up_w[i][j][k];
                int jmax_w = j < n-1 ? suff_w[i][j+1][k] : up_w[i][j][k];
                int kmax_w = k < m-1 ? suff_w[i][j][k+1] : up_w[i][j][k];

                suff_v[i][j][k] = max(imax_v, max(jmax_v, max(kmax_v, up_v[i][j][k])));
                suff_w[i][j][k] = max(imax_w, max(jmax_w, max(kmax_w, up_w[i][j][k])));
            }
        }
    }

    int max_shift = 0;
    for(int i = 0; i < n; i++){
        for(int j = i; j < n; j++){
            for(int k = 0; k < m; k++){
                max_shift = max(max_shift, max(min(down_v[i][j][k], suff_v[i][k][k]), min(down_w[i][j][k], suff_v[i][j][k])));
            }
        }
    }

    return max_shift*sd;

}