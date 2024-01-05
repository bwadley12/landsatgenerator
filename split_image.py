from os import listdir, makedirs, path
from sys import argv
from subprocess import Popen, PIPE
from shutil import move


VALID_LEVELS = ["0","1","2","3","4"]  #todo: eventually add support for "4","5","6","7","8","9" once landsat mosaic is done
EXPECTED_ARGUMENT_LENGTH = 3
LANDSAT_IMAGE_SIZE_PIXELS = "512x512"
LEVEL = None
ORIGINAL_IMAGE = None

level_to_original_image_size = {
    "0": "5120x512",
    "1": "10240x512",
    "2": "20480x512",
    "3": "40960x512",
    "4": "81920x512"
}

rows_per_level = {
    "0": 5,
    "1": 10,
    "2": 20,
    "3": 40,
    "4": 80
}

columns_per_level = {
    "0": 10,
    "1": 20,
    "2": 40,
    "3": 80,
    "4": 160
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


# split up into rows to help processing time
mode = 0o666
if not path.exists("tmp"):
    makedirs("tmp", mode)
try:
    row_split_command = ["magick.exe",
                        "convert",
                        ORIGINAL_IMAGE,
                        "+repage",
                        "-crop",  "1x" + str(rows_per_level[LEVEL]) + "@",
                        LEVEL + "/%03d.png"
    ]
    print("executing the following command to imagemagick:\n" + ' '.join(row_split_command))
    row_split_proc = Popen(row_split_command, stdout=PIPE)
    row_split_proc.wait()

except Exception as err:
    print("error encountered in splitting into rows:")
    print(err)
    exit(1)

row_images = [f for f in listdir(LEVEL) if path.isfile(path.join(".", LEVEL, f))]
print(row_images)


row_increment = 0 
while row_increment < len(row_images):
    corrected_row_num = len(row_images) - 1 - row_increment

    this_row_image_to_split = row_images[row_increment]
    print("splitting up image:  " + this_row_image_to_split)

    try:
        col_split_command = ["magick.exe",
                            "convert",
                            LEVEL + "/" + this_row_image_to_split,
                            "+repage",
                            "-crop",   str(columns_per_level[LEVEL]) + "x1" + "@",
                            LEVEL + "/" + str(corrected_row_num) + "/%04d.png"
        ]
        print("executing the following command to imagemagick:\n" + ' '.join(row_split_command))
        col_split_proc = Popen(col_split_command, stdout=PIPE)
        col_split_proc.wait()
    except Exception as err:
        print("error encountered in splitting rows into tiles:")
        print(err)
        exit(1)

    row_increment += 1


# resize and rename tiles
row_increment = 0 
while row_increment < len(row_images):
    images_to_resize_and_rename = [f for f in listdir(LEVEL + "/" + str(row_increment)) if path.isfile(path.join(".", LEVEL, str(row_increment), f))]
    print("images in row number " + str(row_increment) + ":   ")

    column_increment = 0
    while column_increment < len(images_to_resize_and_rename):
        image = images_to_resize_and_rename[column_increment]
        print(image)
        try:
            resize_cmd = ["magick.exe", 
                          "mogrify", 
                          "-resize", LANDSAT_IMAGE_SIZE_PIXELS,
                          LEVEL + "/" + str(row_increment) + "/" + image
            ]
            
            print("executing the following command to imagemagick:\n" + ' '.join(resize_cmd))
            resize_proc = Popen(resize_cmd, stdout=PIPE)
            resize_proc.wait()

        except Exception as err:
            print("error encountered in resize:")
            print(err)
            exit(1)

        # rename and organize images
        # the first image (00000) is the top left corner, which is (max row, min column)
        # eg for landsat level 0, 00000 -> (4, 0), 00001 -> (4,1)
        old_image_path = path.join(".", LEVEL, str(row_increment), image)
        new_image_path = path.join(".", LEVEL, str(row_increment), str(row_increment) + "_" + str(column_increment) + ".png")
        move(old_image_path, new_image_path)

        column_increment += 1

    row_increment += 1
