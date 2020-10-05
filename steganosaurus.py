# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#
# Steganosaurus encodes a message into an image file.
#

import sys
import os
import argparse
from PIL import Image, UnidentifiedImageError
import numpy as np
import random
from bitstring import BitArray, BitStream

class SteganoImage:

    def __init__(self, fp: str):
        self.fp = fp
        self.pixelmap = np.array(Image.open(fp))

    def close_fp(self):
        Image.close(self.fp)

def encode_text(text_fp: str, img_fp: str, result_fp: str, key: str) -> str:
    """
    Main process for encoding text (UTF-8 encoded) from a file into
    an 8-bit, three-color image. Creates a SteganoImage() instance
    for managing the pixel data.

    Returns:
        A copy of the given image with the given message hidden
        within, at result_fp. If the text file is empty, returns
        the given image unaltered.
    """

    try:
        with Image.open(img_fp) as og_img:
            if og_img.size < (3, 3):
                print("Specified image is too small to be encoded onto.")
                return result_fp
    except (FileNotFoundError, UnidentifiedImageError):
        print("Specified image cannot be found or opened.")
    except Exception as e:
        print(e)

    if os.path.getsize(text_fp) == 0:
        # Create copy of image and let save at result_fp
        return result_fp

    img = SteganoImage(img_fp)

    img.close_fp()   # Important to clean up open files
    return result_fp

def main():
    """inputs = []
    parser = argparse.ArgumentParser(description='Encode/Decode text into/from an image, using a save key. ' +
    'The save key must be at least 5 characters long and can be made up of uppercase and lowercase letters, ' +
    'numbers, and special characters.')
    parser.add_argument('text input', metavar='text', type=str, nargs='+', help='Text to be encoded.')
    parser.add_argument('save key', metavar='key', type=open, help='Key to encrypt/decrypt message into image.')
    parser.add_argument('--encode', '-e', dest='', action='store', help='Encode the given text into an image.')
    parser.add_argument('--decode', '-d', dest='', action='store', help='Decode the text within in image.')
    args = parser.parse_args('test', inputs)"""
    try:
        action = sys.argv[1]
        userinputs = sys.argv[2:]
        assert action in ['--encode', '--decode'], \
            "Action is not --encode or --decode: " + action

        process(userinputs, action)
    except:
        raise IOError("Proper input format is --encode or --decode followed by a string and then a save key. "
            "The save key must be at least five characters long and can be made up of uppercase and lowercase "
                "letters, numbers, and special characters.")
    
def process(filename, action):

    if action == '--encode':
        return encode_text(" ".join(filename[0:-1]), filename[-1])
    elif action == '--decode':
        return decode_text(filename[0], filename[1])
