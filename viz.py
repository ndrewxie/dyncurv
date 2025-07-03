from consts import *
import plotly.graph_objects as go
import plotly.offline as pyo
from datetime import datetime

def create_box_mesh(a, b, birth, death):
    x = [a, a+DELTA, a+DELTA, a, a, a+DELTA, a+DELTA, a]
    y = [b, b, b+DELTA, b+DELTA, b, b, b+DELTA, b+DELTA]
    z = [birth, birth, birth, birth, death, death, death, death]
    
    i = [0, 0, 0, 0, 1, 1, 2, 2, 4, 4]
    j = [1, 2, 4, 7, 2, 5, 3, 6, 5, 6]
    k = [2, 3, 7, 3, 5, 6, 7, 7, 6, 7]
    
    return x, y, z, i, j, k

def plot_3d(birth_mat, death_mat, color):
    t_pts = np.arange(T_MIN, T_MAX + DELTA, DELTA)
    n_steps = len(t_pts)
    
    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    
    v_offset = 0
    for i in range(n_steps):
        for j in range(i, n_steps):
            birth = birth_mat[i, j]
            death = death_mat[i, j]
            
            if birth < death:
                a = t_pts[i]
                b = t_pts[j]
                
                x, y, z, idx_i, idx_j, idx_k = create_box_mesh(a, b, birth, death)
                
                all_x.extend(x)
                all_y.extend(y)
                all_z.extend(z)
                
                all_i.extend([idx + v_offset for idx in idx_i])
                all_j.extend([idx + v_offset for idx in idx_j])
                all_k.extend([idx + v_offset for idx in idx_k])
                
                v_offset += len(x)
    
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

def plot_data(birth_mat_x, death_mat_x, birth_mat_y, death_mat_y):
    fig = go.Figure()

    fig_x = plot_3d(birth_mat_x, death_mat_x, color='blue')
    fig_y = plot_3d(birth_mat_y, death_mat_y, color='red')
    for trace in fig_x.data:
        trace.visible = True
        trace.name = "X Points"
        fig.add_trace(trace)
    for trace in fig_y.data:
        trace.visible = False
        trace.name = "Y Points"
        fig.add_trace(trace)
    
    t_pts = np.arange(T_MIN, T_MAX + DELTA, DELTA)
    n_steps = len(t_pts)
    support_x_pts = [(t_pts[i], t_pts[j]) 
                    for i in range(n_steps) 
                    for j in range(i, n_steps) if birth_mat_x[i, j] < death_mat_x[i, j]]
    support_y_pts = [(t_pts[i], t_pts[j]) 
                        for i in range(n_steps) 
                        for j in range(i, n_steps) if birth_mat_y[i, j] < death_mat_y[i, j]]
    min_z_x = np.min(birth_mat_x[birth_mat_x < death_mat_x]) if len(support_x_pts) > 0 else 0
    min_z_y = np.min(birth_mat_y[birth_mat_y < death_mat_y]) if len(support_y_pts) > 0 else 0
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
    filename = f"./outputs/output_{(len(x_pts) - 2)//2}_{timestamp}.html"
    fig.write_html(filename)
    #fig.show()
