import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
from datetime import datetime

T_MIN = 0
T_MAX = 2
DELTA = 0.01

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

def compute_Hn(dist_matrix):
    n = len(dist_matrix)
    t_b = 0.0
    t_d = float('inf')
    
    for x0 in range(n):
        distances = []
        for i in range(n):
            if i != x0:
                distances.append(dist_matrix[x0, i])
        
        distances.sort(reverse=True)
        
        t_b = max(t_b, distances[1])
        t_d = min(t_d, distances[0])
    
    if t_d - t_b > 1e-9 and t_d > 1e-9:
        return (t_b, t_d)
    else:
        return None

def compute_dist(t, in_pts):
    points = [in_pts[i](t) for i in range(len(in_pts))]
    points_arr = np.array(points)
    dist_matrix = np.linalg.norm(points_arr[:, None] - points_arr[None, :], axis=2)
    return dist_matrix

def analyze(in_pts):
    time_points = np.arange(T_MIN, T_MAX + DELTA, DELTA)
    results = []
    
    for i in range(len(time_points)):
        for j in range(i, len(time_points)):
            a = time_points[i]
            b = time_points[j]
            
            distance_matrices = []
            interval_times = np.arange(a, b + DELTA, DELTA)
            
            for t in interval_times:
                if t <= T_MAX:
                    distance_matrices.append(compute_dist(t, in_pts))
            
            if distance_matrices:
                min_dist = np.stack(distance_matrices).min(axis=0)
                h1_result = compute_Hn(min_dist)
                
                if h1_result is not None:
                    birth, death = h1_result
                    results.append({
                        'interval': (a, b),
                        'birth': birth,
                        'death': death
                    })
    
    return results

def create_box_mesh(a, b, birth, death):
    x = [a, a+DELTA, a+DELTA, a, a, a+DELTA, a+DELTA, a]
    y = [b, b, b+DELTA, b+DELTA, b, b, b+DELTA, b+DELTA]
    z = [birth, birth, birth, birth, death, death, death, death]
    
    i = [0, 0, 0, 0, 1, 1, 2, 2, 4, 4]
    j = [1, 2, 4, 7, 2, 5, 3, 6, 5, 6]
    k = [2, 3, 7, 3, 5, 6, 7, 7, 6, 7]
    
    return x, y, z, i, j, k

def plot_3d(data, color):
    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    
    vertex_offset = 0
    for item in data:
        a, b = item['interval']
        birth = item['birth']
        death = item['death']
        
        x, y, z, i, j, k = create_box_mesh(a, b, birth, death)
        
        all_x.extend(x)
        all_y.extend(y)
        all_z.extend(z)
        
        all_i.extend([idx + vertex_offset for idx in i])
        all_j.extend([idx + vertex_offset for idx in j])
        all_k.extend([idx + vertex_offset for idx in k])
        
        vertex_offset += len(x)
    
    fig = go.Figure(data=[
        go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            color=color,
            opacity=0.6,
            hoverinfo='none'
        )
    ])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='t_0',
            yaxis_title='t_1',
            zaxis_title='DELTA',
            dragmode='turntable',
            camera=dict(eye=dict(x=0, y=0, z=3), up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0))
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

print("X")
results_x = analyze(x_pts)
print("Y")
results_y = analyze(y_pts)
print("Plotting")
support_x_pts = [item['interval'] for item in results_x]
support_y_pts = [item['interval'] for item in results_y]
min_z_x = min(item['birth'] for item in results_x) if results_x else 0
min_z_y = min(item['birth'] for item in results_y) if results_y else 0

fig = go.Figure()

fig_x = plot_3d(results_x, color='blue')
fig_y = plot_3d(results_y, color='red')
for trace in fig_x.data:
    trace.visible = True
    trace.name = "X Points"
    fig.add_trace(trace)
for trace in fig_y.data:
    trace.visible = False
    trace.name = "Y Points"
    fig.add_trace(trace)
fig.add_trace(go.Scatter3d(
    x=[pt[0] for pt in support_x_pts], 
    y=[pt[1] for pt in support_x_pts], 
    z=[min_z_x] * len(support_x_pts),
    mode='markers', name='X Support', 
    marker=dict(color='black', opacity=0.5, size=1),
    visible=True
))
fig.add_trace(go.Scatter3d(
    x=[pt[0] for pt in support_y_pts], 
    y=[pt[1] for pt in support_y_pts], 
    z=[min_z_y] * len(support_y_pts),
    mode='markers', name='Y Support', 
    marker=dict(color='black', opacity=0.5, size=2),
    visible=False
))
fig.update_layout(
    fig_x.layout,
    updatemenus=[dict(
        type="buttons",
        buttons=[
            dict(args=[{"visible": [True] * len(fig_x.data) + [False] * len(fig_y.data) + [True, False]}], label="Show V"),
            dict(args=[{"visible": [False] * len(fig_x.data) + [True] * len(fig_y.data) + [False, True]}], label="Show W")
        ]
    )]
)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output_{(len(x_pts) - 2)//2}_{timestamp}.html"
fig.write_html(filename)
fig.show()
input("Press any key to exit")
