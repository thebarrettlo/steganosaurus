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
    keyval = int(((((keyarray[0] % keyarray[1]) % sum(keyarray[3:-1])) * math.exp(keyarray[2])) // keyarray[-1]))

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
