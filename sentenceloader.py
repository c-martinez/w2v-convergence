from helpers import *

class SentenceLoader():
    def __init__(self, years, batchSize=10000):
        self.years = years
        self.yearIdx = 0
        self.batchSize = batchSize
        self.buffer = []
        self.currentYear = 0

    def canFetch(self):
        return self.yearIdx < len(self.years)

    def getCurrentYear(self):
        return self.currentYear

    def nextBatch(self):
        batch = []
        # While batch has less than batchSize
        while len(batch) < self.batchSize:
            # Grab what we can from buffer
            itemsNeeded = self.batchSize - len(batch)
            grabN = int(min(itemsNeeded, len(self.buffer)))
            batch += self.buffer[:grabN]
            
            del self.buffer[:grabN]
            # print 'Batch now has: ', len(batch)
            # If not enough in buffer - load next year
            if len(self.buffer)==0:
                if self.canFetch():
                    # print 'Reloading buffer...',self.years[self.yearIdx]
                    self.currentYear = self.years[self.yearIdx]
                    self.buffer = getSentencesForYear(self.currentYear)
                    self.yearIdx += 1
                else:
                    # If no more years, exit
                    # print 'Out of years!'
                    break
        return batch

