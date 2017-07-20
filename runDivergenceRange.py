#!/usr/bin/env python 
"""Usage: runDivergenceRange.py --y0=<y0> --nYears=<years> --outDir=<dir>

  --y0 <y0>         First year in the period to measure divergence
  --nYears <years>  Number of years in the period to measure divergence
  --outDir <dir>    Directory where measured divergence results are saved
"""
import pickle as pkl

from docopt import docopt
from helpers import getYears
from divergence import computeDivergenceOverYearRange

def measureDivergence(y0, nYears, saveDir):
    batchSize = 1e6
    maxSentences = 10e7
    yN = y0 + nYears
    allYears = getYears()
    yearRange = allYears[(y0<=allYears) & (allYears<=yN)]

    divergence, sentenceYearCounter, vocabSize = computeDivergenceOverYearRange(yearRange, batchSize, maxSentences)

    fname = saveDir + '/divergenceRange_%d-%d.pkl'%(y0,yN)
    pkl.dump((divergence, sentenceYearCounter, vocabSize), open(fname, 'wb'))

if __name__ == '__main__':
    args = docopt(__doc__)

    y0 = int(args['--y0'])
    nYears = int(args['--nYears'])
    saveDir = args['outDir']
    measureDivergence(y0, nYears, saveDir)
