# Kruptosaurus generates int for random.seed() from a given save key.
# Barrett Lo
# 24 May, 2019
#

import math
import numpy as np


def hash_pixel(pixel: list, key: int) -> int:
    """Uses mid-square method to generate an int from 0-9999"""

    hash_int = 17
    channels_total = 1

    for i in pixel:   # Creates an 8-digit number
        hash_int += (hash_int * i)
        if i == 0:
            i = hash_int
        if i < 10:
            i = i << 7
        elif i < 100:
            i = i << 4
        channels_total *= i

    channels_total += key
    channels_total %= 9999  # Restrict to four digits
    return ((channels_total**2) // 100) % 10000    # Get middle four digits
