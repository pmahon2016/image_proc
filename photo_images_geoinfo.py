"""This program is designed to search through a directory or drive to find image files (JPG, BMP, HEIC, etc.) and
extract the exif or metadata from the image to parse through for the camera/smartphone maker, model,
timestamp and location data """

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
import io
import pyheif
import exifread
import re
import requests
import os

f = open("api_key.txt", 'r')

##### enter your api-key here #######
api_key = f.read()  # you can paste it in or read from a file

logfile = open('imagelog.txt', 'a')  # will create a file with log


def get_location(latlng):
    r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + latlng + "&key=" + api_key)
    p = re.compile(r'formatted_address" : (.+)')  # to learn about about regex testing go to regex101.com

    """ IF YOU WANT TO USE HERE DEVELOPER NETWORK FOR LOCATION USE THE FOLLOWING CODE AND SEARCH 
        AFTER YOU HAVE YOUR API KEY...USE THE BELOW CODE

    r = requests.get(
        'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json?prox=LATITUDEHERE%2CLONGITUDEHERE%2C250&mode='
        'retrieveAddresses&maxresults=1&gen=9&apiKey=YOUR APIKEY HERE')
        
        SEARCH HERE: 
        p = re.compile(r'Address":{"Label":"[\w  , ]+')
        print(re.search(p, r.text).group(0)[19:])
        """

    return re.search(p, r.text).group(1)




# Finds the GPS tags and populates a dictionary (geotagging) with all the relevant data.
# the lat and lon (coordinates) below will pull the required values from the dictionary to covert with the
# latlng_conversion function
def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]
    return geotagging


""" More information on the conversion below can be found at https://gist.github.com/erans/983821
    YOu can also read about it at: https://exiftool.org/TagNames/GPS.html
"""


def latlng_conversion(latlng, ref):
    degrees = latlng[0][0] / latlng[0][1]
    minutes = latlng[1][0] / latlng[1][1] / 60.0
    seconds = latlng[2][0] / latlng[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)


def get_coordinates(geotags):
    lat = latlng_conversion(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])

    lon = latlng_conversion(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

    return (lat, lon)


def get_exif_data(ifile):
    if re.search(r'jpeg$|bmp$|png$|jpg$', str(ifile), re.IGNORECASE):
        image = Image.open(ifile)
        exifdata = image.getexif()
        geotags = get_geotagging(exifdata)
        if "{1:" in str(exifdata[34853]):
            lat_long = get_coordinates(geotags)
            geo_loc = get_location(str(lat_long)[1:-1])

        else:
            geo_loc = "No location Data"

        return exifdata.get(271), exifdata.get(272), exifdata.get(36867), geo_loc, os.path.basename(ifile)


    elif re.search(r'heic$', str(ifile), re.IGNORECASE):
        # this part of the decision tree processes HEIC files

        heif_file = pyheif.read_heif(str(ifile))

        for metadata in heif_file.metadata:

            if metadata['type'] == 'Exif':
                fstream = io.BytesIO(metadata['data'][6:])

        tags = exifread.process_file(fstream, details=False)

        return str(tags.get("Image Make")), str(tags.get("Image Model")), str(
            tags.get('EXIF DateTimeOriginal')), "N/A", os.path.basename(ifile)  # strips path from file

    elif re.search(r'CR2$|NEF$', str(ifile), re.IGNORECASE):
        # this part of the decision tree processes raw files (Cannon and Nikon)
        f = open(ifile, 'rb')

        # Return Exif tags
        tags = exifread.process_file(f, details=False)
        make = tags['Image Make']
        model = tags['Image Model']
        orig_date = tags['EXIF DateTimeOriginal']

        return make, str(model).partition(' ')[2], str(orig_date)[:10], "N/A", os.path.basename(ifile)

    else:
        logfile.write(str(path) + " doesn't seem to be an image file \n")


def print_results(make, model, date_gen, geoloc, image_name):
    print("{:20.20} \t {:<20} \t {:10.10} \t {:<60} \t {}".format(str(make), str(model), str(date_gen), str(geoloc),
                                                                  image_name))


print("{:20.20} \t {:<20} \t {:10.10} \t {:<60} \t {}".format("Device Maker", "Model", "Date", "Location Data",
                                                              "File Name"))

for path in Path('YOUR PATH HERE').rglob('*'):  # the rglob does recursive searched (subdirectories)

    try:
        make, model, orig_date, geoloc, image_name = get_exif_data(path)  # populates variables
        print_results(make, model, orig_date, geoloc, image_name)

    except:
        logfile.write(str(path) + "  does not appear to have any geo data or is not an image file \n")

logfile.close()
