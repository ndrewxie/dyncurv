#pragma once

#include <array>
#include <algorithm>
#include <limits>
#include <cmath>
#include <assert.h>

#include "support.hpp"

using namespace std;

typedef pair<double, double> Interval;
typedef array<Interval, 2> IntervalArr;

IntervalArr subtract_ints(Interval i1, Interval i2) {
    Interval empty = make_pair(1.0, 0.0);
    double a1 = i1.first, b1 = i1.second;
    double a2 = i2.first, b2 = i2.second;

    if (a1 > b1) {
        return { empty, empty };
    }
    if (a2 > b2 || b2 < a1 || a2 > b1) {
        return { i1, empty };
    }
    if (a2 <= a1 && b1 <= b2) {
        return { empty, empty };
    }
    IntervalArr segments = { empty, empty };
    int n = 0;
    if (a1 < a2) {
        segments[n] = make_pair(a1, min(b1, a2));
        n += 1;
    }
    if (b2 < b1) {
        segments[n] = make_pair(max(a1, b2), b1);
        n += 1;
    }
    return segments;
}

bool filter_intervals(IntervalArr& segs, Interval range1, Interval range2, bool write) {
    bool ret_val = false;
    for (int i = 0; i < segs.size(); i++) {
        double low1 = max(range1.first, segs[i].first);
        double high1 = min(range1.second, segs[i].second);
        double low2 = max(range2.first, low1);
        double high2 = min(range2.second, high1);
        ret_val = ret_val || (low2 < high2);        
        if (write) {
            segs[i] = make_pair(low2, high2);
        }
    }
    return ret_val;
}

double compute_max_rad(
    int i, int j, IntervalArr seg, Support& sup_v, Support& sup_w, int curr_high, double scale_delta
) {
    int m = sup_v.size();
    int n = sup_v[0].size();

    int low = curr_high+1;
    int high = min(min((j - i) / 2, n - j - 1), i);
    
    int max_rad = 0;
    while (low <= high) {
        int mid = low + (high-low)/2;
        double midf = double(mid);
        Interval mid_seg_low = make_pair(
            sup_v[i+mid][j-mid].first + scale_delta * midf, 
            sup_v[i+mid][j-mid].second + scale_delta * midf
        );
        Interval mid_seg_high = make_pair(
            sup_w[i-mid][j+mid].first - scale_delta * midf, 
            sup_w[i-mid][j+mid].second - scale_delta * midf
        );
        bool is_nonempty = filter_intervals(seg, mid_seg_low, mid_seg_high, false);
        if (is_nonempty) {
            max_rad = mid;
            low = mid + 1;
        }
        else {
            high = mid - 1;
        }
    }
    return max_rad;
}

double compute_left_d2(Support& sup_v, Support& sup_w, double scale_delta) {
    assert(sup_v.size() == sup_w.size());
    assert(sup_v[0].size() == sup_w[0].size());

    Interval full = make_pair(-numeric_limits<double>::infinity(), numeric_limits<double>::infinity());

    int m = sup_v.size();
    int n = sup_v[0].size();
    double max_d2 = 0.0;
    for (int i = 0; i < m; i++) {
        for (int j = i; j < n; j++) {
            Interval int_v = make_pair(sup_v[i][j].first, sup_v[i][j].second);
            Interval int_w = make_pair(sup_w[i][j].first, sup_w[i][j].second);
            IntervalArr delta = subtract_ints(int_v, int_w);
            bool delta_nonempty = filter_intervals(delta, full, full, true);
            if (!delta_nonempty) { continue; } 
            double max_rad = compute_max_rad(i, j, delta, sup_v, sup_w, max_d2, scale_delta);
            max_d2 = max(max_d2, max_rad);
        }
    }

    return max_d2 * scale_delta;
}

double compute_d2(Support& sup_v, Support& sup_w, double scale_delta) {
    return max(
        compute_left_d2(sup_v, sup_w, scale_delta),
        compute_left_d2(sup_w, sup_v, scale_delta)
    );
}