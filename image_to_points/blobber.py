#!/usr/bin/env python

'''blobber: Takes SVG files output from potrace and gets the biggest shape'''

from xml.dom.minidom import parse
import argparse
import sys
from svg.path import parse_path, Path


def get_shapes(path):
    '''Takes an SVG path and returns lists of points'''
    shapes = [Path()]
    for line in path:
        if len(shapes[-1]) > 0:
            if shapes[-1][-1].end != line.start:
                shapes.append(Path())
        shapes[-1].append(line)
    for shape in shapes:
        try:
            shape.closed = True
        except ValueError:
            pass
    return shapes


def get_paths(filename):
    '''Takes an SVG filename and returns a list of the paths found in it'''
    dom = parse(filename)
    paths = [p.getAttribute('d')
             for p in dom.getElementsByTagName('path')]
    return list(map(parse_path, paths))


def get_biggest_subpath(paths):
    '''Finds the subpath with most points out of a list of paths'''
    subpaths = []
    for path in paths:
        subpaths.extend(get_shapes(path))
    return sorted(subpaths, key=len)[-1]


def output_points(path, output_file):
    '''Given a path, writes the points in it to a given output_file'''
    for line in path:
        output_file.write(''+str(line.start.real)+'\t'+str(line.start.imag)+'\n')


def main():
    '''Parses arguments and processes files'''
    parser = argparse.ArgumentParser(
        description='Takes and SVG file and outputs the largest path in it '
        'as a list of x, y values'
    )
    parser.add_argument('input_file', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output_file', default=sys.stdout,
                        type=argparse.FileType('w'))
    args = parser.parse_args()

    paths = get_paths(args.input_file)
    largest_path = get_biggest_subpath(paths)
    output_points(largest_path, args.output_file)

if __name__ == '__main__':
    main()
