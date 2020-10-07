# Henosisaurus holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

import numpy as np
from PIL import Image
from bitstring import BitArray, BitStream
from kruptosaurus import hash_pixel

ONE_BYTE = 1
TWO_BYTES = 2
THREE_BYTES = 3
FOUR_BYTES = 4

RED = 0
GREEN = 1
BLUE = 2
NUM_CHANNELS = 3

NEG = -1
POS = 1

class SteganoImage:

    def __init__(self, fp: str, key: str):
        self.fp = fp
        self.pillow_img = Image.open(fp)
        self.pixelmap = np.array(self.pillow_img)
        self.occupied = set()
        self.key = 0
        for char in key:
            self.key += ord(char)

    def close_fp(self):
        self.pillow_img.close()

def encode_to_cluster(char: str, ref_x: int, ref_y: int, pixelmap: list) -> int:
    """
    Encodes char to a cluster of pixels, starting with the reference pixel
    at (ref_x, ref_y). Red channel, green channel, then blue channel, are
    encoded at bits 0 and 1 before moving to the next pixel (pixel to the
    right (x+1) until x = ref_x+2 then next pixel is (ref_x, ref_y-1) up
    one pixel and a new row of three.
    
    Returns:
        The number of bits that the character took up, as an int
    """

    byte_len = check_num_bytes(char)
    char_bits = BitArray(char.encode('utf-8')).bin
    clear_mask = int('11111100', 2)
    curr_x = ref_x
    curr_y = ref_y
    channel = RED   # Cycles between RED (0), GREEN (1), and BLUE (2)

    for bindex in range(0, byte_len * 8, 2):
        data_mask = int(char_bits[bindex:bindex+2], 2)
        pixelmap[curr_y][curr_x][channel] &= clear_mask
        pixelmap[curr_y][curr_x][channel] |= data_mask

        channel += 1
        if channel == BLUE + 1:
            curr_x += 1
            if curr_x == ref_x + 3:
                curr_x = 0
                curr_y -= 1
            channel = RED

    return byte_len * 8

def find_next_open(ref_x: int, ref_y: int, img: SteganoImage) -> (int, int):
    """
    Hashes the pixels at the current location (ref_x, ref_y) and creates
    an offset to the next open location (not in occupied). Validates that
    the new location has a 3x2 pixels space for a character cluster

    Returns:
        x and y coordinates of the next open location
    """

    next_x = ref_x
    x_sign = y_sign = POS
    img_height = img.pixelmap.shape[0]
    img_width = img.pixelmap.shape[1]
    x_boundary = 0

    y_offset = (hash_pixel(img.pixelmap[ref_y][ref_x], img.key) % img_height)
    x_offset = (hash_pixel(img.pixelmap[ref_y][ref_x + 1], img.key) % img_width)
    if y_offset % 2 == 1:
        y_offset = -(y_offset + 1)
        y_sign = NEG
    if x_offset % 3 == 2:
        x_offset = -(x_offset + 1)
        x_sign = NEG
    elif x_offset % 3 == 1:
        x_offset += 2

    # print("y_offset: " + str(y_offset))
    # print("x_offset: " + str(x_offset))

    if ref_y + y_offset < 0:
        y_offset = -ref_y
    elif ref_y + y_offset >= img_height - 1:
        y_offset = img_height - ref_y - 2 - (img_height % 2)
    next_y = ref_y + y_offset
    if ref_x + x_offset < 0:
        x_offset = -ref_x
    elif ref_x + x_offset >= img_width - ref_x - 4:
        x_offset = img_width - ref_x - 5 - (img_width % 3)
    next_x = ref_x + x_offset
    
    # print("next_y: " + str(next_y) + " " + str(y_sign))
    # print("next_x: " + str(next_x) + " " + str(x_sign))

    while True:
        next_y = _find_open_y(next_x, ref_y, y_offset, y_sign, img)
        if next_y == ref_y:
            next_x = next_x + 3 * x_sign
            if next_x < 0 or img_width - 1 - next_x < 3:
                x_boundary += 1
                x_sign = -x_sign
                next_x = ref_x + x_offset + 3 * x_sign
                # print("Hit x boundary")
            if x_boundary == 2:
                print(ref_x)
                print(ref_y)
                print(len(img.occupied))
                raise IndexError("No open space!")
        else:
            break

    return next_x, next_y

def _find_open_y(next_x: int, ref_y: int, y_offset: int, y_sign: int, img: SteganoImage):
    
    next_y = ref_y + y_offset
    img_height = img.pixelmap.shape[0]
    y_boundary = 0

    # Try one y-direction first
    while ((next_x, next_y) in img.occupied):
        next_y = next_y + 2 * y_sign
        if next_y < 0 or next_y >= img_height:
            y_boundary += 1
            y_sign = -y_sign
            next_y = ref_y + y_offset + 2 * y_sign
            # print("Hit y boundary")
        if y_boundary == 2:
            # print("No open y in second direction")
            return ref_y

    return next_y

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

# img = SteganoImage('./16x16_dot.jpg')
# for x in range(0, 15, 3):
#     for y in range(0, 15, 2):
#         img.occupied.add((x, y))
# img.occupied.add((1, 2))
# img.occupied.add((1, 4))
# img.occupied.add((1, 6))
# img.occupied.add((1, 8))
# img.occupied.add((8, 8))
# img.occupied.add((1, 10))
# img.occupied.add((1, 12))
# img.occupied.add((1, 14))
# img.occupied.add((2, 8))
# img.occupied.add((5, 8))
# img.occupied.add((11, 8))
# img.occupied.add((14, 8))
# print(find_next_open(0, 0, img))