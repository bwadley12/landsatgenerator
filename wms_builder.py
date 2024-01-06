from os import listdir, makedirs, path
from sys import argv
import requests
import shutil
from concurrent.futures import ThreadPoolExecutor

VALID_LEVELS = ["0","1","2","3","4","5","6","7","8","9"]
VALID_LAYER_NAMES = ["bluemarble","landsat","night"]
EXPECTED_ARGUMENT_LENGTH = 3
LEVEL = None

rows_per_level = {
    "0": 5,
    "1": 10,
    "2": 20,
    "3": 40,
    "4": 80,
    "5": 160,
    "6": 320,
    "7": 640,
    "8": 1280,
    "9": 2560
}

columns_per_level = {
    "0": 10,
    "1": 20,
    "2": 40,
    "3": 80,
    "4": 160,
    "5": 320,
    "6": 640,
    "7": 1280,
    "8": 2560,
    "9": 5120
}

degrees_per_image_per_level = {
    "0": 36,
    "1": 18,
    "2": 9,
    "3": 4.5,
    "4": 2.25,
    "5": 1.125,
    "6": 0.5625,
    "7": 0.28125,
    "8": 0.140625,
    "9": 0.0703125
}

layername_to_wms_capabilities = {
    "bluemarble":"BlueMarble-200405" ,
    "landsat":"BlueMarble-200405,esat",
    "night":"earthatnight"
}

URL = 'https://worldwind25.arc.nasa.gov/wms'
HEADERS = {'content-type': 'image/png'}

# bbox = lower left latitude, lower left longitude, upper right latitude, upper right longitude
parameters = {
    "service": "WMS",
    "request":"GetMap",
    "version":"1.3.0",
    "transparent":"TRUE",
    "layers":"BlueMarble-200405,esat",
    "styles":"",
    "format":"image/png",
    "width":"512",
    "height":"512",
    "crs":"EPSG:4326",
    "bbox":"54,-180,90,-144",
}


def getImage(URL, parameters, HEADERS, image_name):
    response = requests.get(URL, 
                                params=parameters,
                                headers=HEADERS, 
                                stream=True)

    if response.status_code == 200:
        with open(image_name, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


# ingest argv, error check it. Should give 1 additional args, level value from 0 - 9
if len(argv) > EXPECTED_ARGUMENT_LENGTH:
    print("too many arguments given")
elif len(argv) < EXPECTED_ARGUMENT_LENGTH:
    print("not enough arguments, choose a level from [0 - 9] and a wms layer of bluemarble, landsat, or night")
else: 
    if(argv[1] in VALID_LEVELS and argv[2] in VALID_LAYER_NAMES):
        LEVEL = argv[1]
        LAYER_NAME = layername_to_wms_capabilities[argv[2]]
        parameters["layers"] = LAYER_NAME

    else:
        print("invalid level given, choose a level from [0 - 9]")

if(LEVEL == None):
    exit(1)


# set up file structure
print("building tiles for level: " + LEVEL + " using wms layer " + LAYER_NAME)
paths_to_create = []
thisrow = 0
while thisrow < rows_per_level[LEVEL]:
    paths_to_create.append(path.join(".", LAYER_NAME, LEVEL, str(thisrow)))
    thisrow += 1

mode = 0o666
for path_to_create in paths_to_create:
    if not path.exists(path_to_create):
        makedirs(path_to_create, mode)


thisrow = 0

with ThreadPoolExecutor(max_workers = 100) as e:
    while thisrow < rows_per_level[LEVEL]:
        thiscolumn = 0
        while thiscolumn < columns_per_level[LEVEL]:
            lower_lat = -90 + thisrow * degrees_per_image_per_level[LEVEL]
            lower_long = -180 + thiscolumn * degrees_per_image_per_level[LEVEL]
            upper_lat = lower_lat + degrees_per_image_per_level[LEVEL]
            upper_long = lower_long + degrees_per_image_per_level[LEVEL]
            bbox = str(lower_lat) + "\," + str(lower_long) + "\," + str(upper_lat) + "\," + str(upper_long)
            parameters["bbox"] = bbox
            image_name = path.join(".", LAYER_NAME, LEVEL, str(thisrow), str(thisrow) + "_" + str(thiscolumn) + ".png")

            e.submit(getImage, URL, dict(parameters), HEADERS, image_name)
                
            thiscolumn += 1
        thisrow += 1



