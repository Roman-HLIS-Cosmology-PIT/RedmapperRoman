#!/usr/bin/env python

from __future__ import division, absolute_import, print_function

import argparse
import sys
import elidestools.des_depth as des_depth


parser = argparse.ArgumentParser(description='Code to compute the coarse depth on a single pixel.')

parser.add_argument('-p', '--pixFileBase', action='store', type=str, required=True, help='Base name of pixel file (excluding _basic, etc)')
parser.add_argument('-o', '--outBase', action='store', type=str, required=True, help='Output base file name')
parser.add_argument('-f', '--fluxCol', action='store', type=str, required=True, help='Name of flux column')
parser.add_argument('-e', '--errCol', action='store', type=str, required=True, help='Name of flux error column')
parser.add_argument('-t', '--typeName', action='store', type=str, required=True, help='Type of flux to process')
parser.add_argument('-n', '--nSide', action='store', type=int, default=1024, help='Coarse nside for computing depths')
parser.add_argument('-N', '--nSidePixFile', action='store', type=int, default=8, help='Nside of input pixel file')
parser.add_argument('-b', '--bands', action='store', type=str, default='g,r,i,z,Y', help='Comma-delimited list of band names')
parser.add_argument('-G', '--noGoldFlags', action='store_true', help='Do not look for gold flags in input files.')
parser.add_argument('-s', '--s2nCut', action='store', type=float, default=5.0, help='Signal to noise cut to perform fit.')
parser.add_argument('-g', '--selectGalaxies', action='store_true', help='Select the galaxies with default algorithm (otherwise use ext_mash)')
parser.add_argument('-S', '--bdSizeFileType', action='store', type=str, help='Type of file to get bd sizes from')

args = parser.parse_args()

bandList = args.bands.split(',')

des_depth.catalogPixelProcess(args.pixFileBase,
                              args.outBase,
                              args.typeName,
                              args.fluxCol,
                              args.errCol,
                              args.nSide,
                              nSidePixFile=args.nSidePixFile,
                              bandList=bandList,
                              noGoldFlags=args.noGoldFlags,
                              s2nCut=args.s2nCut,
                              selectGalaxies=args.selectGalaxies,
                              bdSizeFileType=args.bdSizeFileType)
