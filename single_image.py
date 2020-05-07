from PIL import Image
from PIL.ExifTags import TAGS

# open test
def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif()

# extract the exif data from image file
exif = get_exif('tablerock.jpeg') # included image

# Loop through tags for print out
if exif:
    for k, v in exif.items():
        print(str([TAGS.get(k)]) + "\t" + str(v))
