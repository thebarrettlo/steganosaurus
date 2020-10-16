# Henosisaurus holds operations for blending and de-blending two images -- but not in
# the typical alpha factor sense. Merging with steganomerge will simply add the color bit
# values and mark the pixels that contain information (through the alpha layer).
#
# Created by Barrett Lo
# 25 May, 2019
#

import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import piexif
from typing import TextIO
from bitstring import BitArray, BitStream

ONE_BYTE = 1
TWO_BYTES = 2
THREE_BYTES = 3
FOUR_BYTES = 4


class SteganoImage:

    def __init__(self, fp: str, key: str):
        self.fp = fp
        self.pillow_img = Image.open(fp)
        self.pixelmap = np.array(self.pillow_img)
        self.occupied = set()
        self.key = key
        # for char in key:
        #     self.key += ord(char)

    def close_fp(self):
        self.pillow_img.close()


class Buffer():
    
    def __init__(self):
        self.buffer = 0
        self.bit_pos = 0


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

def encode_text(text_fp: str, img_fp: str, result_fp: str, key: str) -> int:
    """
    Main process for encoding text (UTF-8 encoded) from a file into
    an 8-bit, three-color image. Creates a SteganoImage() instance
    for managing the pixel data.

    Returns:
        A copy of the given image with the given message hidden
        within, at result_fp. If the text file is empty, returns
        the given image unaltered.
    """

    try:
        with open(text_fp, "r", encoding="utf-8") as text_file:

            img = SteganoImage(img_fp, key)
            ref_table = generate_reference_array(img)
            buffer = Buffer()
            curr_pixel = 0
            pixel_max = len(ref_table)

            fill_buffer(buffer, text_file)
            while buffer.bit_pos > 0:
                encode_pixel(img, buffer, ref_table[curr_pixel])
                curr_pixel += 1

                if curr_pixel == pixel_max:
                    print("Max amount of characters encoded. Please provide a larger image for more characters.")
                    break

                if buffer.bit_pos < 6:
                    fill_buffer(buffer, text_file)

            encoded_img = Image.fromarray(img.pixelmap)
            encoded_img.save(result_fp)

            if img.pillow_img.format == "JPEG" or img.pillow_img.format == "TIFF":
                try:
                    piexif.transplant(img_fp, result_fp)
                except ValueError:
                    pass

            img.close_fp()   # Important to clean up open files
    except (OSError):
        print("Specified text file cannot be accessed.")
        return 1

    return 0

def fill_buffer(buffer: Buffer, text_file: TextIO) -> int:
    """
    Gets a character from the text file and puts it into the buffer. buffer should
    be at least a 32 bit int.

    Returns:
        0 on success, 1 if fail.
    """

    next_char = text_file.read(1)
    if next_char == '':
        return 1

    num_bits = check_num_bytes(next_char) * 8

    buffer.buffer = buffer.buffer << (num_bits)
    buffer.buffer |= ord(next_char)

    buffer.bit_pos += (num_bits - 1)

    return 0

def encode_pixel(img: SteganoImage, buffer: Buffer, curr_pixel: int) -> int:
    """
    Encodes six bits from the buffer into a pixel (2 bits per channel). The
    buffer is adjusted within this function.

    Returns:
        0 on success, 1 if failure writing from buffer.
    """
    # Can't I use BitArray for all of this? Isn't that the point...?
    y = curr_pixel // (img.pixelmap.shape[0])
    x = curr_pixel % (img.pixelmap.shape[1] - 1)
    clear_mask = int('11111100', 2)
    curr_shift = buffer.bit_pos
    bit_mask = int('11', 2) << curr_shift
    
    if buffer.bit_pos > 4:
        num_channels = 3
    elif buffer.bit_pos > 2:
        num_channels = 2
    else:
        num_channels = 1

    for channel in range(num_channels):
        data_mask = (bit_mask & buffer.buffer) >> curr_shift
        buffer.buffer |= ~bit_mask   # Clear bits in buffer

        img.pixelmap[y][x][channel] &= clear_mask
        img.pixelmap[y][x][channel] |= data_mask

        curr_shift -= 2
        bit_mask = bit_mask >> 2

    buffer.bit_pos -= 2 * num_channels
    
    return 0

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

def generate_reference_array(img: SteganoImage) -> np.ndarray:
    """
    Generates a 1-dimensional array with values corresponding to locations (indices) of
    pixels on the original image. Values are shuffled to be referenced when
    encoding or decoding text onto image.

    Returns:
        An ndarray with shuffled random numbers from [0, w x h]
    """

    height = img.pixelmap.shape[0]
    width = img.pixelmap.shape[1]

    ref_table = np.arange(0, height * width, 1, int)
    shuffler = np.random.default_rng([ord(char) for char in img.key])
    shuffler.shuffle(ref_table, axis=0)

    return ref_table

def generate_reference_table(img: SteganoImage) -> np.ndarray:
    """
    Generates a table with values corresponding to locations (indices) of
    pixels on the original image. Values are shuffled to be referenced when
    encoding or decoding text onto image.

    Returns:
        An ndarray with a width and height of img.
    """

    height = img.pixelmap.shape[0]
    width = img.pixelmap.shape[1]

    ref_table = np.arange(0, height * width, 1, int).reshape(height, width)
    shuffler = np.random.default_rng([ord(char) for char in img.key])
    
    shuffler.shuffle(ref_table, axis=0)
    shuffler.shuffle(ref_table, axis=1)

    return ref_table
