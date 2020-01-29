#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 11:47:33 2020

@author: dan
"""



import os
import gensim




#p0 = '/home/dan/Data/Gensim/Models/de_new.w2v'
def load_model(path):
    return gensim.models.Word2Vec.load(path)




def getFileList(path, ext='', recursive=False):
    fileList = []
    if not path.endswith('/'): path = path + '/'
    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(ext): fileList.append(str(os.path.join(root, file)))
    else:
        fileList = [path + file for file in os.listdir(path)\
                    if os.path.isfile(os.path.join(path, file)) and file.endswith(ext)]
    return fileList



