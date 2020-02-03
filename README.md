# trackpipe
This project is an image processing pipeline that allows you to create reusable transformations and compose them into individual windows to see intermediate output.

This project is based on the work done by Bob Kerner, [here](https://github.gatech.edu/bkerner3/trackbar), so kudos to Bob!

**Note**: This code has not been tested against python 2.7

## Installation
`pip install git+https://github.com/geoff-va/trackpipe.git`

or if you've cloned the repo:
`pip install -e trackpipe/`


## Usage
Create individual `Transform`s once, and then compose them into `Window`s and reuse them throughout your pipeline.

- Subclass `pipeline.Transform`
- Add `Param` class attributes for each trackbar param you'd like
- Add a `draw(self, img)` method that performs the transform, accessing your params as `self.your_param.value`
- Optionally add a `compute_values(self)` function that further modifies either your `self.your_param.value` or other instance attributes you've created

```python
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
```

Create one of these for each operation you'd like to perform (Convert Color, inRange filter, MedianBlur, HoughLines, Load Video Frame, etc), then compose them into windows (or just a single list):

**Multiple Windows**
```python
w1 = Window([Transform1(), Transform2(), ...])
w1 = Window([Transform3(), Transform4(), ...])

pipeline.run_pipe([w1, w2])
```

**Single Window**
```python
transforms = [Transform1(), Transform2(), ...]
pipeline.run_pipe(transforms)
```

If no `name` parameter is passed to the `Window` constructor, it defaults to `Step N`. Otherwise, you can name the windows if you'd like.

A few simple transforms are included.

## Examples
If you clone the repo, there are two examples in `example.py`. To run:
- `python example.py --example 1`
- `python examlpe.py --example 2`

Example 1 is a reproduciton of Bob's trackbar example
Example 2 is a file load, color convert and two gaussian blurs in successive windows to demonstrate the pipeline

