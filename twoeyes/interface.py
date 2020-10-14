from .imports import *
from .stereo import Stereo
from ipywidgets import GridspecLayout, FileUpload, Output, Layout, VBox, HBox, Checkbox, Button
from IPython.display import clear_output, display, HTML

__all__ = ['MakeYourOwn']

class MakeYourOwn(Stereo):
    def __init__(self, prefix='stereograph', colab=False):
        '''
        Initialize an object to make a stereograph interactively
        from within a jupyter notebook (including one that might
        be hosted on colaboratory).
        '''

        # is this in colab?
        self.colab = colab

        # create a dictionary to store objects for the two eyes
        self.eyes = {'left':{}, 'right':{}}
        self.left, self.right = None, None
        #create the overall layout
        gs = GridspecLayout(2, 2, height='350px', width='620px')

        # loop over two eyes
        for i, k in enumerate(['left', 'right']):


            # create a widget to upload a file ...
            self.eyes[k]['upload'] = FileUpload(description=f"Upload {k} image.",
                                           accept='',
                                           multiple=False,
                                           layout=Layout( width='auto'),
                                           name=k)
            # ...and include it in the widget layout
            #gs[0, i] = self.eyes[k]['upload']

            # create a widget to display an image ...
            self.eyes[k]['image-output'] = Output(layout = {'border': '4px solid gray',
                                                            'height': 'auto',
                                                            'width' : '300px'})
            #... and include it in thte widget layout
            #gs[1, i] = self.eyes[k]['image-output']

            self.eyes[k]['text-output'] = Output(layout = {'width' : '300px'})

            self.eyes[k]['vbox'] = VBox([self.eyes[k]['upload'],
                                         self.eyes[k]['image-output'],
                                         self.eyes[k]['text-output']],
                                         layout=Layout(height='auto', align_items='center', padding='10px'))


            # do put a random image into
            with self.eyes[k]['image-output']:
                """
                img = np.random.normal(0, 1, (10,10))
                self.eyes[k]['figure'] = plt.figure(k, figsize=(2,2), dpi=100)
                '''fig.canvas.toolbar_visible = False
                fig.canvas.header_visible = False
                fig.canvas.footer_visible = False
                fig.canvas.resizable = False'''

                self.eyes[k]['ax'] =  self.eyes[k]['figure'].add_axes([0, 0, 1, 1])
                plt.sca(self.eyes[k]['ax'])
                self.eyes[k]['imshow'] = plt.imshow(img)
                plt.axis('off')
                plt.show(self.eyes[k]['figure'])
                """
        self.do = {}
        self.do['redcyan'] = Checkbox(value=True, description='red/cyan', layout=Layout(width='auto'))
        self.do['gif'] = Checkbox(value=True, description='animated', layout=Layout(width='auto'))
        #do_sidebyside = Checkbox(value=False, description='sidebyside', layout=Layout(width='auto'))
        options = VBox([self.do['redcyan'], self.do['gif']], layout=Layout(width='300px', align_items='flex-start', margin='0px 10px 0px 10px') )
        make = Button(description='Make stereograph(s)!',
                      tooltip='Make stereograph(s)!',
                      icon='check',
                      layout=Layout(width='300px', margin='0px 10px 0px 10px'))
        self.make_button = make

        actions_together = HBox([options, make])

        eyes_together = HBox([self.eyes['left']['vbox'],
                              self.eyes['right']['vbox']],
                              layout=Layout())

        self.messages = Output(layout=Layout(width='auto'))
        everything = VBox([eyes_together, actions_together, self.messages])

        Stereo.__init__(self, prefix=prefix)
        display(everything)

    def load(self, *args, **kwargs):
        # watch for the image uploads
        for eye in ['left', 'right']:
            self.eyes[eye]['upload'].observe(self.update_image,
                                             names='value')

        # watch the button click
        self.make_button.on_click(self.make_stereographs)

    def update_image(self, change):
        eye = change['owner'].description.split(' ')[1]
        uploaded = change['owner']
        filename = uploaded.metadata[0]['name']
        extension = filename.split('.')[-1]
        file = uploaded.value[filename]
        bytes = file['content']
        local_image_filename = f'{eye}.{extension}'
        with open(local_image_filename,'wb') as f:
            f.write(bytes)

        #print(f'wrote to {local_image_filename}')
        img = Image.open(local_image_filename)

        self.__dict__[eye] = img
        with self.eyes[eye]['image-output']:
            clear_output()
            display(img)

        with self.eyes[eye]['text-output']:
            clear_output()
            print(f'{filename} ({img.width}x{img.height} px)')

    def make_stereographs(self, change):

        with self.messages:
            clear_output()
            if self.left is None:
                print('Please upload a left image.')
                return
            if self.right is None:
                print('Please upload a right image.')
                return
            if (self.left.width != self.right.width) or (self.left.height != self.right.height):
                print('Please upload images that are the same size!')
                return


            if self.do['redcyan'].value:
                filename = self.to_anaglyph()
                self.display_stereograph(filename)
            if self.do['gif'].value:
                filename = self.to_gif()
                self.display_stereograph(filename)

    def display_stereograph(self, filename):
        if self.colab:
            #from google.colab import files
            #files.download(filename)
            print('''
            You're using google colaboratory.
            Please click the folder icon in the
            left menubar to access all images
            that you have created.
            ''')
        else:
            #with self.messages:
            html = HTML(f"<img src='{filename}' width=620px>")
            display(html)
