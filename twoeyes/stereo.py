from .iplot import *

__all__ = ['Stereo']
def add_number_to_filename(filename, i):
    components = filename.split('.')
    components[-2] += f'-{i:03.0f}'
    return '.'.join(components)

def create_safe_filename(filename):
    i = 0
    safe_filename = add_number_to_filename(filename, i)
    while os.path.exists(safe_filename):
        i += 1
        safe_filename = add_number_to_filename(filename, i)
    return safe_filename



class Stereo:
    '''
    A generic stereographic image.
    '''
    def __init__(self, left=None, right=None, prefix='stereograph'):
        '''
        Initialize a new stereograph.

        Parameters
        ----------
        left : str
            Filename of the left image.
        right : str
            Filename of the right image.
        '''

        # load the images from their files
        self.load(left, right)

        # store a prefix for saving a filename
        self.prefix = prefix

    def load(self, left_filename, right_filename):
        '''
        Load and store images for the left and right eyes.
        '''

        print('Reading input images.')
        self.filenames = dict(left=left_filename, right=right_filename)
        print(self.filenames)

        # loop over the eyes, loading the image for each
        for eye in ['left', 'right']:
            print(f"  loading {eye} eye's image from {self.filenames[eye]}")
            # store images in self.left and self.right
            self.__dict__[eye] = Image.open(self.filenames[eye])
            print("   success!")

    def adjust(self):
        '''
        Let user click to identify a feature to line up in both images.
        '''

        raise NotImplementedError('Still buggy!')

        self.iplot = iplot(1,2,verbose=False,hspace=0,wspace=0)
        self.iplot.subplot(0,0,name='left')
        self.iplot.subplot(0,1,name='right')
        for k in ['left', 'right']:
            ax = self.iplot.axes[k]
            ax.imshow(self.__dict__[k], interpolation='nearest')
            ylim = ax.get_ylim()
            ax.set_ylim(max(ylim), min(ylim))
            ax.set_title(k.capitalize())
            plt.setp(ax.get_yticklabels(), visible=False)
            plt.setp(ax.get_xticklabels(), visible=False)
        print(" Please click the same feature in boths images.")
        print("  (the images will be aligned to match up on this feature, to draw the viewer's focus)")
        self.referencepoints = {}
        while(len(self.referencepoints.keys())<2):
            click = self.iplot.getMouseClicks(1)[0]
            for k in self.iplot.axes.keys():
                if self.iplot.axes[k] == click.inaxes:
                    whicheye = k
                    self.referencepoints[k] = np.round(np.array([click.xdata, click.ydata])).astype(np.int)
            print("  You clicked the {0} image at {1}".format(whicheye, self.referencepoints[whicheye]))
            #self.iplot.axes[whicheye].scatter(*self.referencepoints[whicheye], s=50)
        nudgex, nudgey = self.referencepoints['right']-self.referencepoints['left']

        print(" Applying a nudge of {0} pixels between the two images.".format((nudgex,nudgey)))
        left, right = np.array(self.left), np.array(self.right)
        if nudgex > 0:
            left = left[:,:-nudgex]
            right = right[:,nudgex:]
        else:
            left = left[:,-nudgex:]
            right = right[:,:nudgex]
        if nudgey > 0:
            left = left[:-nudgey, :]
            right = right[nudgey:, :]
        else:
            left = left[-nudgey:, :]
            right = right[:nudgey, :]
        self.left, self.right = Image.fromarray(left), Image.fromarray(right)

    def to_sidebyside(self, directory=''):
        '''
        Output stereograph as a side-by-side image pair.
        '''

        label = 'side-by-side'

        # convert images to arrays, but keep them as colors (width x height x 3)
        left = np.array(self.left)
        right = np.array(self.right)

        # construct a comined image by stacking the images side by side
        combined = Image.fromarray(np.hstack([left,right]))

        # save to an image file
        base_filename = os.path.join(directory, f'{self.prefix}-{label}.jpg')
        filename = create_safe_filename(base_filename)
        combined.save(filename)
        print(f'Saved {label} stereograph to {filename}')
        return filename

    def to_anaglyph(self, directory=''):
        '''
        Output stereograph as a red-cyan image pair.
        '''

        # set the label
        label = 'red-cyan'

        # first convert images to black and white (width x height)
        left = np.array(self.left.convert('L'))
        right = np.array(self.right.convert('L'))

        # construct a combined image by populating the RGB channels
        merged = np.zeros_like(np.array(self.left))
        merged[:,:,0] += left
        merged[:,:,1] += right
        merged[:,:,2] += right
        combined = Image.fromarray(merged)

        # save to an image file
        base_filename = os.path.join(directory, f'{self.prefix}-{label}.jpg')
        filename = create_safe_filename(base_filename)
        combined.save(filename)
        print(f'Saved {label} stereograph to {filename}')
        return filename

    def to_gif(self, directory=''):
        '''
        Output stereograph as an animated gif.
        '''
        # set the label
        label = 'animated'

        # convert images to arrays, but keep them as colors (width x height x 3)
        left = self.left
        right = self.right

        # save to an image file
        base_filename = os.path.join(directory, f'{self.prefix}-{label}.gif')
        filename = create_safe_filename(base_filename)
        left.save(filename, save_all=True, append_images=[right], optimize=True, duration=500, loop=0)
        print(f'Saved {label} stereograph to {filename}')
        return filename
