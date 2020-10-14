#!/usr/bin/env python
import optparse

#s = Stereo('couchtest/left.jpg','couchtest/right.jpg')
if __name__ == '__main__':

    print()

    # parse the input options
    parser = optparse.OptionParser(usage = """
    ./stereo.py [options] left_image right_image
Options:
    -a, --auto = skip the alignment step""")

    # figure out which options have been set, and the image filenames
    parser.add_option('-a', '--auto',
        action = 'store_const', const = True, dest = 'automatic', default=False,
        help = 'skip the adjustment step (this assumes your images are perfectly aligned)')
    options, args = parser.parse_args()

    # complain if the wrong number of filenames is included
    if len(args) != 2:
        parser.error("""Hmmm...there are {0} arguments to ./stereo.py.
                        Please run with two image filenames.
                        (e.g. "./stereo.py leftimage.jpg rightimage.jpg")
                        """.format(len(args)))

    # create the stereo image
    print("Creating a stereo image from your two input images!")
    s = Stereo(*args)


    # unless the "--auto" option is set,
    if options.automatic == False:
        s.adjust()

    # create a side-by-side image
    sbs = SideBySide(s)
    sbs.display()

    # create a blue-red image
    a = Anaglyph(s)
    a.display()
