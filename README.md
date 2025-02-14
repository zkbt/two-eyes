# two-eyes
Simple tools for making stereographic images in Python.

## Documentation
This code currently very poorly documented. However, a browser-based interactive user interface for it is available [here](https://colab.research.google.com/github/zkbt/two-eyes/blob/main/notebooks/make_your_own_stereographs.ipynb). Try it out!

## Example Usage
To create stereographs within a script:
```python
from twoeyes import Stereo

s = Stereo(left='some-image.jpg', right='another-image.jpg')
s.to_anaglyph()
s.to_gif()
s.to_sidebyside()
```

To spin up an interactive interface in a jupyter notebook:
```python
from twoeyes import MakeYourOwn

s = MakeYourOwn()
```

## Installation
You should be able to install this by running
```
pip install two-eyes
```
from a UNIX prompt.

## Acknowledgements
These tools were originally developed by Zach Berta-Thompson for the Fall 2020 (pandemic) semester of ASTR1030 at the University of Colorado Boulder. The lab instructional team and students for that course provided valuable feedback and suggestions on its usage.

## Contributors
This package was written by [Zach Berta-Thompson](https://github.com/zkbt).
