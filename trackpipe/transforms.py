from pathlib import Path

import cv2
import numpy as np

from .pipeline import (
    Transform,
    Param
)


def scale(factor): return lambda x: x*factor


def make_odd(x):
    return x if x % 2 != 0 else x + 1


class LoadImage(Transform):
    def __init__(self, path):
        """Loads and returns an img at path"""
        super().__init__()
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Path {p} does not exist")
        self.img = cv2.imread(path)

    def draw(self, img):
        return self.img


class GaussianBlur(Transform):
    """Performs a Gaussian Blur"""
    size = Param(_max=100, adjust=make_odd)
    sigma = Param(label='Sigma', _max=10)

    def draw(self, img):
        return cv2.GaussianBlur(
            img,
            (self.size.value, self.size.value),
            self.sigma.value
        )
