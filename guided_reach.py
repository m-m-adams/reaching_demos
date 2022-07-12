import tkinter as tk
from typing import Callable, Union
from pathlib import Path
from datetime import datetime
import math
import random


class guided_reach():
    def __init__(self, root: tk.Tk,
                 target: tuple[float, float] = (0.50, 0.50),
                 height: int = 1000, width: int = 1000,
                 logfile: Path = None,
                 feedback: str = 'guided',
                 participant: str = "Roger",
                 feedback_fn: Callable = lambda h, w, xt, yt, xm, ym: (xm, ym)):
        if logfile == None:
            now = datetime.now()
            current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
            logfile = Path(f"{participant}_trial_{current_time}.csv")
        self.logfile = logfile
        if feedback not in ['reflected', 'rotated', 'both']:
            raise ValueError('type must be one of reflected, rotated, both')
        if feedback == 'reflected':
            real_color = 'green'
            feedback_color = 'red'
        if feedback == 'rotated':
            real_color = 'red'
            feedback_color = 'green'
        if feedback == 'both':
            real_color = 'green'
            feedback_color = 'red'
        self.feedback_fn = feedback_fn
        self.window = root
        self.width = width
        self.height = height
        self.target_p = self.calc_target_location(target, height, width)
        self.feedback_p = target
        self.feedback_r = 25
        self.canvas = tk.Canvas(self.window, width=width,
                                height=height, bg="white")

        self.real_target = self.create_circle(
            -100, -100, r=self.feedback_r, fill=real_color, outline="")

        # just a default position before the mouse is on the canvas
        self.feedback_target = self.create_circle(
            -100, -100, r=self.feedback_r, fill=feedback_color, outline="")
        start = self.canvas.create_rectangle(
            width/2-50, height-100, width/2+50, height, fill="blue")
        self.canvas.tag_bind(start, '<Button-1>', self.start)
        self.canvas.pack()

    def calc_target_location(self, target: tuple[float, float], height: int, width: int) -> tuple[int, int]:
        # limit the target to a location within a central square of half the dimensions of the bounding window
        center_x = width/2
        center_y = height/2
        target_x = target[0]*center_x+center_x/2
        target_y = target[1]*center_y+center_y/2
        return int(target_x), int(target_y)

    def start(self, event: tk.Event):
        self.stime = datetime.now()  # type: ignore
        self.init_log_file()
        self.move_circle(self.real_target,
                         self.target_p[0], self.target_p[1], self.feedback_r)
        self.canvas.bind('<Motion>', self.motion)

    def init_log_file(self):
        with open(self.logfile, 'w') as f:
            line = f"target_x, target_y, feedback_x, feedback_y, mouse_x, mouse_y, elapsed_time\n"
            f.write(line)

    def check_finished(self):
        bbox = self.canvas.bbox(self.real_target)
        collision = self.canvas.find_overlapping(*bbox)
        if len(collision) > 1:
            print(collision)
            self.finished()

    def log(self):
        now = datetime.now()
        elapsed = now-self.stime
        line = f"{self.target_p[0]}, {self.target_p[1]},"\
            f"{self.feedback_p[0]}, {self.feedback_p[1]},"\
            f"{self.mouse_position[0]}, {self.mouse_position[1]},"\
            f"{elapsed}\n"
        with open(self.logfile, 'a') as f:
            f.write(line)

    def calc_feedback_position(self) -> tuple[int, int, int]:
        xt, yt = self.target_p
        xm, ym = self.mouse_position
        x, y = self.feedback_fn(self.height, self.width, xt, yt, xm, ym)
        return *self.clip_to_canvas(x, y), self.feedback_r

    def clip_to_canvas(self, x: int, y: int) -> tuple[int, int]:
        x = max(min(self.width-20, x), 20)
        y = max(min(self.height-20, y), 20)
        return x, y

    def finished(self):
        now = datetime.now()
        elapsed = now-self.stime
        self.elapsed = elapsed
        self.canvas.destroy()
        self.window.quit()

    def create_circle(self, x: int, y: int, r: int = 10, **kwargs):
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def move_circle(self, id: int, x: int, y: int, r: int = None, **kwargs):
        # moves a circle to a new center position
        # coords give the coordinates of the bounding rectangle

        coords: list[float] = self.canvas.coords(id)  # type: ignore
        if r == None:
            r = (coords[2]-coords[0])/2
        return self.canvas.coords(id, x-r, y-r, x+r, y+r, **kwargs)

    def motion(self, event: tk.Event):

        x, y = event.x, event.y
        self.mouse_position = (x, y)
        tx, ty, r = self.calc_feedback_position()
        self.feedback_p = tx, ty
        self.move_circle(self.feedback_target, tx, ty, r)
        self.log()
        self.check_finished()
