#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 14:35:08 2020

@author: dan
"""


import gensim
import re




def test_para_corpus(court='DE'):

    court_LC = court.lower()
    if court_LC == "all": data_path = '/home/dan/Data/Gensim/Corpora/all_opinions_para.txt'
    elif court_LC == "de":data_path = '/home/dan/Data/Gensim/Corpora/de_opinions_para.txt'
    elif court_LC == "pa": data_path = '/home/dan/Data/Gensim/Corpora/pa_opinions_para.txt'
    elif court_LC == "us": data_path = '/home/dan/Data/Gensim/Corpora/us_opinions_para.txt'
    else:
        print("Invalid court.")

    i = 0
    blanklines = 0
    wellformed = 0
    
    for line in open(data_path):
        i += 1
        if line.strip() == "": blanklines += 1
        elif re.search(r"^\d{5,}\s", line): wellformed += 1
        else: print(line)
    print("Total:", i)
    print("Line is Blank:", blanklines)
    print("Well-Formed:", wellformed)
    print("Well-Formed Percentage:", wellformed / i)





class LawCorpus_para(object):
    """An interator that yields paragraphs (each a str)."""

    def __init__(self, court='de', add_label=True):
        court_LC = court.lower()
        if court_LC == "all": self.data_path = '/home/dan/Data/Gensim/Corpora/all_opinions_para.txt'
        elif court_LC == "de": self.data_path = '/home/dan/Data/Gensim/Corpora/de_opinions_para.txt'
        elif court_LC == "pa": self.data_path = '/home/dan/Data/Gensim/Corpora/pa_opinions_para.txt'
        elif court_LC == "us": self.data_path = '/home/dan/Data/Gensim/Corpora/us_opinions_para.txt'
        else:
            print("Invalid court.")
        self.add_label = add_label
        self.index = {}
        self.make_index()


    def __iter__(self):

        if self.add_label == False:
            for i, line in enumerate(open(self.data_path)):
                if not re.search(r"^\d{5,}\s", line): continue # CHECK THAT LINE STARTS WITH DOC_ID!
                docID, database, para, pro_line = line.split(None, 3)
                # assume there's one para per line, tokens separated by whitespace                
                yield gensim.utils.simple_preprocess(pro_line)
        else:
            for i, line in enumerate(open(self.data_path)):
                if not re.search(r"^\d{5,}\s", line): continue # CHECK THAT LINE STARTS WITH DOC_ID!
                docID, database, paraID, pro_line = line.split(None, 3)
                tokens = gensim.utils.simple_preprocess(pro_line)
                # Make index
                yield gensim.models.doc2vec.TaggedDocument(tokens, [i])


    def make_index(self):
        for i, line in enumerate(open(self.data_path)):
            if not re.search(r"^\d{5,}\s", line): continue # CHECK THAT LINE STARTS WITH DOC_ID!
            docID, database, paraID, pro_line = line.split(None, 3)
            docID = int(docID)
            self.index[i] = (database, docID, paraID)


    def clear_index(self):
        self.index = {}




class LawCorpus_sent(object):
    """An interator that yields sentences (each a str)."""

    def __init__(self, court='de'):
        court_LC = court.lower()
        if court_LC == "all": self.data_path = '/home/dan/Data/Gensim/Corpora/all_opinions_sent.txt'
        elif court_LC == "de": self.data_path = '/home/dan/Data/Gensim/Corpora/de_opinions_sent.txt'
        elif court_LC == "pa": self.data_path = '/home/dan/Data/Gensim/Corpora/pa_opinions_sent.txt'
        elif court_LC == "us": self.data_path = '/home/dan/Data/Gensim/Corpora/us_opinions_sent.txt'
        else:
            print("Invalid court.")

    def __iter__(self):
        for line in open(self.data_path):
            # assume there's one sentence per line, tokens separated by whitespace
            yield gensim.utils.simple_preprocess(line)






def test_similarity(*models_to_test):

    pairs_list = [[('sanctions', 'punishment'), ('sanctions','deter'), ('sanctions','judicial'), ('sanctions','reward'), ('sanctions','contract'), ('sanctions', 'swim')],
                  [('aggressive', 'hostile'), ('aggressive', 'forceful'), ('aggressive', 'insistent'), ('aggressive', 'peaceful'), ('aggressive', 'airplane')],     
                  [('car', 'vehicle'), ('car', 'tire'), ('car', 'foot'), ('car', 'apple'), ('car', 'justice')],
                 ]

    nearest_words_list = ['sanctions', 'aggressive', 'car', 'fell']

    print("PAIRS COMPARISON:\n")
    for pairs in pairs_list:
        print("{:<15} {:<15} ".format('Word 1', 'Word 2'), end='')
        for i, _ in enumerate(models_to_test): print("{:>10}".format("Model " + str(i)), end='')
        print('\n' + '-' * 52)
        for w1, w2 in pairs:
            print('{:<15} {:<15} '.format(w1, w2), end='')
            for m in models_to_test:
                sim = m.wv.similarity(w1, w2)
                print("{:>10.5f}".format(sim), end='')
            print()
        print()

    print("\nNEAREST WORDS COMPARISON:\n")
    for word in nearest_words_list:
        print("Word:", word)
        for i, m in enumerate(models_to_test):
            print("Model " + str(i) + ":", end='')
            top_words = [(word2, "{:.3f}".format(freq)) for word2, freq in m.wv.most_similar(positive=[word], topn=3)]
            print(top_words)
        print()





