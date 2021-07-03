from glob import glob
import ntpath

class Words():
    
    def __init__(self, data_path:str):
        self.data_path = data_path

    def readWordFile(self, word_file:str):
        """returns the list of words in a file
        """
        with open(word_file) as f:
            ls = f.readlines()
            lsstrip = [x.strip() for x in ls]
            if '' in lsstrip: lsstrip.remove('')
            f.close()
        return lsstrip

    def getNouns(self):
        """returns a list of nouns
        """
        word_files = self.getWordFiles()
        nouns = [ntpath.basename(f).replace('.txt','') for f in word_files]
        return nouns

    def getWordFiles(self):
        """returns list of word files
        """
        return glob(f'{self.data_path}/words/*.txt')

    def getWordLists(self):
        """returns list of lists of tracked words
        multidimensional list
        """
        word_lists = []
        for word_file in self.getWordFiles():
            ls = self.readWordFile(word_file)
            word_lists.append(ls)
        return word_lists

    def getWordList(self, noun:str):
        """returns a single word list
        """
        word_file = self.getWordFiles()[self.getNouns().index(noun)]
        return self.readWordFile(word_file)
