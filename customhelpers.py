def getYears():
    """Return a list of years for which data is available."""
    years = [1900, 1901, 1902, 1903, 1905, 1905, 1906, 1907, 1908, 1909, 1910]
    return years


def getSentencesForYear(year):
    """Return list of sentences in given year.
    Each sentence is a list of words.
    Each word is a string.
    Returns a list of lists of strings."""
    sentence1 = ['this', 'is', 'one', 'sentence']
    sentence2 = ['this', 'is', 'another', 'sentence']
    sentence3 = ['and', 'yet', 'another', 'one']
    sentences = [sentence1, sentence2, sentence3]
    return sentences
