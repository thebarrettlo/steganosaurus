# Henosisaurus holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

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

def find_next_open(ref_x: int, ref_y: int, pixelmap: list, occupied: set) -> (int, int):
    """
    Hashes the pixels at the current location (ref_x, ref_y) and creates
    an offset to the next open location (not in occupied). Validates that
    the new location has a 3x2 pixels space for a character cluster

    Returns:
        x and y coordinates of the next open location
    """

    next_x = ref_x
    next_y = ref_y
    y_add = False   # False == subtract
    x_add = True
    img_height = pixelmap.shape[0]
    img_width = pixelmap.shape[1]

    y_offset = (hash_pixel(pixelmap[ref_y][ref_x]) % img_height) + 2
    x_offset = (hash_pixel(pixelmap[ref_y][ref_x + 1]) % img_width) + 2
    if y_offset % 2 == 1:
        y_offset = -(y_offset + 1)
        y_add = not y_add
    if x_offset % 2 == 1:
        x_offset = -(x_offset + 1)
        x_add = not x_add

    while (next_x + x_offset, next_y + y_offset) in occupied:
        if y_offset == img_height:
            if x_offset == img_width:
                break
            x_offset += 2
        else:
            y_offset += 2

    # Validate new coordinates have room for a cluster

    return next_x + x_offset, next_y + y_offset

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
