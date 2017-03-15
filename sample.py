'''
The sample class for the imgprep script. One object of this class contains
three images of the sample. It also defines the methods used to process
the images.
'''

import skimage
import skimage.io


class Sample(object):

    def __init__(self, sample_name):
        '''
        Creates instances of the Sample class.
        '''

        self.name = sample_name

        self.image_paths = []
        self.images = []

    def load_images(self):
        '''
        Loads microscope images of the sample as numpy arrays and saves the
        image metadata. Make sure to have filenames and image_pathes set so
        load the images.
        '''
        self.image_count = len(self.image_paths)
        self.images = [None] * self.image_count

        if self.image_count > 1:
            self.images = skimage.io.imread_collection(self.image_paths)
        else:
            self.images = skimage.io.imread(str(self.image_paths))

        # TODO: Save metadata
        # TODO: Maybe rotate the second polarized image by -45°


    # TODO: Recognize the Magnification and calculate scale-bar dimensions
    # TODO: Crop the images and place them next to each other
    # TODO: Create three scale-bars and insert them into the images
