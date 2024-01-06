from os import listdir, makedirs, path
from sys import argv
import requests
import shutil

VALID_LEVELS = ["0","1","2","3","4","5"] 
EXPECTED_ARGUMENT_LENGTH = 2
LEVEL = None

rows_per_level = {
    "0": 5,
    "1": 10,
    "2": 20,
    "3": 40,
    "4": 80,
    "5": 160
}

columns_per_level = {
    "0": 10,
    "1": 20,
    "2": 40,
    "3": 80,
    "4": 160,
    "5": 320
}

degrees_per_image_per_level = {
    "0": 36,
    "1": 18,
    "2": 9,
    "3": 4.5,
    "4": 2.25,
    "5": 1.125
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

# ingest argv, error check it. Should give 1 additional args, level value from 0 - 9
if len(argv) > EXPECTED_ARGUMENT_LENGTH:
    print("too many arguments given")
elif len(argv) < EXPECTED_ARGUMENT_LENGTH:
    print("not enough arguments, choose a level from [0 - 9]")
else: 
    if(argv[1] in VALID_LEVELS):
        LEVEL = argv[1]
    else:
        print("invalid level given, choose a level from [0 - 9]")

if(LEVEL == None):
    exit(1)


# set up file structure
print("building tiles for level: " + LEVEL)
paths_to_create = []
thisrow = 0
while thisrow < rows_per_level[LEVEL]:
    paths_to_create.append(path.join(".", LEVEL, str(thisrow)))
    thisrow += 1

mode = 0o666
for path_to_create in paths_to_create:
    if not path.exists(path_to_create):
        makedirs(path_to_create, mode)


thisrow = 0
while thisrow < rows_per_level[LEVEL]:
    thiscolumn = 0
    while thiscolumn < columns_per_level[LEVEL]:
        lower_lat = -90 + thisrow * degrees_per_image_per_level[LEVEL]
        lower_long = -180 + thiscolumn * degrees_per_image_per_level[LEVEL]
        upper_lat = lower_lat + degrees_per_image_per_level[LEVEL]
        upper_long = lower_long + degrees_per_image_per_level[LEVEL]
        bbox = str(lower_lat) + "\," + str(lower_long) + "\," + str(upper_lat) + "\," + str(upper_long)
        parameters["bbox"] = bbox
        image_name = path.join(".", LEVEL, str(thisrow), str(thisrow) + "_" + str(thiscolumn) + ".png")

        response = requests.get(URL, 
                        params=parameters,
                        headers=HEADERS, 
                        stream=True)

        if response.status_code == 200:
            with open(image_name, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

        thiscolumn += 1
    thisrow += 1



