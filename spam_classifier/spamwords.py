from nltk.stem.porter import PorterStemmer

class Spamwords():

    spamwords = []

    def __init__(self, filename):
        self.__parse(filename)

    def __parse(self, filename):
        file = open(filename)
        lines = file.readlines()
        word_list = []
        for line in lines:
            words = line.split()
            word_list = word_list + words
        porter = PorterStemmer()
        # self.spamwords = set([porter.stem(word.strip().lower()) for word in word_list])
        self.spamwords = list(set(word_list))


