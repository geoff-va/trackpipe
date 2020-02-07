# trackpipe
This project is an image processing pipeline that allows you to create reusable transformations and compose them into individual windows to see intermediate output. You can also run a single set of transforms on multiple images simultaneously.

This project is based on the work done by Bob Kerner, [here](https://github.gatech.edu/bkerner3/trackbar), so kudos to Bob!

[Demo](https://drive.google.com/open?id=1GUpTdmhZYhUZ3D7-PlTz90leqJ9auMqQ)

**Note**: This code has not been tested against python 2.7

## Installation
`pip install git+https://github.com/geoff-va/trackpipe.git`

or if you've cloned the repo:
`pip install -e trackpipe/`


## Usage
### Sequenced Pipeline
Create individual `Transform`s once, add them into `Window`s and reuse/reorder them throughout your pipeline.

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
w1 = Window([LoadImage('your_file.png'), Transform1(), ...])
w2 = Window([Transform2(), Transform3(), ...])

pipeline.run_pipe([w1, w2])  # no img param; can use a transform to load and return your image
```

**Single Window**
```python
img = cv2.imread('your_file.png')
transforms = [Transform1(), Transform2(), ...]
pipeline.run_pipe(transforms, img)  # Can also pass a loaded image to `run_pipe`
```

If no `name` parameter is passed to the `Window` constructor, it defaults to `Step N`. Otherwise, you can name the windows if you'd like.

A few simple transforms are included.

If you override the `__init__` method, you _must_ call `super().__init__()` first.

### Parallel Pipeline
You can apply a single sequence of transforms to multiple images simultaneously with `run_parallel_pipe`.

You supply the list of transforms and list of images. The first image will be the master window with trackbar controls, and those trackbars will control the master and all the slaves at the same time.

```python
from pipeline import run_parallel_pipe

images = [
    'path1.jpg',
    'path2.jpg',
]

transforms = [
    YourTransform1(),
    YourTransform2(),
    YourTransform3()
]

run_parallel_pipe(transforms, images)
```

## Examples
If you clone the repo, there are two examples in `example.py`. To run:
- `python example.py --example 1`
- `python example.py --example 2`

Example 1 is a reproduciton of Bob's trackbar example
Example 2 is a file load, color convert and two gaussian blurs in successive windows to demonstrate the pipeline



