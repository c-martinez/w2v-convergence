from glob2 import glob
import numpy as np
import os

import pandas as pd
import cPickle as pkl
import nltk
from nltk.corpus import words, wordnet, stopwords
import string
import gzip

from util import checkPath
from settings import dataDir, cacheDir

print 'Using data from : ' + dataDir
print 'Using cache from: ' + cacheDir

_englishWords = set(w.lower() for w in words.words())
_englishStopWords = set(stopwords.words('english'))


def getYears():
    """Return a list of years for which data is available."""
    years = glob(dataDir + '????')
    years = [int(year.replace(dataDir, '')) for year in years]
    years = np.array(years)
    years.sort()
    return years


def getSentencesForYear(year):
    """Return list of sentences in given year.
    Each sentence is a list of words.
    Each word is a string.
    Returns a list of lists of strings."""
    docs = _getDocumentsForYear(year)

    sentences = []
    for doc in docs:
        for sent in doc:
            sentences.append(sent)
    return sentences


def getSentencesInRange(startY, endY):
    """Return list of sentences in given year.
    Each sentence is a list of words.
    Each word is a string.
    Return list of lists of strings."""
    return [s for year in range(startY, endY)
            for s in getSentencesForYear(year)]


def _getDocumentsForYear(year):
    """Retrieves the content of all documents for a year specified. Also caches
    the document for later use (if required). This is meant to speed document
    processing time, as document preparation requires significant time."""
    cachedFile = _getCachedName(year)

    checkPath(cacheDir)

    print 'Loading cached file: ' + cachedFile
    if os.path.exists(cachedFile):
        with gzip.open(cachedFile, 'rb') as f:
            documentsForYear = pkl.load(f)
    else:
        docs = _listDocsForYear(year)
        documentsForYear = []
        for doc in docs:
            articles = _getArticlesInDoc(doc)
            sentences = [_getSentencesInArticle(
                article) for article in articles]
            sentences = [_prepareSentences(sentence) for sentence in sentences]
            documentsForYear += sentences
        print 'Saving to cache %s...' % cachedFile

        with gzip.open(cachedFile, 'wb') as f:
            pkl.dump(documentsForYear, f)
    return documentsForYear


def _listDocsForYear(year):
    """Returns list of CSV documents available for a given year"""
    return glob(dataDir + str(year) + '/*.csv')


def _getArticlesInDoc(doc):
    """Returns a list of sentences in a given CSV doc"""
    try:
        df = pd.DataFrame.from_csv(doc, encoding='UTF8')
        df = df.replace(np.nan, '')
        df['FullData'] = df['Title'] + df['Content']
        return df['FullData'].tolist()
    except Exception as e:
        print 'Error reading file: ', doc
        print 'Ignorring...'
        raise e
        return []


def _getSentencesInArticle(body):
    """Transform a single news paper article into a list of sentences (each
    sentence represented by a string)."""
    sent_tokenizer = nltk.punkt.PunktSentenceTokenizer()
    sentences = sent_tokenizer.tokenize(body)
    return sentences


def _prepareSentences(sentences):
    """Document preparation for a list of sentences. Document preparation
    consists of: removing punctuation, removing invalid words, lowe casing and
    splitting into individual words."""
    newSentences = []
    for sentence in sentences:
        sentence = _depunctuate(sentence)
        sentence = sentence.lower()
        sentence = sentence.split(' ')
        sentence = [w for w in sentence if _isValidWord(w)]
        if len(sentence) > 0:
            newSentences.append(sentence)
    return newSentences


def _depunctuate(sentence):
    """Remove punctuation marks"""
    return filter(lambda w: w not in string.punctuation, sentence)


def _isValidWord(word):
    """Determine whether a word is valid. A valid word is a valid english
    non-stop word."""
    if word in _englishStopWords:
        return False
    elif word in _englishWords:
        return True
    elif wordnet.synsets(word):
        return True
    else:
        return False


def _getCachedName(year):
    """Return the name used for caching data for the given year"""
    cachedFile = cacheDir + str(year) + '.pklz'
    return cachedFile
