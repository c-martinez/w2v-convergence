from glob2 import glob
import numpy as np
import os

import pandas as pd
import pickle as pkl
import nltk
from nltk.corpus import words, wordnet, stopwords
import string
import gzip

englishWords = set( w.lower() for w in words.words() )
englishStopWords = set(stopwords.words('english'))

#dataDir = 'times/'
#cacheDir = 'cache/'
dataDir = 'times/'
cacheDir = '/data3/times/times_cache/'

print 'Using cache dir: ' + cacheDir

def getYears():
    years = glob(dataDir + '????')
    years = [ int(year.replace(dataDir, '')) for year in years ]
    years = np.array(years)
    years.sort()
    return years

def listDocsForYear(year):
    return glob(dataDir + str(year) + '/*.csv')

def getArticlesInDoc(doc):
    try:
        '''Return a list of sentences'''
        df = pd.DataFrame.from_csv(doc, encoding='UTF8')
        df = df.replace(np.nan,'')
        df['FullData'] = df['Title'] + df['Content']
        return df['FullData'].tolist()
    except Exception as e:

        print 'Error reading file: ', doc
        print 'Ignorring...'
        raise e
        return []

def getSentencesForYear(year):
    '''Return list of lists of strings.
    Return list of sentences in given year.
    Each sentence is a list of words.
    Each word is a string.'''
    docs = getDocumentsForYear(year)

    sentences = []
    for doc in docs:
        for sent in doc:
            sentences.append(sent)
    return sentences

def getDocumentsForYear(year):
    '''Retrieves a list of documents for a year specified.'''
    cachedFile = getCachedName(year)

    if not os.path.isdir(cacheDir):
        print 'Folder does not exist, creating it...'
        os.mkdir(cacheDir)

    if os.path.exists(cachedFile):
        with gzip.open(cachedFile,'rb') as f:
            documentsForYear = pkl.load(f)
    else:
        docs = listDocsForYear(year)
        documentsForYear = []
        for doc in docs:
            articles = getArticlesInDoc(doc)
            sentences = [ getArticleAsSentences(article) for article in articles ]
            sentences = [ prepareSentences(sentence) for sentence in sentences ]
            documentsForYear += sentences
        print 'Saving to cache %s...'%cachedFile

        with gzip.open(cachedFile,'wb') as f:
            pkl.dump(documentsForYear,f)
    return documentsForYear

def getSentencesInRange(startY, endY):
    '''Return list of lists of strings.
    Return list of sentences in given year.
    Each sentence is a list of words.
    Each word is a string.'''
    return [ s for year in range(startY, endY) 
               for s in getSentencesForYear(year) ]

def getCachedName(year):
    cachedFile = cacheDir + str(year) + '.pklz'
    return cachedFile

def clean(w):
    w = w.lower()
    w = depunctuate(w)
    return w

def getVocabForYear(year):
    docs = listDocsForYear(year)
    vocab = set()
    for doc in docs:
        articles = getArticlesInDoc(doc)
        for article in articles:
            artSet = set(article.split(' '))
            vocab.update(artSet)
    vocab = set([ clean(w) for w in vocab ])
    return vocab

def depunctuate(sentence):
    return filter(lambda w: w not in string.punctuation, sentence)

def getArticleAsSentences(body):
    sent_tokenizer = nltk.punkt.PunktSentenceTokenizer()
    sentences = sent_tokenizer.tokenize(body)
    return sentences

def prepareSentences(sentences):
    newSentences = []
    for sentence in sentences:
        sentence = depunctuate(sentence)
        sentence = sentence.lower()
        sentence = sentence.split(' ')
        # sentence = [ w for w in sentence if len(w)>0 ]
        sentence = [ w for w in sentence if isValidWord(w) ]
        if len(sentence)>0:
            newSentences.append(sentence)
    return newSentences

def isValidWord(word):
    if word in englishStopWords:
        return False
    elif word in englishWords:
        return True
    elif wordnet.synsets(word):
        return True
    else:
        return False

