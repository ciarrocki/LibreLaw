#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 21:55:30 2019

@author: dan
"""



import spacy


from CiteVista_utils import getFileList, corporaDir




#----------------------------------------------------
### START SCRIPT ------------------------------------
#print("Loading 'en_core_web_md' . . . ", end='')
nlp = spacy.load("en_core_web_md")
#print("Done.")
#----------------------------------------------------
#----------------------------------------------------





def process_from_text_medium(path=corporaDir + 'puretext/Delaware/', recursive=True):
    
    flist = getFileList(path=path, recursive=recursive)[:100]
    print("Processing", len(flist), "records.")
    entities = [doc.ents for doc in list(nlp.pipe(text_generator(flist)))]
    
    return entities





def text_generator(flist):
    for f in flist: yield open(f, 'r').read()
            
    


    
