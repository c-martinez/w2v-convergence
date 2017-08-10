import os
import tempfile
import gensim
import numpy as np
import cPickle as pkl

from glob2 import glob
from sortedcontainers import SortedDict

from util import checkPath
from sentenceloader import SentenceLoader
from randomsentenceloader import buildChunks, RandomSentenceLoader
from w2vtransformation import calculateTransform, getModelInv


import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

def computeConvergenceOverYearRange(yearRange, batchSize, maxSentences):
    """Compute the convergence of w2v models generated over a given range of
    years. W2v models are generated for every batch of data produced by
    a SentenceLoader (using the given batchSize). Every model is compared
    with the previous one and the convergence between these models is
    calculated. This process stops once all years in the given range have been
    processed or once the maximum number of sentences (maxSentences) has been
    reached."""
    # Initialize model
    vocabSizeMB = 1000 * 1024 * 1024
    model = gensim.models.Word2Vec(max_vocab_size=vocabSizeMB, size=300)

    # Initialize sentence loader
    loader = SentenceLoader(yearRange, batchSize=batchSize)
    batch = loader.nextBatch()
    y0 = yearRange[0]

    # Initialize returned objects
    convergence = SortedDict()
    sentenceYearCounter = SortedDict()
    vocabSize = SortedDict()

    # Initialize loop variables
    doUpdate = False
    cumSentences = 0
    oldModel = None
    oldModelinv = None

    print 'Building models (%d):' % y0
    while cumSentences < maxSentences and len(batch) > 0:
        cumSentences += len(batch)
        cumSentencesStr = ('%d' % cumSentences).zfill(12)
        currYear = loader.getCurrentYear()
        modelName = '%d (%s)' % (currYear, cumSentencesStr)
        print modelName + ',',

        model.build_vocab(batch, update=doUpdate)
        # model.train(batch, model.corpus_count, epochs=model.iter)
        model.train(batch)
        modelinv = getModelInv(model)

        vocabSize[cumSentences] = len(model.wv.vocab)

        # Keep the latest sentence count for given year
        sentenceYearCounter[currYear] = cumSentences

        if oldModel is not None:
            d = testModelConvergence(oldModel, oldModelinv, model, modelinv)
            convergence[cumSentences] = d

        # Prepare for next iteration
        doUpdate = True
        batch = loader.nextBatch()
        oldModel = _makeCopy(model)
        oldModelinv = modelinv

    return convergence, sentenceYearCounter, vocabSize


def testModelConvergence(A, Ainv, B, Binv):
    """Given two models (A and B) and their inverse matrices, calculate the
    convergence between the two models (as a single value)."""
    TTinv = _calculateSymetricTransform(A, Ainv, B, Binv)
    Si_ip = np.trace(TTinv) / 300 # A.vector_size
    return Si_ip

def generateModelsForPeriod(years, minSentences, maxSentences, nSteps, chunkSize, randomSeed, modelFolder):
    checkPath(modelFolder)
    for year in years:
        buildChunks(year, chunkSize)

    batchSizes = np.logspace(np.log10(minSentences), np.log10(maxSentences), num=nSteps, dtype=int)
    loader = RandomSentenceLoader(years, chunkSize=chunkSize, seed=randomSeed)

    pkl.dump(batchSizes, open(modelFolder + '/nSentences.pkl', 'w'))

    for batchSize in batchSizes:
        batch = loader.nextBatch(batchSize=batchSize)
        cumSentencesStr = ('%d'%batchSize).zfill(12)
        modelKey = '%d_'%years[0] + cumSentencesStr

        modelName = modelFolder + '/%s.w2v'%(modelKey)
        vocabName = modelName.replace('.w2v','.vocab.w2v')
        print 'Building model: ',modelName

        vocabSizeMB = 1000 * 1024 * 1024
        model = gensim.models.Word2Vec(max_vocab_size=vocabSizeMB)
        model.build_vocab(batch)
        model.train(batch)

        print '...saving'
        model.wv.save_word2vec_format(modelName, fvocab=vocabName, binary=True)

        loader.reset()


def computeConvergenceOverYearRangeWithBuildModels(modelFolder):
    files = sorted(glob(modelFolder + '/*[!vocab].w2v'))

    convergence = SortedDict()
    sentenceYearCounter = SortedDict()
    vocabSize = SortedDict()

    oldModel, oldModelInv = None, None
    for f in files:
        newModel = gensim.models.KeyedVectors.load_word2vec_format(f, binary=True)
        newModel.init_sims(replace=False)
        newModelInv = getModelInv(newModel)

        cumSentences = int(f.replace(modelFolder, '').replace('.w2v', '').split('_')[1])
        if oldModel is not None:
            d = testModelConvergence(oldModel, oldModelInv, newModel, newModelInv)
            convergence[cumSentences] = d

        vocabSize[cumSentences] = len(newModel.vocab)

        oldModel = newModel
        oldModelInv = newModelInv

    return convergence, sentenceYearCounter, vocabSize

def measureDiagonalConvergence(A, Ainv, B, Binv):
    """Given two models (A and B) and their inverse matrices, calculate the
    convergence between the two models, per dimension (as a vector of the same
    size as the dimensions of the models)."""
    TTinv = _calculateSymetricTransform(A, Ainv, B, Binv)
    return TTinv.diagonal()


def _calculateSymetricTransform(A, Ainv, B, Binv):
    """Given two models (A and B) calculate the symetric version of the
    transformation matrix."""
    Tab = calculateTransform(A, Ainv, B, Binv, sameVocab=False)
    Tba = calculateTransform(B, Binv, A, Ainv, sameVocab=False)
    TTinv = Tab * Tba
    return TTinv


def _makeCopy(model):
    """Make a copy of the given w2v model."""
    _, fname = tempfile.mkstemp()
    model.save(fname)
    newModel = gensim.models.Word2Vec.load(fname)
    newModel.wv.init_sims(replace=False)
    os.remove(fname)
    return newModel
