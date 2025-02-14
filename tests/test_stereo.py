from twoeyes import Stereo
from twoeyes.imports import data_directory, os

example_directory = 'two-eyes-examples'
try:
    os.mkdir(example_directory)
except:
    pass

def test_stereo():
    s = Stereo(os.path.join(data_directory, 'left.jpg'),
               os.path.join(data_directory, 'right.jpg'))
    s.to_sidebyside(directory=example_directory)
    s.to_anaglyph(directory=example_directory)
    s.to_gif(directory=example_directory)
