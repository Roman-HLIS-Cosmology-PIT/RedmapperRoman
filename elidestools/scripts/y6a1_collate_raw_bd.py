#!/usr/bin/env python

import argparse
import os
import sys
import glob

import elidestools


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Raw download converter')

    parser.add_argument('-o', '--outbase', action='store', type=str, required=True, help='output base name')
    parser.add_argument('-n', '--nside', action='store', type=int, default=8, help='nside')
    parser.add_argument('-g', '--globstr', action='store', type=str, required=True, help='glob string for mof files')
    parser.add_argument('-b', '--bdname', action='store', type=str, required=True, help='Bd name (usually mof or sof)')

    args=parser.parse_args()

    bdFiles = glob.glob(args.globstr)
    bdFiles.sort()

    rc = elidestools.y6a1_tools.Y6A1RawCollator(args.outbase, nside=args.nside)

    rc.runBd(bdFiles, args.bdname)
