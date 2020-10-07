# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#
# Steganosaurus encodes a message into an image file.
#

import sys
import os
import argparse
from PIL import Image, UnidentifiedImageError

from henosisaurus import SteganoImage, encode_to_cluster, find_next_open
from kruptosaurus import hash_pixel

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

    if len(key) < 8:   # Additional key validation is needed
        print("Key must be at least 8 characters long, no spaces.")

    try:
        with open(text_fp, "r", -1, "utf-8") as text_file:

            img = SteganoImage(img_fp, key)
            ref_x = 0
            ref_y = 0

            buffer = text_file.read(1)
            while buffer != '':
                encode_to_cluster(buffer, ref_x, ref_y, img.pixelmap)
                img.occupied.add((ref_x, ref_y))
                ref_x, ref_y = find_next_open(ref_x, ref_y, img)
                buffer = text_file.read(1)

            encoded_img = Image.fromarray(img.pixelmap)
            encoded_img.save(result_fp)

            img.close_fp()   # Important to clean up open files

    except (OSError):
        print("Specified text file cannot be accessed.")

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

encode_text('./hipster-lorem-latin.txt', './testOverlay.jpg', './v2output.jpg', 'testingtesting')