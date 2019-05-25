# Steganomerge holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

from PIL import Image

def merge(im1, im2):
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
    while i < len(encipheredascii):
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
                if pixelchannel == 3:
                   coverrgba[coverpixel][pixelchannel] = (coverrgba[coverpixel][pixelchannel] - digit)
                else:
                    if coverrgba[coverpixel][pixelchannel] > 246:   # Reduce noise in resulting encoded image
                        coverrgba[coverpixel][pixelchannel] = (coverrgba[coverpixel][pixelchannel] - digit) % 256
                    else:
                        coverrgba[coverpixel][pixelchannel] = (coverrgba[coverpixel][pixelchannel] + digit) % 256
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

#print(merge(Image.open("exportImageTEST.png"), Image.open("encodedImage.png")))