#!/usr/bin/env python
"""Measure the divergence of w2v models generated on a given time range. W2V
models are trained in incremental batches of 1e6 sentences.

Usage: runDivergenceRange.py --y0=<y0> --nYears=<years> --outDir=<dir>

Options:
  --y0 <y0>         First year in the period to measure divergence
  --nYears <years>  Number of years in the period to measure divergence
  --outDir <dir>    Directory where measured divergence results are saved
"""
import pickle as pkl

from docopt import docopt
from helpers import getYears
from util import checkPath
from divergence import computeDivergenceOverYearRange


def measureDivergence(y0, nYears, saveDir):
    """
    Call computeDivergenceOverYearRange for sentences in the given year range
    and save divergence results to the given directory.
    """
    batchSize = 1e6
    maxSentences = 10e7
    yN = y0 + nYears
    allYears = getYears()
    yearRange = allYears[(y0 <= allYears) & (allYears <= yN)]

    divergence, sentenceYearCounter, vocabSize = computeDivergenceOverYearRange(
        yearRange, batchSize, maxSentences)

    checkPath(saveDir)
    fname = saveDir + 'divergenceRange_%d-%d.pkl' % (y0, yN)
    pkl.dump((divergence, sentenceYearCounter, vocabSize), open(fname, 'wb'))


if __name__ == '__main__':
    args = docopt(__doc__)

    y0 = int(args['--y0'])
    nYears = int(args['--nYears'])
    saveDir = args['--outDir']
    measureDivergence(y0, nYears, saveDir)
