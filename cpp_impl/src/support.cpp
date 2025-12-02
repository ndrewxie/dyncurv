#include "support.hpp"

float dist_euc(vector<float>& p1, vector<float>& p2) {
    float sum = 0.0;
    for (int i = 0; i < min(p1.size(), p2.size()); i++) {
        sum += powf(p1[i] - p2[i], 2.0);
    }
    return sqrt(sum);
}

float dist_torus(vector<float>& p1, vector<float>& p2, vector<float>& bounds) {
    float sum = 0.0;
    for (int i = 0; i < min(p1.size(), p2.size()); i++) {
        float diff = abs(p1[i] - p2[i]);
        sum += powf(min(diff, bounds[i]-diff), 2.0);
    }
    return sqrt(sum);
}

void update_dist_mat(PointCloud& pc, vector<float>& dmat, vector<float>& bounds) {
    int n_pts = pc.size();
    for (int i = 0; i < n_pts; i++) {
        for (int j = 0; j < n_pts; j++) {
            int indx = i * n_pts + j;
            float d = bounds[0]<=0 || bounds[1]<=0 ? dist_euc(pc[i], pc[j]) : dist_torus(pc[i], pc[j], bounds);
            dmat[indx] = min(dmat[indx], d);
        }
    }
}

pair<float, float> compute_hn(int n_pts, vector<float>& dist_matrix) {
    float t_b = 0.0;
    float t_d = numeric_limits<float>::infinity();
    for (int x0 = 0; x0 < n_pts; x0++) {
        float max_1 = 0.0;
        float max_2 = 0.0;
        for (int x1 = 0; x1 < n_pts; x1++) {
            float dist = dist_matrix[x0 * n_pts + x1];
            if (dist > max_1) {
                max_2 = max_1;
                max_1 = dist;
            }
            else if (dist > max_2) {
                max_2 = dist;
            }
        }
        t_b = max(t_b, max_2);
        t_d = min(t_d, max_1);
    }
    if (t_d - t_b > 1e-9 && t_d > 1e-9) {
        return make_pair(t_b, t_d);
    }
    return make_pair(0.0, 0.0);
}

Support::Support(DynPointCloud& dpc, vector<float>& bounds, vector<float>& distances) 
    : mat(dpc.size(), make_pair(0.0, 0.0)) {
    int n_time = dpc.size();
    int n_pts = dpc[0].size();
    if (distances.size() < n_pts * n_pts) {
        distances.resize(n_pts * n_pts, std::numeric_limits<float>::infinity());
    }
    for (int t0 = 0; t0 < n_time; t0++) {
        std::fill(distances.begin(), distances.end(), std::numeric_limits<float>::infinity());
        for (int t1 = t0; t1 < n_time; t1++) {
            update_dist_mat(dpc[t1], distances, bounds);
            auto h1_result = compute_hn(n_pts, distances);
            this->at(t0, t1) = h1_result;
        }
    }

    this->build_indices();
}

void Support::build_indices() {
    indices.clear();
    for (int d = 0; d < mat.n_diagonals(); d++) {
        for (int k = 0; k < mat.diagonal_size(d); k++) {
            pair<int, int> indx = mat.to_cartesian(d, k);
            pair<float, float> elem = mat.at(indx.first, indx.second);
            if (elem.first < elem.second) { indices.push_back(indx); }
        }
    }
}
