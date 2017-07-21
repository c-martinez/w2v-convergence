import os
import tempfile
import gensim
import numpy as np

from sortedcontainers import SortedDict
from sentenceloader import SentenceLoader
from w2vtransformation import calculateTransform, getModelInv


def computeDivergenceOverYearRange(yearRange, batchSize, maxSentences):
    # Initialize model
    vocabSizeMB = 1000 * 1024 * 1024
    model = gensim.models.Word2Vec(max_vocab_size=vocabSizeMB, size=300)

    # Initialize sentence loader
    loader = SentenceLoader(yearRange, batchSize=batchSize)
    batch = loader.nextBatch()
    y0 = yearRange[0]

    # Initialize returned objects
    divergence = SortedDict()
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
            d = testModelDivergence(oldModel, oldModelinv, model, modelinv)
            divergence[cumSentences] = d

        # Prepare for next iteration
        doUpdate = True
        batch = loader.nextBatch()
        oldModel = _makeCopy(model)
        oldModelinv = modelinv

    return divergence, sentenceYearCounter, vocabSize


def testModelDivergence(A, Ainv, B, Binv):
    """Given two models (A and B) and their inverse matrices, calculate the
    divergence between the two models (as a single value)."""
    TTinv = _calculateSymetricTransform(A, Ainv, B, Binv)
    Si_ip = np.trace(TTinv) / A.vector_size
    return Si_ip


def measureDiagonal(A, Ainv, B, Binv):
    """Given two models (A and B) and their inverse matrices, calculate the
    divergence between the two models, per dimension (as a vector of the same
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
