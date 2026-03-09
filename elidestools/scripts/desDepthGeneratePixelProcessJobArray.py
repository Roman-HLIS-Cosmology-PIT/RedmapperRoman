#!/usr/bin/env python

from __future__ import division, absolute_import, print_function

import argparse
import sys
import os
import glob
import re

parser = argparse.ArgumentParser(description="Generate depth generation scripts in LSF format for SLAC")

parser.add_argument('-p', '--basicPixBase', action='store', type=str, required=True, help='Base name for basic pixel files')
parser.add_argument('-o', '--outBase', action='store', type=str, required=True, help='Output base file name')
parser.add_argument('-f', '--fluxCol', action='store', type=str, required=True, help='Name of flux column')
parser.add_argument('-e', '--errCol', action='store', type=str, required=True, help='Name of flux error column')
parser.add_argument('-t', '--typeName', action='store', type=str, required=True, help='Type of flux to process')
parser.add_argument('-n', '--nSide', action='store', type=int, default=1024, help='Coarse nside for computing depths')
parser.add_argument('-N', '--nSidePixFile', action='store', type=int, default=8, help='Nside of input pixel file')
parser.add_argument('-b', '--bands', action='store', type=str, default=['g,r,i,z,Y'], help='Comma-delimited list of band names')
parser.add_argument('-G', '--noGoldFlags', action='store_true', help='Do not look for gold flags in input files.')
parser.add_argument('-s', '--s2nCut', action='store', type=float, default=5.0, help='Signal to noise cut to perform fit.')
parser.add_argument('-g', '--selectGalaxies', action='store_true', help='Select the galaxies with default algorithm?')
parser.add_argument('-S', '--bdSizeFileType', action='store', type=str, help='Type of file to get bd sizes from')

args = parser.parse_args()

pixFiles = sorted(glob.glob('%s*basic.fits' % (args.basicPixBase)))

outputPath = os.path.abspath(os.getcwd())

jobPath = '%s/jobs' % (outputPath)

if (not os.path.isdir(jobPath)):
    try:
        os.makedirs(jobPath)
    except:
        if (not os.path.isdir(jobPath)):
            print("Could not make job directory!")
            sys.exit(2)

jobFile = '%s/%s.job' % (jobPath, args.outBase)

jf=open(jobFile,"w")
jf.write("#BSUB -R 'linux64 && rhel60 && (!deft) && (!hequ)'\n")
jf.write("#BSUB -J %s[1-%d]\n" % (args.outBase, len(pixFiles)))
jf.write("#BSUB -oo %s/%s_%%J_%%I.log\n" % (jobPath, args.outBase))
jf.write("#BSUB -n 1\n")
jf.write("#BSUB -W 2000\n")
jf.write("pixarr=(")
for pixFile in pixFiles:
    # need to split off _basic.fits
    parts=pixFile.split('_basic.fits')
    jf.write("%s " % (os.path.abspath(parts[0])))
jf.write(")\n\n")

jf.write("\nexport MKL_NUM_THREADS=1\n")
jf.write("export NUMEXPR_NUM_THREADS=1\n")
jf.write("export OMP_NUM_THREADS=1\n")

jf.write("\nunset PYTHONPATH; source /nfs/slac/g/ki/ki19/des/erykoff/miniconda3/etc/profile.d/conda.sh; conda activate vanilla3\n")

line = 'desDepthCatalogPixelProcess.py -p ${pixarr[$LSB_JOBINDEX-1]} -o %s/%s -f %s -e %s -t %s' % (outputPath, args.outBase, args.fluxCol, args.errCol, args.typeName)
if (args.nSide is not None):
    line = '%s -n %d' % (line, args.nSide)
if (args.nSidePixFile is not None):
    line = '%s -N %d' % (line, args.nSidePixFile)
if (args.bands is not None):
    line = '%s -b %s' % (line, args.bands)
if (args.s2nCut is not None):
    line = '%s -s %s' % (line, args.s2nCut)
if (args.noGoldFlags):
    line = '%s -G' % (line)
if (args.selectGalaxies):
    line = '%s -g' % (line)
if (args.bdSizeFileType is not None):
    line = '%s -S %s' % (line, args.bdSizeFileType)

jf.write("%s\n" % (line))

jf.close()

