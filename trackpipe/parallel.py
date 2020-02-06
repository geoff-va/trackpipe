from pathlib import Path

import numpy as np
import cv2

from . import utils, pipeline


def _load_images(img_paths):
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


def _create_slave_windows(transforms, master_win_name, images):
    slaves = []
    for img in images:
        win = pipeline.Window(
            transforms, name=img['path'], track_src=master_win_name)
        print(f"creating window {win.name}")
        cv2.namedWindow(
            win.name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO|cv2.WINDOW_GUI_EXPANDED)
        slaves.append(win)
    return slaves


def _create_master_trackbars(window):
    """Create trackbars for master window"""
    cv2.namedWindow(
        window.name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO|cv2.WINDOW_GUI_EXPANDED)
    for t in window.transforms:
        for k, v in t.params.items():
            cv2.createTrackbar(k, window.name, v._pos, v.max, pipeline.nothing)



def run_parallel(transforms, img_paths):
    windows = utils.collect_windows(transforms)
    if len(windows) > 1:
        raise ValueError('Must only be a single window for parallel processing')
    utils.check_dup_win_labels(windows)

    # Get all images with their loaded img content
    images = _load_images(img_paths)

    # Setup the master window with the trackbars
    master_win = windows[0]
    _create_master_trackbars(master_win)
    master_win.name = images[0]['path']
    master_win.track_src = images[0]['path']

    # Create slave windows
    slave_wins = _create_slave_windows(transforms, master_win.name, images[1:])
    all_windows = [master_win] + slave_wins

    # Loop performing transforms in each window
    while True:
        # Copy all images
        for img in images:
            img['img'] = np.copy(img['img'])

        # Break on escape key
        k = cv2.waitKey(1) & 0xFF
        if k==27:
            break

        # Break if all windows closed
        vals = [cv2.getWindowProperty(win.name, cv2.WND_PROP_VISIBLE) for win in all_windows]
        if not any(vals):
            print("All windows closed, exiting")
            break

        # import pdb
        # pdb.set_trace()
        if not all_windows[0].dirty:
            print("All clean")
            continue
        for win, img in zip(all_windows, images):
            win.draw(img['img'])

    print("DESTROY")
    cv2.destroyAllWindows()
