# STEGANOSAURUS by Barrett Lo
# Begun on May 22, 2019
#
# Steganosaurus encodes a message into an image file.
#

from PIL import Image, ImageDraw, ImageChops
from PIL.ExifTags import TAGS
import random
import steganoseed
import steganomerge

def encodeText(input_text, savekey):
    """Encodes user's text into an image file. Takes user's text and image to cover up the coded image."""
    
    # Translate user input to ASCII values stored in a list
    ASCIIinput = []
    for char in input_text:
        ASCIIinput.append(ord(char))
    key = steganoseed.generate_key(savekey)
    steganoseed.ASCIIshift(ASCIIinput, key)
    random.seed(steganoseed.generate_key(key))   # User-generated save key for decoding
    random.shuffle(ASCIIinput)

    # Initialize blank image for encoding
    tempcover = Image.open("./testOverlay.png")
    tempcover.load()
    coverimg = Image.new("RGBA", tempcover.size, (255,255,255,0))
    coverimg.paste(tempcover)
    coverimgexif = coverimg.getexif()
    imgdescription = []
    for rgbtuple in list(coverimg.getdata()):
        imgdescription.append(str(rgbtuple).replace(" ", ""))
    coverimgexif[0x010e] = "".join(imgdescription)

    width = coverimg.width
    height = coverimg.height
    template = Image.new("RGB", (width, height))

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
    
    # Conceal the text into the cover image
    exportimg = steganomerge.merge(coverimg, template)
    exportimg.save("exportImageTEST.png", exif=coverimgexif)


def decodeText(input_image, savekey):
    """Decodes text contained in image that was encoded using Steganosaurus."""
    
    img = Image.open(input_image)
    coded_text = []

    # Pull the encoded pixels
    for i in list(img.getdata()):
        if i[3] == 255:
            coded_text.append(i[0])
        if i[1] != 0:
            coded_text.append(i[1])
        if i[2] != 0:
            coded_text.append(i[2])

    # Decode using save key
    temp = range(len(coded_text))
    key = steganoseed.generate_key(savekey)
    steganoseed.deASCIIshift(coded_text, key)
    random.seed(steganoseed.generate_key(key))
    random.shuffle(temp)
    decoded_text = [None] * len(coded_text)
    for i, x in enumerate(temp):
        decoded_text[x] = chr(coded_text[i])
    
    return "".join(decoded_text)


encodeText("Lorem ipsum dolor sit amet, amet accusam sea in, justo tation ut mel? Nostro utamur te nam, ex omnesque oportere nam. Vix ut summo audire consequuntur! Solet qualisque in sit! In vim posse forensibus, ut usu clita facete. Mel an omnis prima interesset, vel alii abhorreant et, et est reque paulo fastidii! No mel choro petentium vituperatoribus. Nec ut graece abhorreant. Ex ius modus homero honestatis, ne pri enim saepe oportere. Omnis perfecto mei id. Consul vituperata per eu? At dicam dolorem inciderint eum. Ut eos summo tamquam, qui no affert fuisset mnesarchum, pro id quot blandit! Rationibus quaerendum his ut, nostrud reformidans ullamcorper sea in, utinam fastidii reprimique ad nec.", "1d3#J%")

img = Image.open("exportImageTEST.png")
print(len(img.getexif()[270]))
