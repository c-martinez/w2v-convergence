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
    '''Generate a list of chunks for each year available on the chunkCache.
    Lists of all available chunks are stored in a dictionary with years as its keys.
    A 'chunk' is a pklz file containing N sentences from a given year.

    e.g:
    chunks = {
        1900: [ '1900_s1000_b000001.pklz', '1900_s1000_b000002.pklz' ]
        1910: [ '1910_s1000_b000001.pklz', '1910_s1000_b000002.pklz' ]
    }
    '''
    chunks = glob(chunkCache + '*.pklz')
    chunks = [chunk.replace(chunkCache, '') for chunk in chunks]

    year_chunk = defaultdict(list)
    for chunk in chunks:
        key = chunk.replace('.pklz', '').split('_')[0]
        key = int(key)
        year_chunk[key].append(chunk)

    return year_chunk


def getChunkName(year, chunkSize, chunkNumber='*'):
    '''Build the name of a 'chunk' for a given year, size and chunk number.
    The year indicates the year from which sentences in a chunk come from.
    The chunkSize incidates the maximum number of sentences in the chunk.
    The chunkNumber indicates is a consecutive number identifying the chunk.
    If no chunkNumber is given, the name is generated with a '*' (which can
    be use in a glob).
    '''
    return '%d_s%d_b%s.pklz' % (year, chunkSize, chunkNumber)


def buildChunks(year, chunkSize):
    '''Loads all sentences from a given year and splits them in chuncks
    of the given number of sentences (chunkSize). The number of chunks depends on
    the total number of sentences available. E.g. for a year containing 5123
    sentences, with a chunk size of 1000, 6 chunks will be generated (5 chunks
    with 1000 sentences and one chunk with 123).'''
    existingChunks = glob(chunkCache + getChunkName(year, chunkSize))
    if len(existingChunks) > 0:
        print 'Chunks for %d have already been created. Skipping...' % year
        return

    n0 = 0
    sentences = getSentencesForYear(year)
    r = range(chunkSize, len(sentences), chunkSize) + [len(sentences)]
    for i, n1 in enumerate(r):
        sentence_chunk = sentences[n0:n1]
        n0 = n1
        chunkName = getChunkName(year, chunkSize, chunkNumber=str(i).zfill(6))
        fileName = chunkCache + chunkName
        with gzip.open(fileName, 'wb') as f:
            pkl.dump(sentence_chunk, f)


class RandomSentenceLoader():
    '''Loads batches of sentences from a range of years at random.

    E.g: Given the years with available chunks.
    1900: [ c1900.1, c1900.2, c1900.3, c1900.4, c1900.5, c1900.6 ]
    1901: [ c1901.1, c1901.2, c1901.3, c1901.4, c1901.5, c1901.6 ]
    1902: [ c1902.1, c1902.2, c1902.3, c1902.4, c1902.5, c1902.6 ]

    A batch could be: [ c1900.3, c1902.1, c1900.5, c1901.5 ]. Where c190?.? is
    a list of sentences.
    '''

    def __init__(self, years, chunkSize=1000, seed=90517):
        '''Initialize sentence loader.
        Years is the range of years from which sentences can be loaded. chunkSize
        is the numbe of sentences on each chunk. seed is used to initialize random
        number generator (so randomness can be reproducible). This is necessary
        in order to produce two random sets which are random, but identical to
        each other.'''
        self.seed = seed
        self.years = years
        self.chunkSize = chunkSize
        self.reset()

    def reset(self):
        '''Reset random number generator to initial state.'''
        np.random.seed(self.seed)
        chunks = getChunks()
        self.chunks = {y: chunks[y] for y in self.years}

    def _nextRandomYear(self):
        '''Select year from which next chunk will be taken'''
        if len(self.chunks) == 0:
            return None
        nextYear = np.random.choice(self.chunks.keys())
        log.debug('Next year: %d', nextYear)
        return nextYear

    def _nextChunkName(self):
        '''Select the filename of the next chunk to be loaded'''
        nextYear = self._nextRandomYear()
        if nextYear is None:
            return None

        yearChunks = self.chunks[nextYear]
        selectIdx = np.random.randint(len(yearChunks))
        miniBatch = yearChunks[selectIdx]
        del yearChunks[selectIdx]

        if len(yearChunks) == 0:
            del self.chunks[nextYear]
        return miniBatch

    def _nextChunk(self):
        '''Loads the next chunk of sentences.'''
        fileName = self._nextChunkName()
        if fileName is None:
            return []
        with gzip.open(chunkCache + fileName, 'rb') as f:
            return pkl.load(f)

    def nextBatch(self, batchSize=2000):
        '''Generate a batch of sentences of the given batchSize. Sentences are
        selected (in chunks) from different years at random.'''
        batch = []
        for i in range(0, batchSize, self.chunkSize):
            batch += self._nextChunk()
        return batch

    def nextBatchGenerator(self, batchSize=2000):
        '''As nextBatch, but returns a generator (so the full batch is not
        loaded into memory at once).'''
        for i in range(0, batchSize, self.chunkSize):
            batch = self._nextChunk()
            for b in batch:
                yield b
