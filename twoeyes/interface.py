from .imports import *
from .stereo import Stereo
from ipywidgets import GridspecLayout, FileUpload, Output, Layout, VBox, HBox, Checkbox, Button, RadioButtons
from IPython.display import clear_output, display, HTML

__all__ = ['MakeYourOwn']

class MakeYourOwn(Stereo):
    def __init__(self, prefix='stereograph',
                       width=300,
                       padding=10,
                       colab=False):
        '''
        Initialize an object to make a stereograph interactively
        from within a jupyter notebook (including one that might
        be hosted on colaboratory).

        Parameters
        ----------
        prefix : str
            How should we start the filenames?
        width : int
            How wide is one eye in the UI, in pixels?
        padding : int
            What's the padding between eyes, in pixels?
        colab : bool
            Is this being run inside of colaboratory?
        '''

        # is this in colab?
        self.colab = colab


        # create a dictionary to hold all the widgets
        self.widgets = {}

        # create a widget to display some instructions
        self.widgets['instructions'] = Output(layout=Layout(width=f'{(width+padding)*2}px'))

        # loop over two eyes
        for i, k in enumerate(['left', 'right']):

            # create a widget to upload a file for each eye
            self.widgets[f'{k}-upload'] = FileUpload(
                                           description=f"Upload {k} image.",
                                           accept='',
                                           multiple=False,
                                           layout=Layout(width='auto'),
                                           name=k)

            # create a widget to display an image
            self.widgets[f'{k}-image-output'] = Output(layout=Layout(border='4px solid gray',
                                                                     height='auto',
                                                                     width=f'{width}px'))

            # create a widget to store image information
            self.widgets[f'{k}-text-output'] = Output(layout=Layout(width=f'{width}px'))

            # create a widget to connect everything for each eye
            self.widgets[f'{k}-vbox'] = VBox([self.widgets[f'{k}-upload'],
                                              self.widgets[f'{k}-image-output'],
                                              self.widgets[f'{k}-text-output']],
                                         layout=Layout(height='auto', align_items='center', padding=f'{padding}px'))



        # create rotation widgets
        self.widgets['rotation'] = RadioButtons(
                        options=['0˚', '90˚', '180˚', '270˚'],
                        value='0˚',
                        description='',
                        layout=Layout(width=f'{width/4:.0f}px'))

        # create widgets for what kinds of stereographs to make
        self.widgets['do-redcyan'] = Checkbox(value=True, description='red/cyan', layout=Layout(width='auto'))
        self.widgets['do-gif'] = Checkbox(value=False, description='animated', layout=Layout(width='auto'))
        #self.widgets['do-sidebyside'] = Checkbox(value=False, description='sidebyside', layout=Layout(width='auto'))

        todo = VBox([self.widgets['do-redcyan'], self.widgets['do-gif']], layout=Layout(width=f'{3*width/4:.0f}px', align_items='flex-start'))
        options = HBox([self.widgets['rotation'], todo], layout=Layout(width=f'{width}px', margin=f'0px {padding}px 0px {padding}px'))

        # create widget for making the stereographs
        make = Button(description='Make stereograph(s)!',
                      tooltip='Make stereograph(s)!',
                      icon='check',
                      layout=Layout(width=f'{width}px', margin=f'0px {padding}px 0px {padding}px'))
        self.widgets['make-button'] = make


        # create widget for outputs
        self.widgets['outputs'] = Output(layout=Layout(width=f'{(width + padding)*2}px'))

        # group the widgets into layouts
        actions_together = HBox([options, make])
        eyes_together = HBox([self.widgets['left-vbox'],
                              self.widgets['right-vbox']],
                              layout=Layout())
        everything = VBox([self.widgets['instructions'],
                           eyes_together,
                           actions_together,
                           self.widgets['outputs']])

        # initialize the stereo viewer overall
        Stereo.__init__(self, prefix=prefix)
        self.thumbnails = dict(left=None, right=None)
        self.width = width
        # set initial instructions
        self.reset_instructions('Hi! Please upload two images to make a 3D image.')
        display(everything)

    def load(self, *args, **kwargs):
        '''
        Start the interactions running.
        (This is called by Stereo.__init__)
        '''

        # watch for new image uploads
        for eye in ['left', 'right']:
            self.widgets[f'{eye}-upload'].observe(self.update_image, names='value')

        # watch the rotation updates
        self.widgets['rotation'].observe(self.update_rotation, names='value')

        # watch the button click
        self.widgets['make-button'].on_click(self.make_stereographs)


    def reset_instructions(self, message=''):
        '''
        Clear the instructions and add new text.
        '''
        with self.widgets['instructions']:
            clear_output()
            print(message)

    def rotate_image(self, image):
        try:
            rotation = float(self.widgets['rotation'].value[:-1])
            return image.rotate(rotation, expand=True)
        except AttributeError:
            return image


    def display_image(self, eye):
        with self.widgets[f'{eye}-image-output']:
            clear_output()
            rotated = self.rotate_image(self.thumbnails[eye])
            if rotated is not None:
                display(rotated)

    def update_rotation(self, change):
        for eye in ['left', 'right']:
            self.display_image(eye)

    def update_image(self, change):
        '''
        Update an image by saving it,
        loading it, and displaying it.

        (Could probably be faster
        with directly reading the
        image from bytestream in
        the uploaded file...)
        '''

        # figure out the filename
        eye = change['owner'].description.split(' ')[1]
        uploaded = change['owner']
        filename = uploaded.metadata[0]['name']

        # provide an update that this will take a while
        with self.widgets['instructions']:
            clear_output()
            print(f'File {filename} is loading.\nPlease have patience (or upload a smaller image).')

        # save the file, with its original extension
        extension = filename.split('.')[-1]
        file = uploaded.value[filename]
        bytes = file['content']
        local_image_filename = f'{eye}.{extension}'
        with open(local_image_filename,'wb') as f:
            f.write(bytes)

        # load that file as a PIL image
        self.images[eye] = Image.open(local_image_filename)
        aspect = self.images[eye].width/self.images[eye].height
        if aspect > 1:
            thumb_size = round(self.width*aspect), self.width
        else:
            thumb_size = self.width, round(self.width/aspect)
        self.thumbnails[eye] = self.images[eye].copy()
        self.thumbnails[eye].thumbnail(thumb_size)
        self.display_image(eye)

        # print a summary of the image as text
        with self.widgets[f'{eye}-text-output']:
            clear_output()
            print(f'{filename}\n ({self.images[eye].width}x{self.images[eye].height} pixels)')

        # update instructions
        if (self.images['left'] is not None) and (self.images['right'] is not None):
            self.reset_instructions("Two images have been uploaded. You're ready to make a stereograph!")
        elif (self.images['left'] is None) or (self.images['right'] is None):
            self.reset_instructions('Please upload a second image to make a 3D image.')
        else:
            self.reset_instructions('')

    def make_stereographs(self, change):
        '''
        Produce stereographs when the button is pressed.
        '''
        with self.widgets['outputs']:
            clear_output()
            if self.images['left'] is None:
                print('Please upload a left image.')
                return
            if self.images['right'] is None:
                print('Please upload a right image.')
                return
            if (self.images['left'].width != self.images['right'].width) or (self.images['left'].height != self.images['right'].height):
                print('Please upload images that are the same size!')
                return

        if self.widgets['do-redcyan'].value:
            with self.widgets['outputs']:
                filename = self.to_anaglyph()
            self.display_stereograph(filename)
        if self.widgets['do-gif'].value:
            with self.widgets['outputs']:
                filename = self.to_gif()
            #self.display_stereograph(filename)

    def display_stereograph(self, filename):
        '''
        Display a stereograph from a file.
        '''

        with self.widgets['outputs']:
            print(f'Displaying stereograph (may take a moment).')
            if self.colab:
                print('''
        | In colaboratory, you can use the File Browser   |
        | (folder icon) to directly access all newly      |
        | created stereographic image files for download. |
                ''')
            i = Image.open(filename)
            display(i)
