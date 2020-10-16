# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#
# Steganosaurus encodes a message into an image file.
#

import sys
import argparse
from PIL import Image, UnidentifiedImageError
from henosisaurus import encode_text

def main(text_fp: str, img_fp: str, result_fp: str, key: str):
    
    if not validate_input(img_fp, key):
        return 1

    return encode_text(text_fp, img_fp, result_fp, key)

def validate_input(img_fp: str, key: str) -> bool:
    """
    Validates input parameters.
    
    Returns:
        True if all inputs are valid, false otherwise.
    
    To be implemented:
        - Validtion of result_fp as graphic file format
    """

    valid = False

    try:
        with Image.open(img_fp) as og_img:
            valid = True
    except (FileNotFoundError, UnidentifiedImageError):
        print("Specified image cannot be found or opened.")
    except Exception as e:
        print(e)

    if len(key) < 8:   # Additional key validation is needed
        print("Key must be at least 8 characters long, no spaces.")
        valid = False

    return valid 


# def main():
#     """inputs = []
#     parser = argparse.ArgumentParser(description='Encode/Decode text into/from an image, using a save key. ' +
#     'The save key must be at least 5 characters long and can be made up of uppercase and lowercase letters, ' +
#     'numbers, and special characters.')
#     parser.add_argument('text input', metavar='text', type=str, nargs='+', help='Text to be encoded.')
#     parser.add_argument('save key', metavar='key', type=open, help='Key to encrypt/decrypt message into image.')
#     parser.add_argument('--encode', '-e', dest='', action='store', help='Encode the given text into an image.')
#     parser.add_argument('--decode', '-d', dest='', action='store', help='Decode the text within in image.')
#     args = parser.parse_args('test', inputs)"""
#     try:
#         action = sys.argv[1]
#         userinputs = sys.argv[2:]
#         assert action in ['--encode', '--decode'], \
#             "Action is not --encode or --decode: " + action

#         process(userinputs, action)
#     except:
#         raise IOError("Proper input format is --encode or --decode followed by a string and then a save key. "
#             "The save key must be at least five characters long and can be made up of uppercase and lowercase "
#                 "letters, numbers, and special characters.")
    
# def process(filename, action):

#     if action == '--encode':
#         return encode_text(" ".join(filename[0:-1]), filename[-1])
#     elif action == '--decode':
#         return decode_text(filename[0], filename[1])


# main('./hipster-lorem-latin.txt', './testOverlay.jpg', './v2output.png', 'testingtesting')