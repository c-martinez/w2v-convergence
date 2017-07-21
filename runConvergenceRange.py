#!/usr/bin/env python
"""Measure the convergence of w2v models generated on a given time range. W2V
models are trained in incremental batches of 1e6 sentences.

Usage: runConvergenceRange.py --y0=<y0> --nYears=<years> --outDir=<dir>

Options:
  --y0 <y0>         First year in the period to measure convergence
  --nYears <years>  Number of years in the period to measure convergence
  --outDir <dir>    Directory where measured convergence results are saved
"""
import pickle as pkl

from docopt import docopt
from helpers import getYears
from util import checkPath
from convergence import computeConvergenceOverYearRange


def measureConvergence(y0, nYears, saveDir):
    """
    Call computeConvergenceOverYearRange for sentences in the given year range
    and save convergence results to the given directory.
    """
    batchSize = 1e6
    maxSentences = 10e7
    yN = y0 + nYears
    allYears = getYears()
    yearRange = allYears[(y0 <= allYears) & (allYears <= yN)]

    convergence, sentenceYearCounter, vocabSize = computeConvergenceOverYearRange(
        yearRange, batchSize, maxSentences)

    checkPath(saveDir)
    fname = saveDir + 'convergenceRange_%d-%d.pkl' % (y0, yN)
    pkl.dump((convergence, sentenceYearCounter, vocabSize), open(fname, 'wb'))


if __name__ == '__main__':
    args = docopt(__doc__)

    y0 = int(args['--y0'])
    nYears = int(args['--nYears'])
    saveDir = args['--outDir']
    measureConvergence(y0, nYears, saveDir)
