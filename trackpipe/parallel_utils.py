from pathlib import Path

import numpy as np
import cv2

from . import pipeline


def load_images(img_paths):
    """Load images into [{'path': ..., 'img': np.array}, ...] for images

    Args:
        img_paths ([str]): paths to images
    """
    images = []
    for path in img_paths:
        img = Path(path)
        if not img.exists():
            raise FileNotFoundError(f'File {path} not found')
        images.append({
            'path': path,
            'img': cv2.imread(path)
        })
    return images


def create_slave_windows(transforms, master_win_name, images):
    """Create windows that will not have trackbars

    Args:
        transforms ([Transform]): list of transforms in order of execution
        master_win_name (str): Name of the master window with trackbar controls
        images ([{}]): list of {'path': ..., 'img': np.array}'s for slaves
    """
    slaves = []
    for img in images:
        win = pipeline.Window(
            transforms, name=img['path'], track_src=master_win_name)
        cv2.namedWindow(
            win.name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO|cv2.WINDOW_GUI_EXPANDED)
        slaves.append(win)
    return slaves


def create_master_trackbars(window):
    """Create trackbars for master window

    Args:
        window (Window): window that will be the master with trackbar conrols
    """
    cv2.namedWindow(
        window.name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO|cv2.WINDOW_GUI_EXPANDED)
    for t in window.transforms:
        for k, v in t.params.items():
            cv2.createTrackbar(k, window.name, v._pos, v.max, pipeline.nothing)
