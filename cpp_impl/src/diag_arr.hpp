#pragma once

#include <vector>
#include <utility>
#include <algorithm>

using namespace std;

template <typename T>
class DiagonalMatrix {
public:
    DiagonalMatrix(int input_n, T init_val) : n(input_n) {
        if (n <= 0) {
            n = 0;
            return;
        }

        num_diagonals = 2 * n - 1;
        start_i.resize(num_diagonals);
        diag_lengths.resize(num_diagonals);
        offsets.resize(num_diagonals + 1);

        int total = 0;
        for (int d = 0; d < num_diagonals; ++d) {
            int i_min = std::max(0, d - (n - 1));
            int i_max = std::min(n - 1, d / 2);
            int len = (i_max >= i_min) ? (i_max - i_min + 1) : 0;
            start_i[d] = i_min;
            diag_lengths[d] = len;
            offsets[d] = total;
            total += len;
        }
        offsets[num_diagonals] = total;

        data.assign(total, init_val);
    }

    inline T& at(int i, int j) {
        int d = i + j;
        return data[offsets[d] + (i - start_i[d])];
    }

    inline const T& at(int i, int j) const {
        int d = i + j;
        return data[offsets[d] + (i - start_i[d])];
    }

    inline int size() const { return n; }

    inline int n_diagonals() const { return num_diagonals; }
    
    inline int diagonal_size(int d) const noexcept { return diag_lengths[d]; }

    inline int diagonal_offset(int d) const { return offsets[d]; }

    inline pair<int,int> to_cartesian(int d, int k) const {
        int i = start_i[d] + k;
        int j = d - i;
        return std::make_pair(i, j);
    }

private:
    int n;
    int num_diagonals;
    vector<T> data;
    vector<int> offsets;
    vector<int> diag_lengths;
    vector<int> start_i;
};
