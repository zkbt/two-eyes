from .imports import *
from ipywidgets import GridspecLayout, FileUpload, Output, Layout
from IPython.display import clear_output
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()


class MakeStereo:
    def __init__(self):
        '''
        Initialize an object to make a stereograph interactively
        from within a jupyter notebook (including one that might
        be hosted on colaboratory).
        '''

        # create a dictionary to store objects for the two eyes
        self.eyes = {'left':{}, 'right':{}}


        #create the overall layout
        gs = GridspecLayout(2, 2, height='350px', width='620px')

        # loop over two eyes
        for i, k in enumerate(['left', 'right']):

            # create a widget to upload a file ...
            self.eyes[k]['upload'] = FileUpload(description=k,
                                           accept='',
                                           multiple=False,
                                           layout=Layout(height='auto', align='center'),
                                           name=k)
            # ...and include it in the widget layout
            gs[0, i] = self.eyes[k]['upload']

            # create a widget to display an image ...
            self.eyes[k]['image-output'] = Output(layout = {'border': '3px solid black',
                                                           'height': '300px',
                                                           'width' : '300px'})
            #... and include it in thte widget layout
            gs[1, i] = self.eyes[k]['image-output']


            # do put a random image into
            with self.eyes[k]['image-output']:
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

            # have the uploaders observe for changes
            self.eyes[k]['upload'].observe(self.update_image,
                                           names='value')

        display(gs)

    def update_image(self, change):
        print(change.keys())
        print()
        k = change['owner'].description
        print(k)
        uploaded = change['owner']
        filename = uploaded.metadata[0]['name']
        print(filename)
        extension = filename.split('.')[-1]
        file = uploaded.value[filename]
        bytes = file['content']
        local_image_filename = f'{k}.{extension}'
        with open(local_image_filename,'wb') as f:
            f.write(bytes)
        print(f'wrote to {local_image_filename}')


        img = np.array(Image.open(local_image_filename).convert('L'))

        print(f'updating plot for {k}')
        print(self.eyes[k]['ax'])
        print(k)

        with self.eyes[k]['image-output']:
            clear_output()
            self.eyes[k]['ax'].imshow(img)
            display(self.eyes[k]['figure'])
