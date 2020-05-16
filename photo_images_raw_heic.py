from PIL import Image
from pathlib import Path  # search within directories and subdirectories
import io
import pyheif # for heic files
import exifread # for heic files
import re  # regex - used ot search through text files
import os  # operating sys ( may work differently on a PC)

logfile = open('imagelog.txt', 'a')  # all files that are not printed out below will logged here


def get_exif_data(ifile):  # if the file is a standard image file
    if re.search(r'jpeg$|bmp$|png$|jpg$', str(ifile), re.IGNORECASE):
        image = Image.open(ifile)
        exifdata = image.getexif()
        return exifdata.get(271), exifdata.get(272), exifdata.get(36867), ifile

    elif re.search(r'heic$', str(ifile), re.IGNORECASE):  # if an Apple Heic file

        heif_file = pyheif.read_heif(str(ifile))

        for metadata in heif_file.metadata:

            if metadata['type'] == 'Exif':
                fstream = io.BytesIO(metadata['data'][6:])

        tags = exifread.process_file(fstream, details=False)

        return str(tags.get("Image Make")), str(tags.get("Image Model")), str(tags.get('EXIF DateTimeOriginal')), ifile

    elif re.search(r'CR2$|NEF$', str(ifile), re.IGNORECASE):  # for raw files. Canon and NIkon is this case.
        f = open(ifile, 'rb')  # open the file in bytes / ro mode

        # Return Exif tags
        tags = exifread.process_file(f, details=False)  # the "False" statement filters out a lot of comment data from
        # device maker
        make = tags['Image Make']
        model = tags['Image Model']
        orig_date = tags['EXIF DateTimeOriginal']

        return make, str(model).partition(' ')[2], str(orig_date)[:10], ifile  # some hoops to get the correct format

    else:
        logfile.write(ifile + " this file is corrupt")


# the routine to print out make , model etc.
def print_results(make, model, date_gen, image_name):
    print("{:20.20} \t {:<20} \t {:10.10} \t {}".format(str(make), str(model), str(date_gen), image_name))


for path in Path('YOUR PATH HERE').rglob('*'):  # the path will be different for a PC
    # uncomment the below if you simply want work specifically with image files
    # if re.search(r'\.jpg$|\.png$|\.bmp$|\.heic$|\.cr2$', str(path), re.IGNORECASE):
    if path.is_file():  # this simply validates that it's a file
        try:
            make, model, orig_date, image_name = get_exif_data(path)
            print_results(make, model, orig_date,
                          os.path.basename(image_name))  # path.baseline strips out file from path

        except:
            logfile.write(str(path) + " may be corrupted or not an image file \n")

logfile.close()  # close the log file
