#!/usr/bin/env python

# ###############################
# @author Petar Vorotnikov
# @description Sobel operations
# ###############################

import base64
import cStringIO

import argparse, logging, sys, os
from PIL import Image, ImageFilter, ImageChops


def apply_edge_detector(input_image):

    # Apply median filter
    median_image = input_image.filter(ImageFilter.MedianFilter(3))

    # Create Sobel Matrix for X
    sobel_x = (-1, 0, 1,
                -2, 0, 2,
                -1, 0, 1)
    kernelx_image = median_image.filter(ImageFilter.Kernel((3, 3), sobel_x, scale=1))

    # Create Sobel Matrix for Y
    sobel_y = (1,  2,  1,
               0,  0,  0,
              -1, -2, -1)
    kernely_image = median_image.filter(ImageFilter.Kernel((3, 3), sobel_y, scale=1))

    # Sum the pixels of the X and Y sobel images
    merged = ImageChops.add(kernelx_image, kernely_image)

    # Thresholding
    merged = merged.point(lambda x: 0 if x < 60 else 255)

    return merged


def main():

    # Get arguments
    parser = argparse.ArgumentParser(prog='kNN-classification', description=__doc__)
    parser.add_argument('input', metavar='INPUT FILE', help="Input file")
    args = parser.parse_args()

    # Configure logger
    logging.basicConfig(stream=sys.stdout, format="%(message)s", level=logging.INFO)

    # Apply sobel detection
    input_image = Image.open(args.input)
    input_image = input_image.convert('L')
    output_image = apply_edge_detector(input_image)

    buffer = cStringIO.StringIO()
    output_image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue())

    print img_str;

if __name__ == '__main__':
    main()
