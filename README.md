Built out of a lack of existing help in the internet, this project is aimed at helping others generate and use imagery tiles with NASA's WorldWind (https://worldwind.arc.nasa.gov/java/) and Web WorldWind (https://worldwind.arc.nasa.gov/web/) LandsatRestLayer.
This interface is useful when you need a project to run offline, in which case WMS nad WMTS is unavailable. This is not intended to provide street-level detail, but will provide better detail than a single image wrapped around the globe.

Dependencies: 
- Python 3 (https://www.python.org/downloads/)
- ImageMagick (https://imagemagick.org/script/download.php)

Background Info:
Two REST tiling interfaces provided by WorldWind are Blue Marble and Landsat. Landsat is a series of satellite generations that provided multiple bands of increasingly high-resolution and purpose-oriented scans.
More information about Landsat and imagery can be found from NASA and USGS EarthExplorer (https://landsat.gsfc.nasa.gov/ and https://earthexplorer.usgs.gov/)
To download landsat data from USGS, you can freely register an account.

However, I find this data is relatively difficult to use as someone whose expertise is not in GIS. I want some quick and dirty image tiles. Additionally, there is not a lot of readily-available information online explaining how
to generate and use tiles that conform to WorldWind's REST interfaces. So here's a breakdown:

Landsat is divided into layers of increasing resolution from 0 - 15 (technically there's nothing preventing this from continuing, aside from satellite capabilities and physical storage). 
WorldWind takes care of the magic to determine what tile is needed at a given time, but it does expect the backend tile server to provide tiles in this format:
tiles / layer / row / row_column.png
All landsat tiles are assumed to be, and will be scaled to, 512x512 pixels

At layer 0, the globe is split up into a 5 x 10 grid centered at the Greenwich Meridian, with (0, 0) in Pacific/Antarctica region and (4, 0) covering Alaska. At this level, each square tile covers 36 x 36 degrees
This is shown visually here: https://www.microimages.com/documentation/TechGuides/78Worldwind.pdf
From here, each subsequent layer doubles in each direction with the origin of the grid staying the same, i.e.

| Layer | Grid Size (R x C) | Tile Size (Degrees) | Globe Resolution (Pixels) |
| ----- | ----------------- | ------------------- | ------------------------- |
|   0   |       5 x 10      |        36 x 36      |         5120 x 2560       |
|   1   |      10 x 20      |        18 x 18      |        10240 x 5120       |
|   2   |      20 x 40      |         9 x 9       |        20480 x 10240      |
|   3   |      40 x 80      |       4.5 x 4.5     |        40960 x 20480      |
|   4   |      80 x 160     |      2.25 x 2.25    |        81920 x 40960      |

and so on

Creating a mosaic from USGS landsat tiles will come in the future, but for now my own purposes I've found success using maps from these sources:
NASA Blue Marble Gallery - Fine resolution images at 20k x 10k geotifs, wide variety of surface scans and dates - https://visibleearth.nasa.gov/collection/1484/blue-marble 
Huge Earth Maps - Highest resolution images I've been able to find, with 40k x 20k and 80k x 40k pixel geotifs - https://maps.drsys.eu/ 
Note: the higher resolution, the more accurate your globe will look up close due to less interpolation needed.
| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |

Usage:
Clone this script and place a source image in the same directory.
tiles /
  split_image.py
  original_image.tif

run the script in this format: python original_image.py <layer> <original_image_name>
e.g.: python original_image.py 0 original_image.tif

This will:
1. create a copy of the original image at the correct resolution for the level selected, named original_image_<scaled_dimensions_in_pixels>.png
2. create the file structure relative current location that WorldWind expects
3. split the copied image into the tiles according to the level selected
4. organize and name the tiles according to the file structure
   
  For this example of requesting layer 0 tiles, this would be the result:
  tiles /
     original_image.tif
     original_image_5120x2560.png
     0 /
       0 /
         0_1.png
         0_2.png
         0_3.png
         ...
       1 /
         1_1.png
         1_2.png
         1_3.png
         ...
       ...
   
