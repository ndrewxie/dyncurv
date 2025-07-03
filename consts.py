import numpy as np

T_MIN = 0
T_MAX = 2
DELTA = 0.02 # Currently, DELTA needs to divide (T_MAX - T_MIN). Might fix later

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