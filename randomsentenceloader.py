import gzip
import numpy as np
import cPickle as pkl

from glob2 import glob
from collections import defaultdict
from helpers import getSentencesForYear
from settings import chunkCache

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def getChunks():
    chunks = glob(chunkCache + '*.pklz')
    chunks = [ chunk.replace(chunkCache, '') for chunk in chunks ]

    year_chunk = defaultdict(list)
    for chunk in chunks:
        key = chunk.replace('.pklz', '').split('_')[0]
        key = int(key)
        year_chunk[key].append(chunk)

    return year_chunk

def getChunkName(year, chunkSize, chunkNumber='*'):
    return '%d_s%d_b%s.pklz'%(year,chunkSize, chunkNumber)

def buildChunks(year, chunkSize):
    existingChunks = glob(chunkCache + getChunkName(year, chunkSize))
    if len(existingChunks)>0:
        print 'Chunks for %d have already been created. Skipping...'%year
        return

    n0 = 0
    sentences = getSentencesForYear(year)
    r = range(chunkSize,len(sentences),chunkSize) + [ len(sentences) ]
    for i,n1 in enumerate(r):
        sentence_chunk = sentences[n0:n1]
        n0 = n1
        chunkName = getChunkName(year, chunkSize, chunkNumber=str(i).zfill(6))
        fileName = chunkCache + chunkName
        with gzip.open(fileName, 'wb') as f:
                pkl.dump(sentence_chunk, f)


class RandomSentenceLoader():
    def __init__(self, years, chunkSize=1000, seed=90517):
        self.seed = seed
        self.years = years
        self.chunkSize = chunkSize
        self.reset()

    def reset(self):
        np.random.seed(self.seed)
        chunks = getChunks()
        self.chunks = { y: chunks[y] for y in self.years }

    def _nextRandomYear(self):
        if len(self.chunks)==0:
            return None
        nextYear = np.random.choice(self.chunks.keys())
        log.debug('Next year: %d', nextYear)
        return nextYear

    def _nextMiniBatchName(self):
        nextYear = self._nextRandomYear()
        if nextYear is None:
            return None

        yearChunks = self.chunks[nextYear]
        selectIdx = np.random.randint(len(yearChunks))
        miniBatch = yearChunks[selectIdx]
        del yearChunks[selectIdx]

        if len(yearChunks)==0:
            del self.chunks[nextYear]
        return miniBatch

    def _nextMiniBatch(self):
        fileName = self._nextMiniBatchName()
        if fileName is None:
            return []
        with gzip.open(chunkCache + fileName, 'rb') as f:
            return pkl.load(f)


    def nextBatch(self, batchSize=2000):
        batch = []
        for i in range(0, batchSize, self.chunkSize):
            batch += self._nextMiniBatch()
        return batch

    def nextBatchGenerator(self, batchSize=2000):
        for i in range(0, batchSize, self.chunkSize):
            batch = self._nextMiniBatch()
            for b in batch:
                yield b
