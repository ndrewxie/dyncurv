import tkinter as tk
import numpy as np
import argparse

from boids_sim import Flock


class BoidsApp:
    def __init__(self, root):
        self.width, self.height = 500, 250
        self.params = {
            'num_boids':         (tk.IntVar(value=50),      1,   250  , 1    , 'num_pts'),
            'separation':        (tk.DoubleVar(value=0.5),  0.0, 5.0  , 0.05, 'sep'    ),
            'alignment':         (tk.DoubleVar(value=0.5),  0.0, 5.0  , 0.05, 'ali'    ),
            'cohesion':          (tk.DoubleVar(value=0.5),  0.0, 5.0  , 0.05, 'coh'    ),
            'separation_radius': (tk.DoubleVar(value=50.0), 0.0, 350.0, 0.5  , 'sep_rad'),
            'alignment_radius':  (tk.DoubleVar(value=100.0), 0.0, 350.0, 0.5  , 'ali_rad'),
            'cohesion_radius':   (tk.DoubleVar(value=150.0), 0.0, 350.0, 0.5  , 'coh_rad')
        }

        self.root = root
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=len(self.params)+2)

        for row, (name, (var, lo, hi, res, field)) in enumerate(self.params.items()):
            label = tk.Label(root, text=name)
            label.grid(row=row, column=1)
            slider = tk.Scale(root, from_=lo, to=hi, resolution=res,
                              orient=tk.HORIZONTAL, variable=var, length=200,
                              command=None if name=="num_boids" else lambda new_val, field=field : setattr(self.flock, field, float(new_val)))
            slider.grid(row=row, column=2)

        self.show_velocities = tk.BooleanVar(value=False)
        vel_checkbox = tk.Checkbutton(root, text="Show Velocities", variable=self.show_velocities)
        vel_checkbox.grid(row=row+1, column=1, columnspan=2)

        restart_btn = tk.Button(root, text="Restart Simulation", command=self.restart_simulation)
        restart_btn.grid(row=row+2, column=1, columnspan=2, pady=10)

        # Initialize boids
        self.flock = Flock(*[tup[0].get() for tup in self.params.values()])
        
        self.animate()

    def animate(self):
        L = 4
        ROT_NEG_120 = np.array([[-1/2, np.sqrt(3)/2], [-np.sqrt(3)/2, -1/2]])
        ROT_ZERO = np.eye(2)
        ROT_POS_120 = np.array([[-1/2, -np.sqrt(3)/2], [np.sqrt(3)/2, -1/2]])
        ROT_MAT = np.array([L*ROT_NEG_120, 2*L*ROT_ZERO, L*ROT_POS_120])#, np.zeros((2,2))])
        
        self.flock.step()

        triangle_list = []
        vel_list = []
        for i in range(self.flock.num_pts):
            pos, vel = self.flock.position[i].copy(), self.flock.velocity[i].copy()
            pos[1] = self.height - pos[1]
            vel[1] *= -1

            unit = vel / np.linalg.norm(vel)
            points = ROT_MAT @ unit + pos
            triangle_list.append([tuple(pt) for pt in points])
            
            if self.show_velocities.get():
                center = np.array([self.width/2, self.height/2])
                endpts = [center, center + 4*(points[1] - pos)]
                vel_list.append([tuple(pt) for pt in endpts])

        self.canvas.delete("all")
        for points in triangle_list:
            self.canvas.create_polygon(points, fill='black')
        if self.show_velocities.get():
            for a, b in vel_list:
                self.canvas.create_line(a, b, arrow=tk.LAST, fill="red", width="2p")

        self.root.after(10, self.animate)

    def restart_simulation(self):
        self.flock = Flock(*[tup[0].get() for tup in self.params.values()])
        for _ in range(0, 2000):
            self.flock.step()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(prog="boids_viz", description="Program to visualize boids behaviors")
    # parser.add_argument("-v", "--velocities", help="Show velocities in visualiz", action="store_false")
    # args = parser.parse_args()

    root = tk.Tk()
    root.title("Boids Simulator")
    app = BoidsApp(root)
    root.mainloop()