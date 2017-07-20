#!/usr/bin/env python 
"""Usage: runGenerateModels.py --y0=<y0> --yN=<yN> --nYears=<years> --outDir=<dir> [--step=<years>]

  --y0 <y0>         First year in the generated models
  --yN <yN>         Last year in the generated models
  --nYears <years>  Number of years per model
  --outDir <dir>    Directory where models will be writen to
  --step <years>    Step between start year of generated models [default: 1]
"""
import gensim

from docopt import docopt
from helpers import getSentencesInRange

def generateModels(y0, yN, yearsInModel, stepYears, modelFolder):
    '''Documentation missing...
    '''
    for year in range(y0,yN-yearsInModel+1, stepYears):
        startY = year
        endY   = year + yearsInModel
        modelName = modelFolder + '/%d_%d.w2v'%(year,year + yearsInModel)
        print 'Building model: ',modelName

        sentences = getSentencesInRange(startY, endY)
        model = gensim.models.Word2Vec(min_count=1)
        model.build_vocab(sentences)
        model.train(sentences)

        print '...saving'
        model.init_sims(replace=True)
        model.save_word2vec_format(modelName, binary=True)

if __name__ == '__main__':
    args = docopt(__doc__)
    yearsInModel = int(args['--nYears'])
    stepYears = int(args['--step'])
    outDir = args['--outDir']
    y0 = int(args['--y0'])
    yN = int(args['--yN'])

    generateModels(y0, yN, yearsInModel, stepYears, outDir)

