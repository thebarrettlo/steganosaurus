# Kruptosaurus generates int for random.seed() from a given save key.
# Barrett Lo
# 24 May, 2019
#

import math

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

def hash_pixel(pixel: list) -> int:
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

    channels_total %= 9999  # Restrict to four digits
    return ((channels_total**2) // 100) % 10000    # Get middle four digits

pixel = [24, 66, 204]
print(hash_pixel(pixel))
pixel = [25, 66, 204]
print(hash_pixel(pixel))
pixel = [25, 68, 204]
print(hash_pixel(pixel))
pixel = [224, 33, 170]
print(hash_pixel(pixel))
pixel = [1, 0, 3]
print(hash_pixel(pixel))