#!/usr/bin/env python

from __future__ import division, absolute_import, print_function

import argparse
import sys
import elidestools.des_depth as des_depth

parser = argparse.ArgumentParser(description='Code to compute the relationship between exposure time and mag limit from a coarse depth map')

parser.add_argument('-d', '--depthFile', action='store', type=str, required=True, help='Coarse depth file')
parser.add_argument('-b', '--bands', action='store', type=str, required=True, help='Comma-delimited list of bands to compute exp limit relationship')
parser.add_argument('-n', '--npixMax', action='store', type=str, required=True, help='Comma-delimited list of Max number of neighbor-pixels used to obtain the model fit to use in computing relationship')
parser.add_argument('-m', '--minNGal', action='store', type=int, default=50, help='Minimum number of galaxies in a coarse pixel for the model fit to use in computing relationship')
parser.add_argument('-p', '--pivot', action='store', type=float, default=23.0, help='Pivot for exptime/maglim relationship')

args = parser.parse_args()

bandList = args.bands.split(',')
npixMax = [int(x) for x in args.npixMax.split(',')]

if (len(bandList) != len(npixMax)):
    print("Need same number of bands and npixMax")
    sys.exit(0)

des_depth.expLimit(args.depthFile, bandList, npixMax, minNGal=args.minNGal, pivot=args.pivot)
