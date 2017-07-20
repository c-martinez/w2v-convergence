import gensim
import numpy as np

from sortedcontainers import SortedDict
from sentenceloader import SentenceLoader
from PCAStuff import calculateTransform, getModelInv

def testModelDivergence(A, Ainv, B, Binv):
    Tab = calculateTransform(A, Ainv, B, Binv, sameVocab=False)
    Tba = calculateTransform(B, Binv, A, Ainv, sameVocab=False)
    TTinv = Tab * Tba
    Si_ip = np.trace(TTinv)  / 300
    return Si_ip

def makeCopy(model):
    fname = 'tmp.w2v'
    model.save(fname)
    newModel = gensim.models.Word2Vec.load(fname)
    newModel.wv.init_sims(replace=False)
    return newModel

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
    oldInv = None

    print 'Building models (%d):'%y0
    while cumSentences<maxSentences and len(batch)>0:
        cumSentences += len(batch)
        cumSentencesStr = ('%d'%cumSentences).zfill(12)
        currYear = loader.getCurrentYear()
        modelName = '%d (%s)'%(currYear,cumSentencesStr)
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
        oldModel = makeCopy(model)
        oldModelinv = modelinv

    return divergence, sentenceYearCounter, vocabSize
