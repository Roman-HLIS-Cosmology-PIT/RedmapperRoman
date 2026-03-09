#!/usr/bin/env python

from __future__ import division, absolute_import, print_function

import argparse
import sys
import glob

import elidestools.des_depth as des_depth

parser = argparse.ArgumentParser(description='Code to consolidate a bunch of depth map pixel files that were run in parallel.')

parser.add_argument('-g', '--globStr', action='store', type=str, required=True, help='Glob string for finding depth map pixel files')
parser.add_argument('-o', '--outFile', action='store', type=str, required=True, help='Output file')
parser.add_argument('-n', '--nSide', action='store', type=int, required=True, help='Nside for coarse pixelization')
parser.add_argument('-N', '--nest', action='store_true', help='Are coarse pixels nest format?')

args = parser.parse_args()

pixFiles = sorted(glob.glob('%s' % (args.globStr)))

print("Found %d files." % (len(pixFiles)))

des_depth.pixelConsolidate(pixFiles, args.outFile, args.nSide, nest=args.nest)
