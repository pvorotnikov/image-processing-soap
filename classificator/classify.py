#!/usr/bin/env python

# ###############################
# @author Petar Vorotnikov
# @description kNN classifier
# ###############################

import os, sys, math, logging, collections, argparse, json
from json import encoder as json_encoder
import numpy as np
import matplotlib.pylab as plt
import cv2
from PIL import Image


'''
Configuration and globals
'''
ReferenceImage = collections.namedtuple('ReferenceImage', 'path, image, image_histogram')
CLASSIFICATOR_ROOT = os.path.dirname(os.path.realpath(__file__))
DIR_BEACH = os.path.join(CLASSIFICATOR_ROOT, 'beach')
DIR_CITY = os.path.join(CLASSIFICATOR_ROOT, 'city')
DIR_MOUNTAIN = os.path.join(CLASSIFICATOR_ROOT, 'mountain')
RESIZE_DIMENSIONS = (256, 256)
LABEL_BEACH = 0
LABEL_MOUNTAIN = 1
LABEL_CITY = 2


'''
Retreive human-readable label
'''
def get_label(raw_label):
    if raw_label == LABEL_BEACH:
        return 'beach'
    elif raw_label == LABEL_MOUNTAIN:
        return 'mountain'
    elif raw_label == LABEL_CITY:
        return 'city'
    else:
        return 'unknown'

'''
Normalizes a given histogram making it with vector distance 1
'''
def normalize_histogram(histogram):
    np_histogram = np.array(histogram)
    normalized_histogram = np_histogram / np.linalg.norm(np_histogram)

    return normalized_histogram.tolist()

'''
Get the histogram and normalize it
so that the histogram vector length is 1
'''
def get_image_histogram(image):
    histogram = normalize_histogram(image.histogram())

    return histogram

'''
Load a single image, convert it to RGB and
resize it top proper dimensions
'''
def load_image(file):

    try:
        image = Image.open(file) # load the image
        image = image.convert('RGB') # convert the image to RGB
        image = image.resize(RESIZE_DIMENSIONS) # resize the image
        image_histogram = get_image_histogram(image) # get the histogram
        image_histogram = np.array(image_histogram).astype(np.float32) # convert it to numpy array
        image = np.array(image) # convert also the image to numpy array

        return ReferenceImage(
            path = file,
            image = image,
            image_histogram = image_histogram
        )

    except IOError:
        return None


'''
Load all images in a given path
@param {String} path
@return {Map} images
'''
def load_images(path):

    logging.debug('Loading reference images in {0}...'.format(path))

    # Get all image filenames in the images directory
    filenames = os.listdir(path)

    images = []
    for filename in filenames:
        image = load_image(os.path.join(path, filename))
        if image != None:
            images.append(image)

    return images


''' Prepare the training and testing data for an image set '''
def prepare_data(images, label):
    data = np.zeros((len(images), 768)).astype(np.float32)
    for idx in range(len(images)):
        data[idx] = images[idx].image_histogram

    labels = np.empty(len(images)).astype(np.float32)
    labels.fill(label)

    return data, labels

'''
Main routine
'''
def main():

    # Get arguments
    parser = argparse.ArgumentParser(prog='kNN-classification', description=__doc__)
    parser.add_argument('input', metavar='INPUT FILE', help="Input file")
    args = parser.parse_args()

    # Configure logger
    logging.basicConfig(stream=sys.stdout, format="%(message)s", level=logging.INFO)

    # Load the query image and fetch its data
    query_image = load_image(args.input);
    query_image_data, l = prepare_data([query_image], None)

    # Load training images
    beaches = load_images(DIR_BEACH)
    mountains = load_images(DIR_MOUNTAIN)
    cities = load_images(DIR_CITY)

    # Prepare training data
    training_beaches, labels_beaches = prepare_data(beaches, LABEL_BEACH);
    training_mountains, labels_mountains = prepare_data(mountains, LABEL_MOUNTAIN);
    training_cities, labels_cities = prepare_data(cities, LABEL_CITY);

    # Consolidate training data
    training_data = np.concatenate((training_beaches, training_mountains, training_cities), axis=0)
    labels = np.concatenate((labels_beaches, labels_mountains, labels_cities), axis=0)

    # Train the kNN
    knn = cv2.KNearest()
    knn.train(training_data, labels)

    # Fetch result
    ret, results, neighbours, dist = knn.find_nearest(query_image_data, 3)

    # Print output
    classified_label = get_label(results[0][0])
    logging.debug('============================')
    logging.debug('Image classified as {0}'.format(classified_label))
    logging.debug('Nearest neighbor at {0}'.format(dist[0][0]))

    # Return the result
    json_data = {'classification': classified_label}
    json_str = json.dumps(json_data)
    print json_str


if __name__ == '__main__':
    main()
