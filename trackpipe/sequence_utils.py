from . import pipeline


def _check_group(items):
    """Raise TypeError if object in group is not Transform"""
    for i in items:
        if not isinstance(i, pipeline.Transform):
            raise TypeError("Items must be Transforms or list of transforms")


def _create_initial_groups(transforms):
    """Return [groups] and [non_groups] of Transforms

    Args:
        transforms ([Transform/Window]): transforms or windows. Cannot be a
            mixture of both!

    Returns:
        [Window], [Transforms]: list of supplied windows, list of transforms
            not in windows.
    """
    groups = []
    non_groups = []
    for idx, t in enumerate(transforms):
        if isinstance(t, (pipeline.Window)):
            _check_group(t.transforms)
            groups.append(t)
        elif not isinstance(t, pipeline.Transform):
            raise ValueError("Items must be Transforms or list of transforms")
        else:
            non_groups.append(t)
    return groups, non_groups


def collect_windows(transforms):
    """Returns list of Windows"""
    grouped, ungrouped = _create_initial_groups(transforms)
    if len(ungrouped) == len(transforms):
        return [pipeline.Window(ungrouped)]
    if grouped and ungrouped:
        raise ValueError("Cannot have both groups and non-groups together.")
    return grouped


def check_dup_win_labels(windows):
    """Raise ValueError if duplicate trackbar labels exist in same window

    Args:
        windows ([Window]): List of windows with their transforms
    """
    for win in windows:
        params = {}
        for t in win.transforms:
            for label, p in t.params.items():
                if label in params:
                    raise ValueError(
                        f"Param: `{label}` is defined twice in window `{win.name}` "
                        f"in transforms `{t.__class__.__name__}` and "
                        f"`{params[label]}`. Rename one by changing the attribute "
                        "name or using the Param `label` kwarg."
                    )
                else:
                    params[label] = t.__class__.__name__
