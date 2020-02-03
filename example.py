import argparse
import pathlib
import sys

import numpy as np
import cv2

from trackpipe import (
    pipeline,
    transforms
)

# ### Example from Bob Kerner's trackbar, reproduced here ###
class CreateImage(pipeline.Transform):
    def __init__(self, width, height):
        """Load an image"""
        super().__init__()
        self.width = width
        self.height = height

    def draw(self, img):
        """Load an image and return it"""
        return np.zeros((self.height, self.width, 3))


class DrawLine(pipeline.Transform):
    rho = transforms.Param(_max=300, default=100)
    theta = transforms.Param(_max=90, adjust=lambda x: (x / 90.*360)*np.pi/180)
    thickness = transforms.Param(_min=3, _max=10, default=5)

    def __init__(self):
        super().__init__()
        self.x = None
        self.y = None

    def compute_values(self):
        self.x = int(np.cos(self.theta.value) * self.rho.value)
        self.y = int(np.sin(self.theta.value) * self.rho.value)

    def draw(self, img):
        mid = (int(img.shape[1] // 2), int(img.shape[0] // 2))
        cv2.line(
            img,(mid[0] + self.x, mid[1] + self.y),
            mid,
            color=[0,0,255],
            thickness=self.thickness.value
        )
        return img.astype(dtype= np.uint8)


def run_example_1():
    """Example from Bob Kerner's Library in two intermediate steps"""
    transforms = [
        CreateImage(640, 480),
        DrawLine(),
    ]
    pipeline.run_pipe(transforms)


def run_example_2():
    """Gaussian Blur applied to an image, twice just for example"""
    window1 = pipeline.Window([
        transforms.LoadImage('Lenna.png'),
        transforms.GaussianBlur(),
    ])
    window2 = pipeline.Window([
        transforms.GaussianBlur()
    ])
    pipe = [window1, window2]
    pipeline.run_pipe(pipe)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Image Pipeline Demo')
    parser.add_argument('--example', choices=[1, 2], help='Run example 1 or example 2', type=int)
    args = parser.parse_args()

    if args.example == 1:
        run_example_1()
    elif args.example == 2:
        run_example_2()