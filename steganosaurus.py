# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#

from PIL import Image, ImageDraw

def encodeText(input_text):
    """Encodes user's text into an image file. Takes user's text and image to cover up the coded image."""

    # Translate user input to ASCII values stored in a list
    ASCIIinput = []
    for char in input_text:
        ASCIIinput.append(ord(char))

    # Initialize blank image for encoding
    width = 300
    height = 500
    template = Image.new("RGBA", (width, height))
    splitted = template.split() # Split into R, G, B, A channels

    # Change pixel colors
    draw = ImageDraw.Draw(template)
    x = 0
    y = 0

    i = 0
    while i < (len(ASCIIinput) - (len(ASCIIinput) % 3)):
        draw.point([(x, y)], (ASCIIinput[i], ASCIIinput[i+1], ASCIIinput[i+2]))
        i += 3
        x += 1
        if x > width:
            x = 0
            y += 1
            if y > height:
                raise IndexError("Message too tall!")
    # End case for inputs not a multiple of 3
    if (len(ASCIIinput) % 3) == 1:
        draw.point([(x, y)], (ASCIIinput[i], 0, 0))
    elif (len(ASCIIinput) % 3) == 2:
        draw.point([(x, y)], (ASCIIinput[i], ASCIIinput[i+1], 0))

    template.save("encodedImage.png")
