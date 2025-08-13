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

    if (a1 >= b1) {
        return { empty, empty };
    }
    if (a2 <= a1 && b1 <= b2) {
        return { empty, empty };
    }
    if (a2 > b2 || b2 < a1 || a2 > b1) {
        return { i1, empty };
    }
    IntervalArr segments = { empty, empty };
    if (a1 < a2) {
        segments[0] = make_pair(a1, min(b1, a2));
    }
    if (b2 < b1) {
        segments[1] = make_pair(max(a1, b2), b1);
    }
    return segments;
}

template<bool should_write>
bool filter_intervals(IntervalArr& segs, Interval range1, Interval range2) {
    bool ret_val = false;
    for (int i = 0; i < segs.size(); i++) {
        double low = max(segs[i].first, max(range1.first, range2.first));
        double high = min(segs[i].second, min(range1.second, range2.second));
        ret_val = ret_val | (low < high);        
        if (should_write) {
            segs[i] = make_pair(low, high);
        }
    }
    return ret_val;
}

double compute_max_rad(
    int i, int j, IntervalArr seg, const Support& sup_v, int curr_high, double sd_v
) {
    int n = sup_v.size();
    int shift_limit_out = min(i, n - j - 1);
    int shift_limit_in = (j - i + 1) / 2;

    int low = curr_high;
    int high = shift_limit_out;
    
    int max_rad = high+1;
    while (low <= high) {
        int mid = low + (high-low)/2;
        double midf = double(mid);
        
        int shift_in = min(shift_limit_in, mid);
        int shift_out = mid;
        Interval mid_seg_low = make_pair(
            sup_v.at(i+shift_in, j-shift_in).first + sd_v * midf, 
            sup_v.at(i+shift_in, j-shift_in).second + sd_v * midf
        );
        Interval mid_seg_high = make_pair(
            sup_v.at(i-shift_out, j+shift_out).first - sd_v * midf, 
            sup_v.at(i-shift_out, j+shift_out).second - sd_v * midf
        );

        bool is_nonempty = filter_intervals<false>(seg, mid_seg_low, mid_seg_high);
        if (is_nonempty) {
            low = mid + 1;
        }
        else {
            max_rad = mid;
            high = mid - 1;
        }
    }
    return max_rad;
}

double compute_left_d2(const Support& sup_v, const Support& sup_w, double sd_v, double sd_w) {
    assert(sup_v.size() == sup_w.size());

    Interval full = make_pair(-numeric_limits<double>::infinity(), numeric_limits<double>::infinity());

    double max_d2 = 0.0;
    for (auto& indices : sup_v.indices) {
        int i = indices.first;
        int j = indices.second;
        Interval int_v = make_pair(sup_v.at(i, j).first, sup_v.at(i, j).second);
        Interval int_w = make_pair(sup_w.at(i, j).first, sup_w.at(i, j).second);
        IntervalArr delta = subtract_ints(int_v, int_w);
        bool delta_nonempty = filter_intervals<true>(delta, full, full);
        if (!delta_nonempty) { continue; } 
        double max_rad = compute_max_rad(i, j, delta, sup_v, max_d2, sd_v);
        max_d2 = max(max_d2, max_rad);
    }
    return max_d2 * sd_v;
}

double compute_d2(const Support& sup_v, const Support& sup_w, double sd_v, double sd_w) {
    return max(
        compute_left_d2(sup_v, sup_w, sd_v, sd_v),
        compute_left_d2(sup_w, sup_v, sd_v, sd_w)
    );
}
