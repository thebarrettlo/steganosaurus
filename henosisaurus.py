# Henosisaurus holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

from PIL import Image
import piexif
import piexif.helper


def write(im1, ascii_list): # !!! FIX WHEN 0 CHANGE TO 255 ALPHA LAYER
    """write() adds each separate digit of the transcibed text's ASCII values to an
    R, G, B, or Alpha value of the cover image. Takes two Image objects. Returns the first
    image (im1) object with the second image (im2) concealed within it."""

    im1.load()   # Cover image
    # im2.load()   # Cipher text

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

    for pix in coverrgba:   # Convert the cover image RGB values back to tuples for image export
        coverrgba[i] = tuple(pix)
        i += 1

    mergedimage = Image.new("RGB", im1.size)
    mergedimage.putdata(coverrgba)

    return mergedimage


def read(im):
    """read() finds the difference between each separate digit of the transcibed text's ASCII values
    to an R, G, B, or Alpha value of the cover image. Takes one Image object. Returns two image objects:
    the coded image and the cover image."""
    
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
    codedlist = _combinetorgbtuple(codedlist)
    codedimg = Image.new("RGB", im.size)
    codedimg.putdata(codedlist)

    return codedimg, im

def _separatetorgb(vals):
    """_separatetorgb() takes a list of integer values and turns them into 4-value lists within a list."""

    i = 0
    out = []
    while i < len(vals):
        out.append(vals[i:i + 3])
        i += 3

    return out

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

#print(merge(Image.open("exportImageTEST.png"), Image.open("encodedImage.png")))
#print(demerge(Image.open("exportImageTEST.png")))