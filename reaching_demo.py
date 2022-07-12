#!/usr/bin/env python
from guided_reach import guided_reach
import tkinter as tk
from typing import Callable, Union
from pathlib import Path
from datetime import datetime
import math
import random
import numpy as np


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


# feedback_fn: Callable = lambda xt, yt, xm, ym: (xm, ym)


def linear(h, w, xt, yt, xm, ym):
    return xm, ym


def reflect_x(h, w, xt, yt, xm, ym):
    xf = w-xm
    return xf, ym


def rotate_90(h, w, xt, yt, xm, ym):
    x_r = xm-h/2
    y_r = ym-h/2
    radius, angle = cart2pol(x_r, y_r)

    angle -= 1.57
    xz, yz = pol2cart(radius, angle)
    return xz+w/2, yz+h


def run_experiment(window: tk.Tk, name: str, type: str, feedback_fn: Callable):

    logfolder = Path(name)
    logfolder.mkdir(parents=True, exist_ok=True)

    logfile = Path(logfolder, f"trial_{trial}.csv")

    # select a random spot on the canvas to target
    target = random.random(), random.random()

    gr = guided_reach(window, target, height=1080,
                      width=1920, logfile=logfile, feedback=type, feedback_fn=feedback_fn)
    window.mainloop()
    return gr.elapsed.total_seconds()


if __name__ == "__main__":
    n_trials = 2

    window = tk.Tk()
    r_times = []
    # for trial in range(n_trials):
    #     r_times.append(run_experiment(window, 'baseline', 'real'))
    # print(sum(r_times)/n_trials)
    r_times = []
    for trial in range(n_trials):
        r_times.append(run_experiment(
            window, 'reflected', 'reflected', reflect_x))
    for trial in range(n_trials):
        r_times.append(run_experiment(
            window, 'reflected', 'reflected', rotate_90))
    print(sum(r_times)/n_trials)
    r_times = []
