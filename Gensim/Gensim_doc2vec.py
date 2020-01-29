#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 08:43:41 2020

@author: dan
"""


import sys
import os
import re

import gensim



### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc
from Federal.models import UScourtDoc




def find_similar_docs(text, model, index, topN=5):

    tokens = gensim.utils.simple_preprocess(text.lower())
    inferred_vector = model.infer_vector(tokens)
    sims = model.docvecs.most_similar([inferred_vector], topn=5)

    simDocs = []
    for sim in sims:
        
        index_items = index[sim[0]]        
        similarity = sim[1]        
        dbx_str = index_items[0]
        docID = index_items[1]
        paraID = index_items[2]

        if dbx_str == "Delaware_decourtdoc": database = DEcourtDoc
        elif dbx_str == "Pennsylvania_pacourtdoc": database = PAcourtDoc
        elif dbx_str == "Federal_uscourtdoc": database = UScourtDoc
        else:
            print("Invalid database.")
            return

        doc = database.objects.get(pk=docID)
        maintext = doc.MainText
        para = get_para_from_maintext(paraID, maintext)

        simDocs.append((docID, paraID, similarity, para))

    return simDocs




def get_para_from_maintext(paraID, text):
    
    match = re.search(r"\<p\sid\=\'p" + str(paraID) + "\'\>", text)
    start = match.span()[1]
    pro_text = text[start:]
    end = pro_text.find("</p>")
    pro_text = pro_text[:end]

    return pro_text

