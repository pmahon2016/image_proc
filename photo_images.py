from PIL import Image
from PIL.ExifTags import TAGS
import os
import re
from pathlib import Path

logfile = open('image_log.txt','a')

def image_meta(filename):
    try:
        image = Image.open(filename)
        exifdata = image._getexif()

        if exifdata:
            make = exifdata.get(271)
            model = exifdata.get(272)
            date_gen = exifdata.get(36867)

            print("{:20.20} \t {:<20} \t {:10.10} \t {}".format(str(make), str(model), str(date_gen), filename))

        else:
            logfile.write(str(filename) + " does not have exit data \n")

    except:
        logfile.write(str(filename) + "is an incompatible format \n")


for fname in Path('YOUR PATH HERE').rglob('*'):
    if re.search(r'\.jpg$|\.png$|\.bmp$', str(fname), re.IGNORECASE):
        try:
            image_meta(fname)
        except:
            logfile.write(str(fname) + " is bad file \n")

logfile.close()
