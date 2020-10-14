from twoeyes import Stereo

def test_stereo():
    s = Stereo('left.jpg', 'right.jpg')
    s.to_sidebyside()
    s.to_anaglyph()
    s.to_gif()
