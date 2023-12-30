from os import listdir, makedirs, path
from sys import argv
from subprocess import Popen, PIPE
from shutil import move

VALID_LEVELS = ["0","1","2","3"]  #todo: eventually add support for "4","5","6","7","8","9" once landsat mosaic is done
EXPECTED_ARGUMENT_LENGTH = 3
LANDSAT_IMAGE_SIZE_PIXELS = "512x512"
LEVEL = None
ORIGINAL_IMAGE = None

level_to_original_image_size = {
    "0": "5120x2560",
    "1": "10240x5120",
    "2": "20480x10240",
    "3": "40960x20480"
}

rows_per_level = {
    "0": 5,
    "1": 10,
    "2": 20,
    "3": 40
}

columns_per_level = {
    "0": 10,
    "1": 20,
    "2": 40,
    "3": 80
}

# check for dependencies
try:
    proc = Popen(["magick.exe", "-version"],stdout=PIPE)
except FileNotFoundError:
    print("imagemagick not found. To use this script, download imagemagick at https://imagemagick.org/script/download.php")
    exit(1)


# ingest argv, error check it. Should give 2 additional args, level value from 0 - 9 and an image to create tiles from
if len(argv) > EXPECTED_ARGUMENT_LENGTH:
    print("too many arguments given")
elif len(argv) < EXPECTED_ARGUMENT_LENGTH:
    print("not enough arguments, choose a level from [0 - 9] and an image to split")
else: 
    if(argv[1] in VALID_LEVELS):
        LEVEL = argv[1]
        ORIGINAL_IMAGE = argv[2]
    else:
        print("invalid level given, choose a level from [0 - 9]")

if(LEVEL == None or ORIGINAL_IMAGE == None):
    exit(1)


print("creating tiles for level: " + LEVEL)
print("creating from image: " + ORIGINAL_IMAGE)


# resize original image
print("\n---Resizing the original image---")
image_output_name = None
try:
    image_output_name = ORIGINAL_IMAGE.replace('.png','').replace('.jpg', '').replace('.tiff', '') + "_" + level_to_original_image_size[LEVEL]+".png"
    resize_cmd = ["magick.exe", 
                    ORIGINAL_IMAGE, 
                    "-resize", level_to_original_image_size[LEVEL], 
                    image_output_name]
    print("executing the following command to imagemagick:\n" + ' '.join(resize_cmd))
    resize_proc = Popen(resize_cmd, stdout=PIPE)
    resize_proc.wait()

except Exception as err:
    print("error encountered in resize:")
    print(err)
    exit(1)


# set up file structure
paths_to_create = []
thisrow = 0
while thisrow < rows_per_level[LEVEL]:
    paths_to_create.append(path.join(".", LEVEL, str(thisrow)))
    thisrow += 1

mode = 0o666
for path_to_create in paths_to_create:
    if not path.exists(path_to_create):
        makedirs(path_to_create, mode)

print(listdir())
print(listdir(LEVEL))

# split up image
print("\n---Splitting up image into tiles")
try:
    split_cmd = ["magick.exe",
                 image_output_name,
                 "+repage",
                 "-crop", LANDSAT_IMAGE_SIZE_PIXELS,
                 LEVEL + "/%05d.png"
    ]
    print("executing the following command to imagemagick:\n" + ' '.join(split_cmd))
    split_proc = Popen(split_cmd, stdout=PIPE)
    split_proc.wait()

except Exception as err:
    print("error encountered in tiling:")
    print(err)
    exit(1)

print(listdir("./" + LEVEL))
# rename and organize images
images = [f for f in listdir(LEVEL) if path.isfile(path.join(".", LEVEL, f))]
print(images)

# the first image (00000) is the top left corner, which is (max row, min column)
# eg for landsat level 0, 00000 -> (4, 0), 00001 -> (4,1)
currentrow = rows_per_level[LEVEL] - 1
currentcolumn = 0
for image in images:
    if currentcolumn == columns_per_level[LEVEL]:
        currentcolumn = 0
        currentrow -= 1

    print("image: " + image)
    
    old_image_path = path.join(".", LEVEL, image)
    new_image_path = path.join(".", LEVEL, str(currentrow), str(currentrow) + "_" + str(currentcolumn) + ".png")
    print("moving image  :  " + old_image_path)
    print("to  :  " + new_image_path)
    
    move(old_image_path, new_image_path)

    currentcolumn += 1

