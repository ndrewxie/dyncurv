import numpy as np
from dataclasses import dataclass, astuple

@dataclass
class TimeConstants:
    T_MIN: float
    T_MAX: float
    DELTA: float

    def __iter__(self): # Ty to https://stackoverflow.com/a/70753113/19459162
        return iter(astuple(self))

constants = TimeConstants(0, 2, 0.02)
# T_MIN = 0
# T_MAX = 2
# DELTA = 0.02 # Currently, DELTA needs to divide (T_MAX - T_MIN). Might fix later

# Static case to test d_2
x_pts = [
    lambda t: np.array([1.0, 0.0]),
    lambda t: np.array([-1.0, 0.0]),
    lambda t: np.array([0.0, 1.0]), 
    lambda t: np.array([0.0, -1.0])
]
y_pts = [
    lambda t: np.array([1.7, 0.0]),
    lambda t: np.array([-1.0, 0.0]),
    lambda t: np.array([0.0, 1.0]), 
    lambda t: np.array([0.0, -1.0])
]

"""
# H_1 example
x_pts = [
    lambda t: np.array([1.0 + (0.5 * t if t <= 1.0 else 0.5 + 0.75 * (t - 1.0)), 0.0]),
    lambda t: np.array([-1.0, 0.0]),
    lambda t: np.array([0.0, 1.0]), 
    lambda t: np.array([0.0, -1.0])
]
y_pts = [
    lambda t: np.array([1.0 + (0.5 * t if t <= 1.0 else 0.5 + 0.75 * (t - 1.0)), 0.0]),
    lambda t: np.array([-1.0, 0.0]),
    lambda t: np.array([0.0, 1.0 + np.sin(np.pi * t)]), 
    lambda t: np.array([0.0, -1.0])
]
"""

"""
# H_2 example
x_pts = [
    lambda t: np.array([1.0, 0.0, 0.0]),
    lambda t: np.array([-1.0, 0.0, 0.0]),
    lambda t: np.array([0.0, 1.0, 0.0]),
    lambda t: np.array([0.0, -1.0, 0.0]),
    lambda t: np.array([0.0, 0.0, 1.0]),
    lambda t: np.array([0.0, 0.0, -1.0])
]
y_pts = [
    lambda t: np.array([1.0 + np.sin(2.0 * np.pi * t), 0.0, 0.0]),
    lambda t: np.array([-1.0, 0.0, 0.0]),
    lambda t: np.array([0.0, 1.0, 0.0]),
    lambda t: np.array([0.0, -1.0, 0.0]),
    lambda t: np.array([0.0, 0.0, 1.0]),
    lambda t: np.array([0.0, 0.0, -1.0])
]
"""