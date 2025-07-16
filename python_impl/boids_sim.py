# This code is adapted for our purposes from original code online:
# -----------------------------------------------------------------------------
# From Pytnon to Numpy
# Copyright (2017) Nicolas P. Rougier - BSD license
# More information at https://github.com/rougier/numpy-book
# -----------------------------------------------------------------------------
#!/usr/bin/env python
import numpy as np
# import sys
import os
import argparse


class Flock:
    def __init__(self, count=500, sep=1, ali=1, coh=1, sep_rad=50, ali_rad=100, coh_rad=150, width=500, height=250):
        self.num_pts = count
        self.width = width
        self.height = height
        self.min_velocity = 0.5
        self.max_velocity = 2.0
        self.max_acceleration = 0.03
        self.velocity = np.zeros((count, 2), dtype=np.float32)
        self.position = np.zeros((count, 2), dtype=np.float32)

        angle = np.random.uniform(0, 2*np.pi, count)
        self.velocity[:, 0] = np.cos(angle)
        self.velocity[:, 1] = np.sin(angle)
        angle = np.random.uniform(0, 2*np.pi, count)
        radius = min(width, height)/2*np.random.uniform(0, 1, count)
        self.position[:, 0] = width/2 + np.cos(angle)*radius
        self.position[:, 1] = height/2 + np.sin(angle)*radius

        self.sep = sep
        self.ali = ali
        self.coh = coh
        self.sep_rad = sep_rad
        self.ali_rad = ali_rad
        self.coh_rad = coh_rad


    def step(self):

        position = self.position
        velocity = self.velocity
        min_velocity = self.min_velocity
        max_velocity = self.max_velocity
        max_acceleration = self.max_acceleration
        n = len(position)

        dx = np.absolute(np.subtract.outer(position[:, 0], position[:, 0]))
        # dx = np.minimum(dx, self.width-dx)
        dy = np.absolute(np.subtract.outer(position[:, 1], position[:, 1]))
        # dy = np.minimum(dy, self.height-dy)
        distance = np.hypot(dx, dy)

        # Compute common distance masks
        mask_0 = (distance > 0)
        mask_1 = (distance < self.sep_rad)
        mask_2 = (distance < self.ali_rad)
        mask_3 = (distance < self.coh_rad)
        mask_1 *= mask_0
        mask_2 *= mask_0
        mask_3 *= mask_0
        mask_1_count = np.maximum(mask_1.sum(axis=1), 1)
        mask_2_count = np.maximum(mask_2.sum(axis=1), 1)
        mask_3_count = np.maximum(mask_3.sum(axis=1), 1)

        # Separation
        mask, count = mask_1, mask_1_count
        target = np.dstack((dx, dy))
        target = np.divide(target, distance.reshape(n, n, 1)**2, out=target,
                           where=distance.reshape(n, n, 1) != 0)
        steer = (target*mask.reshape(n, n, 1)).sum(axis=1)/count.reshape(n, 1)
        norm = np.sqrt((steer*steer).sum(axis=1)).reshape(n, 1)
        steer = max_velocity*np.divide(steer, norm, out=steer,
                                       where=norm != 0)
        steer -= velocity

        # Limit acceleration
        norm = np.sqrt((steer*steer).sum(axis=1)).reshape(n, 1)
        steer = np.multiply(steer, max_acceleration/norm, out=steer,
                            where=norm > max_acceleration)

        separation = steer

        # Alignment
        # ---------------------------------------------------------------------
        # Compute target
        mask, count = mask_2, mask_2_count
        target = np.dot(mask, velocity)/count.reshape(n, 1)

        # Compute steering
        norm = np.sqrt((target*target).sum(axis=1)).reshape(n, 1)
        target = max_velocity * np.divide(target, norm, out=target,
                                          where=norm != 0)
        steer = target - velocity

        # Limit acceleration
        norm = np.sqrt((steer*steer).sum(axis=1)).reshape(n, 1)
        steer = np.multiply(steer, max_acceleration/norm, out=steer,
                            where=norm > max_acceleration)
        alignment = steer

        # Cohesion
        # ---------------------------------------------------------------------
        # Compute target
        mask, count = mask_3, mask_3_count
        target = np.dot(mask, position)/count.reshape(n, 1)

        # Compute steering
        desired = target - position
        norm = np.sqrt((desired*desired).sum(axis=1)).reshape(n, 1)
        desired *= max_velocity / norm
        steer = desired - velocity

        # Limit acceleration
        norm = np.sqrt((steer*steer).sum(axis=1)).reshape(n, 1)
        steer = np.multiply(steer, max_acceleration/norm, out=steer,
                            where=norm > max_acceleration)
        cohesion = steer

        # ---------------------------------------------------------------------
        acceleration = self.sep*separation + self.ali*alignment + self.coh*cohesion
        velocity += acceleration

        norm = np.sqrt((velocity*velocity).sum(axis=1)).reshape(n, 1)
        velocity = np.multiply(velocity, max_velocity/norm, out=velocity,
                               where=norm > max_velocity)
        velocity = np.multiply(velocity, min_velocity/norm, out=velocity,
                               where=norm < min_velocity)
        position += velocity

        # Wraparound
        # position += (self.width, self.height)
        # position %= (self.width, self.height)


    def simulate(self, num_steps, seed=None, filename=None):
        if seed is not None:
            np.random.seed(seed)
        if filename is not None:
            f = open(filename, "a")
            f.write(f"{self.num_pts}\n{self.width} {self.height}\n")
        for _ in range(num_steps):
            self.step()
            if filename is not None:
                np.savetxt(f, self.position, fmt='%.8f', newline='\n')
        if filename is not None:
            f.close()



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="boids_sim", description="Script used to simulate boids quickly")
    parser.add_argument("outfile", type=str, help="Output file to save data to")
    parser.add_argument("num_pts", type=int, help="Number of points in simulation")
    parser.add_argument("sep", type=float, help="Separation parameter used in motion calculations")
    parser.add_argument("ali", type=float, help="Alignment parameter used in motion calculations")
    parser.add_argument("coh", type=float, help="Cohesion parameter used in motion calculations")
    parser.add_argument("-ns", "--num_steps", default=500, type=int, help="Number of steps to run simulation")
    parser.add_argument("-sr", "--sep_rad", default=50, type=float, help="Separation radius used in motion calculations")
    parser.add_argument("-ar", "--ali_rad", default=100, type=float, help="Alignment radius used in motion calculations")
    parser.add_argument("-cr", "--coh_rad", default=150, type=float, help="Cohesion radius used in motion calculations")
    # parser.add_argument("-w", "--width", default=500, type=int, help="Width of toroidal enviornment")
    # parser.add_argument("-h", "--height", default=250, type=int, help="Cohesion radius used in motion calculations")
    args = parser.parse_args()

    num_pts = args.num_pts
    sep = args.sep
    ali = args.ali
    coh = args.coh
    sep_rad = args.sep_rad
    ali_rad = args.ali_rad
    coh_rad = args.coh_rad
    num_steps = args.num_steps
    outfile = args.outfile # if args.outfile else f"{sep}_{ali}_{coh}"
    
    if os.path.exists(outfile):
        os.remove(outfile)

    # seed = np.random.randint(0, 1<<31)
    # if not outfile: outfile = f"boids_{seed}.txt"
    flock = Flock(num_pts, sep, sep_rad, ali, ali_rad, coh, coh_rad)
    flock.simulate(num_steps, filename=outfile)