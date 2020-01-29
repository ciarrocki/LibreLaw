#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 17:55:37 2020

@author: dan
"""



import spacy




def test0(text):
    
    print("Loading medium english model . . .")
    nlp = spacy.load("en_core_web_md")

    print("Analyzing text . . . .")
    tokens = nlp(text)
    
    for token in tokens:
        print(token.text, token.has_vector, token.vector_norm, token.is_oov)




def test1(text):
    
    print("Loading medium english model . . .")
    nlp = spacy.load("en_core_web_md")

    print("Analyzing text . . . .")
    tokens = nlp(text)

    for token1 in tokens:
        for token2 in tokens:
            print(token1.text, token2.text, token1.similarity(token2))
