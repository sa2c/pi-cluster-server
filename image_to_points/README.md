# Turn an image into a list of points

Usage:

./blobber.sh [image_name].png

Does the following:

* Converts the image to BMP format with `convert`
* Uses `potrace` to create an SVG version of it
* Finds the subpath containing the most points
* Outputs the points to a file

## Requirements

* ImageMagick
* potrace
* Python 3.6

