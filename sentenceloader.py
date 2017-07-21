from helpers import getSentencesForYear


class SentenceLoader():
    """Helper class for loading batches of news paper article data, in
    chronologic order. Each batch contains the same number of sentences. More
    than one batch can be created from the same year. If the curent year does
    not have enough data to fill the batch, sentences from the following year
    are read until the batch has the required size.

    NOTE: This class uses `helpers.getSentencesForYear` to load sentences. Make
    sure this function is implemented to match your needs.
    """

    def __init__(self, years, batchSize=10000):
        """Create a new SentenceLoader which will load batches from the given
        batchSize, over the given range of years (as a list)."""
        self.years = years
        self.yearIdx = 0
        self.batchSize = batchSize
        self.buffer = []
        self.currentYear = 0

    def canFetch(self):
        """Can the sentence loader load more sentences?"""
        return self.yearIdx < len(self.years)

    def getCurrentYear(self):
        """From which year is the current batch loaded from? If from more than
        one year, this method will return the latest year."""
        return self.currentYear

    def nextBatch(self):
        """Load and return the next batch of sentences."""
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
            if len(self.buffer) == 0:
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
