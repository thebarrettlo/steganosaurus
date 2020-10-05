# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#
# Steganosaurus encodes a message into an image file.
#

import sys
import argparse
from PIL import Image, ImageDraw, ImageChops
from PIL.ExifTags import TAGS
import numpy as np
import random
from kruptosaurus import encode_to_cluster
from bitstring import BitArray, BitStream


def encode_text(imagePath, input_text, savekey):
    """
    Encodes user's text into an image file. The user defines their own save key for later message retrieval.

    Args:
        imagePath (str): filepath of the image to conceal the message within.
        input_text (str): text to encode. The length is bound by the number of pixels in the supplied image.
        savekey (str): a key to encrypt and decrypt the message. Can be any combination of letters, numbers,
                        and special characters. Must be at least 5 (five) characters long.

    Returns:
        Nothing. However, encode_text() does create a new image, exported-image.png.

    """

    # 1. Translate user input to ASCII values stored in a list
    ASCIIinput = []
    for char in input_text:  # Convert text into ASCII values
        ASCIIinput.append(ord(char))
    key = kruptosaurus.generate_key(savekey)  # Generate a key based on the user's save key
    random.seed(kruptosaurus.generate_key(key))  # Seed with the user-generated save key
    random.shuffle(ASCIIinput)  # Shuffle in user's message based upon their save key
    kruptosaurus.ASCIIshift(ASCIIinput, key)  # Shift the shuffled message

    # Get length of input and modify only that amount on the original picture
    # (and therefore, save that amount from the original picture)

    # 2. Load the input image
    input_image = Image.open(imagePath)
    input_image.load()
    input_image_exif = input_image.getexif()

    imgdescription = []
    for rgbtuple in list(input_image.getdata()):
        imgdescription.append(str(rgbtuple).replace(" ", "").replace("(", "").replace(")", ""))
    user_comment = ",".join(imgdescription[0:len(ASCIIinput)])
    input_image_exif[37510] = user_comment
    input_image_exif[42034] = 0  # Handles Lens Specification error - Pillow not able to save this data.

    # Handle case where x and y resolutions are tuples. Some images may not have this EXIF data existing, so
    # Pillow will throw a Key Error.
    try:
        if input_image_exif[282] and input_image_exif[283]:
            if len(input_image_exif[282]) > 1:
                input_image_exif[282] = input_image_exif[282][0] / input_image_exif[282][1]
            if len(input_image_exif[283]) > 1:
                input_image_exif[283] = input_image_exif[283][0] / input_image_exif[283][1]
    except:
        KeyError("No EXIF data!")

    exportimg = henosisaurus.write(input_image, ASCIIinput)  # Conceal the text into the cover image

    exportimg.save("exported-image.png", exif=input_image_exif)


def decode_text(input_image, savekey):
    """
    Decodes text contained in image that was encoded using Steganosaurus. User supplies a save key that
    will (potentially) retrieve the originally implanted message.

    Args:
        input_image (str): filepath of the image (potentially) with a concealed message.
        savekey (str): a key to encrypt and decrypt the message. Can be any combination of letters, numbers,
                        and special characters. Must be at least 5 (five) characters long.

    Returns:
        Nothing. However, a text file, decoded-text.txt, is created/written into containing the decoded
        text (if any exists within the supplied image).

    """

    coded_text = henosisaurus.read(Image.open(input_image))

    # Decode using save key
    temp = list(range(len(coded_text)))
    key = kruptosaurus.generate_key(savekey)
    kruptosaurus.deASCIIshift(coded_text, key)
    random.seed(kruptosaurus.generate_key(key))
    random.shuffle(temp)
    decoded_text = [None] * len(coded_text)
    with open("decoded-text.txt", "w") as textout:
        for i, x in enumerate(temp):
            decoded_text[x] = chr(coded_text[i])
        if decoded_text[0] is not None:
            textout.write("".join(decoded_text))

    print("".join(decoded_text))


def main():
    script = sys.argv[0]
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
        return encodeText(" ".join(filename[0:-1]), filename[-1])
    elif action == '--decode':
        return decodeText(filename[0], filename[1])

class SteganoImage:

    def __init__(self, fp: str):
        self.fp = fp
        self.pixelmap = np.array(Image.open(fp))
