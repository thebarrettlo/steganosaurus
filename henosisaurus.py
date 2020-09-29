# Henosisaurus holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

from PIL import Image
from bitstring import BitArray, BitStream

ONE_BYTE = 1
TWO_BYTES = 2
THREE_BYTES = 3
FOUR_BYTES = 4

def merge(im1, im2): # !!! FIX WHEN 0 CHANGE TO 255 ALPHA LAYER
    """Merge() adds each separate digit of the transcibed text's ASCII values to an
    R, G, B, or Alpha value of the cover image. Takes two Image objects. Returns the first
    image (im1) object with the second image (im2) concealed within it."""

    im1.load()   # Cover image
    im2.load()   # Cipher text

    # Get pixel data from images
    coverrgba = [list(pix) for pix in list(im1.getdata())]
    encipheredascii = [char for tup in list(im2.getdata()) for char in tup]
    coverpixel = 0   # Counter for current pixel on cover image
    pixelchannel = 0   # Counter for current channel of current pixel on cover image
    i = 0   # Counter for current encipheredascii number
    while encipheredascii[i] > 0:
        curr = [int(a) for a in str(encipheredascii[i])]
        # Ensure all pixel values are three digits long; necessary for accurate decoding
        if len(curr) == 1:
            curr = [0, 0] + curr
        elif len(curr) == 2:
            curr = [0] + curr
        for digit in curr:   # Add the next cipher text digit to the next cover image pixel channel
            if digit == 0:
                pixelchannel += 1
            else:
                if coverrgba[coverpixel][pixelchannel] < 247:   # Reduce noise in resulting encoded image
                    coverrgba[coverpixel][pixelchannel] = (coverrgba[coverpixel][pixelchannel] + digit)
                else:
                    coverrgba[coverpixel][pixelchannel] = (coverrgba[coverpixel][pixelchannel] - digit)
                pixelchannel +=1
            if pixelchannel > 3:
                coverpixel += 1
                pixelchannel = 0
        i += 1

    i = 0
    for pix in coverrgba:   # Convert the cover image RGBA values back to tuples for image export
        coverrgba[i] = tuple(pix)
        i += 1

    mergedimage = Image.new("RGBA", im1.size)
    mergedimage.putdata(coverrgba)

    return mergedimage


def demerge(im):
    """Demerge() finds the difference between each separate digit of the transcibed text's ASCII values
    to an R, G, B, or Alpha value of the cover image. Takes one Image object. Returns two image objects:
    the coded image and the cover image."""
    
    # Get pixel data from images
    im.load()
    coverrgba = [list(pix) for pix in list(im.getdata())]
    imgexif = _separatetorgba([int(a) for a in str(im.getexif()[270]).split(",")])
    codedlist = []
    i = 0   # Counter for pixel channel pointer
    j = 0   # Channel pointer counter
    while coverrgba[i] != imgexif[i]:
        for channel in coverrgba[i]:
            if imgexif[i][j] < 247:
                codedlist.append(channel - imgexif[i][j])
            else:
                codedlist.append((imgexif[i][j]) - channel)
            j += 1
            if j == 4:
                j = 0
        i += 1
    codedlist = _combinetorgbtuple(codedlist)
    codedimg = Image.new("RGB", im.size)
    codedimg.putdata(codedlist)

    return codedimg, im

def _separatetorgba(vals):
    """_listtorgbatuple() takes a list of integer values and turns them into 4-value lists within a list."""

    i = 0
    out = []
    while i < len(vals):
        out.append(vals[i:i+4])
        i += 4
    
    return out


def _combinetorgbtuple(vals):
    """_combinetorgbtuple() takes a list of integer values (single digits) and turns them into 3-value tuples within a list."""
    
    vals = vals + [0] * (9 - (len(vals) % 9))  # Ensures that there will be a full tuple to post

    i = 0
    out = []
    while i < len(vals):
        curr = (int("".join(map(str, vals[i:i+3]))), int("".join(map(str, vals[i+3:i+6]))), int("".join(map(str, vals[i+6:i+9]))))
        out.append(curr)
        i += 9

    return out

def check_num_bytes(utf_char: str) -> int:
    """
    Checks length of UTF-8 encoded character.
        utf_char: Character encoded with UTF-8
    Returns:
        0 = not UTF-8 encoded
        1 = 1 byte
        2 = 2 bytes
        3 = 3 bytes
        4 = 4 bytes
    """

    mask = BitArray(utf_char.encode('utf-8')).bin

    if mask[0] == '0':
        return ONE_BYTE
    elif mask[2] == '0':
        return TWO_BYTES
    elif mask[3] == '0':
        return THREE_BYTES
    elif mask[4] == '0':
        return FOUR_BYTES
    
    return 0
