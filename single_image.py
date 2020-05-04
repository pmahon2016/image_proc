from PIL import Image
from PIL.ExifTags import TAGS

# open files
def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image.getexif()


exif = get_exif('tablerock.jpeg') # included image

if exif:
    for k, v in exif.items():
        print(str([TAGS.get(k)]) + "\t" + str(v))
