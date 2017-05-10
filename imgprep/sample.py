'''
The sample class for the imgprep script. One object of this class contains
three images of the sample. It also defines the methods used to process
the images.
'''
import os
import tempfile

import skimage.io as io
import skimage.measure as measure
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar


class Sample(object):
    '''
    Class for a sample. Including microscopy images and methods for editing.
    '''
    def __init__(self, sample_name):
        '''
        Creates instances of the Sample class and sets initial variables.
        '''
        self.sample_name = sample_name
        self.image_list = []
        self.image_count = 0

        self.cropped_image_list = []

    def load_images(self, filepaths):
        '''
        Loads a microscope images as numpy array and saves the image metadata.
        Make sure to have filenames and paths set so load the images.
        '''
        self.image_count = len(filepaths)

        for image in filepaths:
            self.image_list.append(Image(image))

        # TODO: Save metadata (magnification, scale, etc)
        # TODO: Maybe rotate the second polarized image by -45°

    def save_images(self):
        '''
        Method for saving the adjusted images.
        '''
        # Iterate over images
        for cropped in self.cropped_image_list:
            filepath = os.path.join(cropped.dir_name, cropped.filename)
            io.imsave(filepath, cropped.image)

    def add_scale(self, cropped=False):
        '''
        Adds a scale to the top-right of the cropped image.
        '''
        list_selector = {True: self.cropped_image_list,
                         False: self.image_list}

        for img in list_selector[cropped]:
            # TODO: Add method to image class for calculating px:µm ratio and
            #       adjust scalebar dynamically
            scalebar = ScaleBar(0.000002)  # 1 pixel = 0.2 meter

            # Prepare a figure without axes
            fig = plt.figure()
            ax = plt.add_subplot(1, 1, 1)
            plt.axis('off', frameon=None)

            # Add image and scale
            plt.imshow(img.image)
            plt.gca().add_artist(scalebar)

            # Save the figure without borders (to temporary file)
            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            tempfile = os.path.join(tempfile._get_default_tempdir, 'temp.png')
            plt.savefig(tempfile, bbox_inches=extent)

            # Reload the temporary file as image object and delete it
            img.image = io.imread(tempfile)
            os.remove(tempfile)

    def crop(self):
        '''
        Iterate over images, detect squares and crop
        '''
        for img in self.image_list:
            # New filename
            new_filename = '{}_cropped{}'.format(img.name, img.extension)
            self.new_filepath = os.path.join(img.dir_name, new_filename)
            self.cropped_image_list.append(Image(self.new_filepath, load=False))

        for img, cropped_img in zip(self.image_list, self.cropped_image_list):
            # Detecting the square (ROI)
            img.detect_roi()

            # Setting up coordinates
            left = img.roi_coords[0]
            right = left + img.roi_dim[0]
            top = img.roi_coords[1]
            bot = top + img.roi_dim[1]
            # Cropping
            cropped_img.image = img.image[left:right, top:bot, :]


class Image(object):
    '''
    Subclass of the sample class for images of each sample. It contains all in-
    formation concerning the images, as well as the image-files themselves.
    Methods performing on a single image are stored here.
    '''
    def __init__(self, filepath, load=True):
        '''
        Instantiates an image object, loads the image and sets up the variables
        '''
        # Filename, Path, Name, Extension
        self.dir_name = os.path.dirname(filepath)
        self.abs_path = os.path.abspath(filepath)
        self.filename = os.path.basename(self.abs_path)
        self.name, self.extension = os.path.splitext(self.filename)

        # Image object
        if load:
            self.image = io.imread(self.abs_path)

        # ROI parameters
        self.roi_dim = []
        self.roi_coords = []

    def align(self):
        '''
        Aligns images next to each other. If the y-axis isn't the same length,
        the remaining space should be filled with white or black space.
        '''
        # TODO
        pass

    def detect_roi(self, threshold=150):
        '''
        Detects the square in the sample image. Determines ROI dimensions and
        coordinates.
        '''
        # Find all pixels greater than threshold (arbitrary)
        img_red_thresh = self.image[:, :, 0] > threshold

        # Marching squares algorithm to find contours
        img_contours = measure.find_contours(img_red_thresh,
                                             0, fully_connected='high')

        # Find index of the biggest contour
        border = [len(x) for x in img_contours].index(max([len(x) for x in img_contours]))

        # Find the coordinates within the border
        x_points, y_points = zip(*img_contours[border])
        x_max = int(max(x_points)) - border
        y_max = int(max(y_points)) - border
        x_min = int(min(x_points)) + border
        y_min = int(min(y_points)) + border

        # The ROI dimensions
        self.roi_dim = [x_max - x_min, y_max - y_min]
        if self.roi_dim[0] == self.roi_dim[1]:
            self.is_square = True
        else:
            self.is_square = False

        # The ROI coordinates
        self.roi_coords = [x_min, y_min]
