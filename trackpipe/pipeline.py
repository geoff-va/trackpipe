"""Implements a pipeline of Transformations

- Windows contain Tranformations
- Transformations have Params

This has become a re-implementation of the work done by Bob Kerner here:
- https://github.gatech.edu/bkerner3/trackbar

So kudos to him for the original work and inspiration!
"""
import logging

from . import (
    sequence_utils,
    parallel_utils
)

import numpy as np
import cv2

log = logging.getLogger(__name__)


def nothing(*a,**k):
    pass


class Window(object):
    counter = 1

    def __init__(self, transforms, name='', track_src=''):
        """A Window that transforms will be applied in named `name`

        Args:
            transforms ([Transform]): list of transforms in execution order
            name (str): default 'Step N' if not supplied
        """
        self.last_output = None
        self.transforms = transforms
        if not name:
            self.name = f'Step {self.counter}'
            Window.counter += 1
        else:
            self.name = name
        self.track_src = self.name if not track_src else track_src

    @property
    def dirty(self):
        """Returns index of first tranform that's dirty or -1 if None dirty"""
        for i, transform in enumerate(self.transforms):
            transform.update_params(self.track_src)
            if transform.dirty:
                return i
        return -1

    def draw(self, img):
        """Call _draw on each child transform in sequence and show it in window"""
        result = img
        for transform in self.transforms:
            result = transform._draw(result)
        self.last_output = result
        cv2.imshow(self.name, result.astype(np.uint8))
        return result


class Transform(object):
    def __init__(self):
        """A transformation that will be applied to an image"""
        self.last_output = None
        self.params = self._get_params()

    @property
    def dirty(self):
        """Returns True if any child parameter has been modified"""
        for p in self.params.values():
            if p.dirty:
                return True
        return False

    def _get_params(self):
        """Return dict of Param objects defined in order on class"""
        params = {}
        for attr in self.__class__.__dict__.keys():
            # TODO: Think there's a better Meta programming way to convert
            # class var's into instance vars (think django Fields)
            if isinstance(getattr(self, attr), Param):
                inst = getattr(self, attr)
                # Create instance var from class var so we don't ref class var
                new_inst = Param(
                    label=inst.label,
                    _max=inst.max,
                    _min=inst.min,
                    default=inst.default,
                    adjust=inst.adjust
                )
                setattr(self, attr, new_inst)
                label = new_inst.label if new_inst.label else attr
                new_inst.label = label
                params[label] = new_inst
        return params

    def update_params(self, win_name):
        """Updates the value from trackbar for each child parameter

        Args:
            win_name (str): Name of the window to get param from
        """
        if not self.params:
            return False
        for p in self.params.values():
            p.update_value(win_name)

    def compute_values(self):
        """Can modify self.your_param.value being passed to draw function"""
        pass

    def _draw(self, img):
        """Perform the transform and save the output

        Args:
            img (np.array): Image to operate on

        Returns:
            img (np.array): Output image
        """
        self.compute_values()
        result = img
        try:
            result = self.draw(img)
        except Exception as e:
            print(e)
        self.last_output = result

        # Nothing is dirty since we've just drawn image
        for p in self.params.values():
            p.dirty = False
        return result

    def draw(self, img):
        """Perform your transformation

        Args:
            img (np.array): Image to operate on

        Returns:
            img (np.array): Output image
        """
        raise NotImplementedError


class Param(object):
    def __init__(self, label='', _max=100, _min=0, default=1, adjust=None):
        """Represents a parameter to be used in your Transform.draw method

        Args:
            label (str): Name of param as shown in trackbard window. If not
                supplied, attribute name is used
            _max (int): max position of trackbar
            default (int): starting value of trackbar
            adjust (callable): adjustment that can be made to your value.
                ex: lambda x: x if x % 2 == 0 else x + 1
        """
        self.label = label
        self.max = _max
        self.min = _min
        self.adjust = adjust
        self.default = default
        self.value = max(_min, default)
        self.dirty = True
        self._pos = self.value
        if adjust:
            self.value = adjust(self.value)

    def update_value(self, win_name):
        """Fetches parm position from trackbar and sets dirty

        Args:
            win_name (str): Name of window to fetch param from
        """
        pos = cv2.getTrackbarPos(self.label, win_name)
        self.dirty = False if self._pos == pos else True
        self._pos = pos
        if callable(self.adjust):
            pos = self.adjust(pos)
        self.value = max(pos, self.min)


def run_pipe(transforms, img=None):
    """Run the pipeline

    Args:
        transforms ([Transform/Group]): list of all transforms or windows of
            transforms
        img (np.array): Input image to first transform. Can leave as None and
            allow your first Transform to perform any image loading (for things
            like videos, etc). Default: None
        verbose (bool): If True, sets logging.LogLevel(logging.DEBUG) (Default: False)
    """
    windows = sequence_utils.collect_windows(transforms)
    sequence_utils.check_dup_win_labels(windows)

    # Build the windows and trackbars
    for window in windows:
        cv2.namedWindow(
            window.name, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO|cv2.WINDOW_GUI_EXPANDED)
        for t in window.transforms:
            for k, v in t.params.items():
                cv2.createTrackbar(k, window.name, v._pos, v.max, nothing)

    # Draw an intitial image
    orig = None if img is None else np.copy(img)
    for window in windows:
        orig = window.draw(orig)

    # Loop performing transforms in each window
    while True:
        result = np.copy(img)
        # Break on escape key
        k = cv2.waitKey(1) & 0xFF
        if k==27:
            break

        # Break if all windows closed
        vals = [cv2.getWindowProperty(win.name, cv2.WND_PROP_VISIBLE) for win in windows]
        if not any(vals):
            break

        # Only update starting at first dirty window
        dirty = np.array([win.dirty for win in windows])
        clean = dirty == -1
        if all(clean):
            continue
        offset = np.argmax(dirty >= 0)
        result = result if offset == 0 else windows[offset - 1].last_output
        for window in windows[offset:]:
            result = window.draw(result)

    cv2.destroyAllWindows()


def run_parallel_pipe(transforms, img_paths):
    """Run a single list of transforms on multiple images

    Args:
        transforms [Transform]: list of transforms in order of execution
        img_paths ([str]): List of paths to images. First image is master
    """

    # Can only have a single window
    windows = sequence_utils.collect_windows(transforms)
    if len(windows) > 1:
        raise ValueError('Must only be a single window for parallel processing')
    sequence_utils.check_dup_win_labels(windows)

    # Get all images with their loaded img content
    images = parallel_utils.load_images(img_paths)

    # Setup the master window with the trackbars
    master_win = windows[0]
    master_win.name = images[0]['path']
    master_win.track_src = images[0]['path']
    parallel_utils.create_master_trackbars(master_win)

    # Create windows that won't have trackbars
    slave_wins = parallel_utils.create_slave_windows(transforms, master_win.name, images[1:])
    all_windows = [master_win] + slave_wins

    # Update once so we have an image in each window
    for img in images:
        img['img'] = np.copy(img['img'])
    for win, img in zip(all_windows, images):
        win.draw(img['img'])

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
            break

        if all_windows[0].dirty == -1:
            continue
        for win, img in zip(all_windows, images):
            win.draw(img['img'])

    cv2.destroyAllWindows()