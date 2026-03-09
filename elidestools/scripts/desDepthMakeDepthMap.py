#!/bin/env python

from __future__ import division, absolute_import, print_function

import argparse
import os
import sys

import elidestools.des_depth as des_depth

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Code to make a DES depth map from systematics')

    parser.add_argument('-d', '--depthFile', action='store', type=str, required=True, help='Coarse depth file')
    parser.add_argument('-p', '--sysPath', action='store', type=str, required=True, help='Systematics path')
    parser.add_argument('-t', '--sysTemplate', action='store', type=str, required=True, help='Systematics template, with %s for band %s for type')
    parser.add_argument('-o', '--outBase', action='store', type=str, required=True, help='Output file base')
    parser.add_argument('-M', '--minGalFit', action='store', type=int, default=50, help='Minimum number of galaxies in pixel to use for training')
    parser.add_argument('-m', '--maglimType', action='store', type=str, default='maglim', help='Maglimit type string')
    parser.add_argument('-s', '--sysTypes', action='store', type=str, default='FWHM.WMEAN,AIRMASS.WMEAN,EXPTIME.SUM,SKYBRITE.WMEAN', help='comma-separated list of systematics to use')
    parser.add_argument('-b', '--bands', action='store', type=str, default='g,r,i,z,Y', help='comma-separated list of bands')
    parser.add_argument('-z', '--zpTemplate', action='store', type=str, required=False, default=None, help='ZP correction template')
    parser.add_argument('-n', '--npixFit', action='store', type=str, default='1,1,1,1,9', help='comma-separated list of npixFit in coarse map')
    parser.add_argument('-e', '--ebvFile', action='store', type=str, required=False, default=None, help='EBV Map')
    parser.add_argument('-A', '--aLambda', action='store', type=str, required=False, default='3.186,2.140,1.569,1.196,1.048', help='a_lambda (per band)')

    args = parser.parse_args()

    sysTypes = args.sysTypes.split(',')
    print(sysTypes)
    bands = args.bands.split(',')
    print(bands)
    npixFitStr = args.npixFit.split(',')
    npixFit = []
    for n in npixFitStr:
        npixFit.append(int(n))

    if (len(bands) != len(npixFit)):
        raise ValueError("Number of bands must equal number of npixFit")

    aLambdaStr = args.aLambda.split(',')
    aLambda = []
    for n in aLambdaStr:
        aLambda.append(float(n))

    if len(bands) != len(aLambda):
        raise ValueError("Number of bands must equal number of aLambda")

    mapMaker = des_depth.MakeMap(args.depthFile,
                                 args.sysPath,
                                 args.sysTemplate,
                                 args.outBase,
                                 minGalFit=args.minGalFit,
                                 maglimType=args.maglimType,
                                 sysTypes=sysTypes,
                                 bands=bands,
                                 npixFit=npixFit,
                                 zpTemplate=args.zpTemplate,
                                 ebvFile=args.ebvFile,
                                 aLambda=aLambda)
    mapMaker.run()

