#pragma once

#include <vector>
#include <cassert>

using namespace std;

template <typename T>
class DiagonalMatrix {
public:
    DiagonalMatrix(int size, T init_val) : n(size) {
        if (n == 0) return;
        
        int num_diagonals = 2 * n - 1;
        diagonals.resize(num_diagonals);
        
        for (int d = 0; d < num_diagonals; d++) {
            int len = (d < n) ? (d + 1) : (2 * n - 1 - d);
            diagonals[d] = vector<T>(len, init_val);
        }
    }

    T& at(int i, int j) {
        return const_cast<T&>(static_cast<const DiagonalMatrix&>(*this).at(i, j));
    }
    
    const T& at(int i, int j) const {
        assert(i < n && j < n);
        
        int diagonal_index = i + j;
        int inner_index = (diagonal_index < n) ? i : (n - 1 - j); // Hopefully this will be branchless?
        
        return diagonals[diagonal_index][inner_index];
    }

    int size() const {
        return n;
    }

    int n_diagonals() const {
        return diagonals.size();
    }

    int diagonal_size(int d) const {
        return diagonals[d].size();
    }
    
    pair<int, int> to_cartesian(int d, int k) const {
        int len = (d < n) ? (d + 1) : (2 * n - 1 - d);
        int i, j;
        if (d < n) {
            i = k;
            j = d - k;
        } else {
            j = n - 1 - k;
            i = d - j;
        }
        return make_pair(i, j);
    }
private:
    int n;
    vector<vector<T>> diagonals;
};