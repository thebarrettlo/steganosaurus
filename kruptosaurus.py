# Kruptosaurus generates int for random.seed() from a given save key.
# Barrett Lo
# 24 May, 2019
#

import math
import secrets
from henosisaurus import *

RED = 0
GREEN = 1
BLUE = 2
NUM_CHANNELS = 3


def generate_key(savekey):
    """Generates a key from the given save key. The save key must be between five and twenty characters, and may include
    uppercase, lowercase, numbers, and special characters."""

    # Convert save key to integer values
    keyarray = list(str(savekey))
    i = 0
    for char in keyarray:
        keyarray[i] = ord(char)
        i += 1

    # Mathematically manipulate save key values
    keyval = int(((((keyarray[0] % keyarray[1]) * sum(keyarray[3:-1])) * math.exp(keyarray[2])) // keyarray[-1]))

    return keyval


def ASCIIshift(ascii_array, savekey):
    """ASCIIshift shifts all ASCII values in an array by an amount determined by the save key."""

    key = sum([int(i) for i in list(str(generate_key(savekey)))]) + 100

    i = 0
    while i < len(ascii_array):
        ascii_array[i] = (ascii_array[i] + key) % 256
        i += 1

    return ascii_array


def deASCIIshift(ascii_array, savekey):
    """ASCIIshift un-shifts all ASCII values in an array by an amount determined by the save key."""

    key = sum([int(i) for i in list(str(generate_key(savekey)))]) + 100

    i = 0
    while i < len(ascii_array):
        ascii_array[i] = (ascii_array[i] - key) % 256
        i += 1

    return ascii_array

def encode_to_cluster(char: str, ref_x: int, ref_y: int, pixelmap):
    """
    Encodes char to a cluster of pixels, starting with the reference pixel
    at (ref_x, ref_y). Red channel, green channel, then blue channel, are
    encoded at bits 0 and 1 before moving to the next pixel (pixel to the
    right (x+1) until x = ref_x+2 then next pixel is (ref_x, ref_y-1) up
    one pixel and a new row of three.
    """

    byte_len = check_num_bytes(char)
    char_bits = BitArray(char.encode('utf-8')).bin
    clear_mask = int('11111100', 2)
    curr_x = ref_x
    curr_y = ref_y
    channel = 0   # Cycles between RED (0), GREEN (1), and BLUE (2)

    # Add check that (x, y) will stay in bounds?

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

    return None

def mask_channel(mask: int, channel: int) -> int:
    """
    Changes bits 0 and 1 of channel to the masked bits. Mask must be
    ones except for bits 0 and 1 (may be 0 or 1).
    Returns:
        Modified channel as an int.
    """
    return mask & channel

def hash_pixel(rgb_int: list) -> int:
    """Uses mid-square method to generate an int from 0-9999"""

    hash_int = 17
    channels_total = 1

    for i in rgb_int:   # Creates an 8-digit number
        hash_int += (hash_int * i)
        if i == 0:
            i = hash_int
        if i < 10:
            i = i << 7
        elif i < 100:
            i = i << 4
        channels_total *= i

    channels_total %= 9999  # Restrict to four digits
    return ((channels_total**2) // 100) % 10000    # Get middle four digits

# rgb_int = [24, 66, 204]
# print(hash(rgb_int, 256))
# rgb_int = [25, 66, 204]
# print(hash(rgb_int, 256))
# rgb_int = [25, 68, 204]
# print(hash(rgb_int, 256))
# rgb_int = [224, 33, 170]
# print(hash(rgb_int, 256))