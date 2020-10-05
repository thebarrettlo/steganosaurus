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

def encodeText(input_text, savekey):
    """Encodes user's text into an image file. Takes user's text and image to cover up the coded image."""

    # Translate user input to ASCII values stored in a list
    ASCIIinput = []
    for char in input_text:
        ASCIIinput.append(ord(char))
    key = kruptosaurus.generate_key(savekey)
    random.seed(kruptosaurus.generate_key(key))   # User-generated save key for decoding
    random.shuffle(ASCIIinput)
    kruptosaurus.ASCIIshift(ASCIIinput, key)

    # Initialize blank image for encoding
    tempcover = Image.open("./testOverlay.png")
    tempcover.load()
    coverimg = Image.new("RGBA", tempcover.size, (255,255,255,0))
    coverimg.paste(tempcover)
    coverimgexif = coverimg.getexif()   # Store original cover image data in Image Description metadata
    imgdescription = []
    for rgbtuple in list(coverimg.getdata()):
        imgdescription.append(str(rgbtuple).replace(" ", "").replace("(", "").replace(")", ""))
    coverimgexif[270] = ",".join(imgdescription)

    width = coverimg.width
    height = coverimg.height
    template = Image.new("RGB", (width, height))

    # Change pixel colors
    draw = ImageDraw.Draw(template)
    x = 0
    y = 0
    i = 0
    while i < (len(ASCIIinput) - (len(ASCIIinput) % 3)):
        draw.point([(x, y)], (ASCIIinput[i], ASCIIinput[i+1], ASCIIinput[i+2]))
        i += 3
        x += 1
        if x >= width:
            x = 0
            y += 1
            if y >= height:
                raise IndexError("Message too tall!")
    # End case for inputs not a multiple of 3
    if (len(ASCIIinput) % 3) == 1:
        draw.point([(x, y)], (ASCIIinput[i], 0, 0))
    elif (len(ASCIIinput) % 3) == 2:
        draw.point([(x, y)], (ASCIIinput[i], ASCIIinput[i+1], 0))
    
    # Conceal the text into the cover image
    exportimg = henosisaurus.merge(coverimg, template)
    exportimg.save("exported-image.png", exif=coverimgexif)


def decodeText(input_image, savekey):
    """Decodes text contained in image that was encoded using Steganosaurus."""
    
    img, coverimg = henosisaurus.demerge(Image.open(input_image))

    # Pull the encoded pixels
    coded_text = [char for tup in list(img.getdata()) for char in tup]
    i = 0
    while coded_text[i] != 0:
        i += 1
    coded_text = coded_text[:i]

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
