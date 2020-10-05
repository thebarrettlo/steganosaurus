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


def write(im1, ascii_list):
    """
    Adds each separate digit of the transcibed text's ASCII values to a Red, Green, or Blue value of the cover image.
    Takes an image and a list of ASCII values. Returns the first image with the ASCII values concealed within it.

    Args:
        im1 (Image): Image object (from PIL) to be written on.
        ascii_list (list): list of characters in ASCII value.

    Returns:
        mergedimage (Image): Image object (from PIL) with the text written into the image.

    """

    im1.load()   # Cover image

    # Get pixel data from images
    coverrgba = [list(pix) for pix in list(im1.getdata())]
    coverpixel = 0   # Counter for current pixel on cover image
    pixelchannel = 0   # Counter for current channel of current pixel on cover image
    i = 0   # Counter for current encipheredascii number

    for char in ascii_list:
        curr = [int(a) for a in str(char)]
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
                pixelchannel += 1
            if pixelchannel > 2:
                coverpixel += 1
                pixelchannel = 0
        i += 1

    i = 0
    for pix in coverrgba:   # Convert the cover image RGBA values back to tuples for image export
        coverrgba[i] = tuple(pix)
        i += 1

    mergedimage = Image.new("RGB", im1.size)
    mergedimage.putdata(coverrgba)

    return mergedimage


def read(im):
    """
        Finds the difference between each pixel (and their color channels) on the image and its original
        value from the EXIF UserComment.

        Args:
            im (Image): Image object (from PIL) to be written on.

        Returns:
            mergedimage (Image): Image object (from PIL) with the text written into the image.

        """
    
    # Get pixel data from images
    im.load()
    imagepixels = [list(pix) for pix in list(im.getdata())]
    image_exif = im.getexif()
    user_comment = image_exif[37510]
    usercomment_exif = _separatetorgb([int(a) for a in user_comment.split(",")])
    codedlist = []
    i = 0   # Counter for pixel channel pointer
    j = 0   # Channel pointer counter
    while i < len(usercomment_exif):
        for channel in imagepixels[i]:
            if usercomment_exif[i][j] < 247:
                codedlist.append(channel - usercomment_exif[i][j])
            else:
                codedlist.append((usercomment_exif[i][j]) - channel)
            j += 1
            if j == 3:
                j = 0
        i += 1
    codedlist = _combine(codedlist)

    return codedlist


def _separatetorgb(vals):
    """_separatetorgb() takes a list of integer values and turns them into 4-value lists within a list."""

    i = 0
    out = []
    while i < len(vals):
        out.append(vals[i:i + 3])
        i += 3

    return out


def _combine(vals):
    """
    Takes a list of integer values (single digits) and combines them in threes (leading zeroes are
    counted but thrown out.

    Args:
        vals (List): list of single digits.

    Returns:
        out (List): list of more complete digits.

    """

    i = 0
    out = []
    while i < len(vals):
        curr = int("".join(map(str, vals[i:i + 3])))
        out.append(curr)
        i += 3

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

# test = BitArray('a'.encode('utf-8')).bin
# print(test)
# print(int(test[1:3], 2))
# mask_template = int('11111100', 2)
# mask = int(test[0:2], 2) | mask_template
# print(BitArray(uint=mask, length=8).bin)
