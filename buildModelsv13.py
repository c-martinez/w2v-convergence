import gensim 
import cPickle as pkl
from collections import defaultdict
from helpers import getYears
from glob2 import glob
from sortedcontainers import SortedDict

from util import checkPath
from randomsentenceloader import RandomSentenceLoader
from randomsentenceloader import buildChunks
from convergence import testModelConvergence
from w2vtransformation import getModelInv
from convergence import generateModelsForPeriod, computeConvergenceOverYearRangeWithBuildModels

allYears = getYears()

y0 = 1990
yN = 1999
years = allYears[(y0<=allYears) & (allYears<=yN)]

# runSeeds = [ 681, 1261, 1543, 2154, 3536, 4111, 5317, 5571, 8543, 9566]
runSeeds = [ 3536, 4111, 5317, 5571, 8543, 9566]
minSentences = 1e5
maxSentences = 1e8
vector_size = 300
nSteps = 25
chunkSize = 1000

for randomSeed in runSeeds:
    print '==== Running for seed: %d ================'%randomSeed
    modelFolder = './run%d_s%d'%(y0,randomSeed)

    generateModelsForPeriod(years, minSentences, maxSentences, nSteps, chunkSize, randomSeed, vector_size, modelFolder)
    convergence, sentenceYearCounter, vocabSize = computeConvergenceOverYearRangeWithBuildModels(modelFolder, vector_size)
    fname = modelFolder + '/convergenceRange_%d.pkl'%y0
    pkl.dump((convergence, sentenceYearCounter, vocabSize), open(fname, 'wb'))
