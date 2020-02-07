#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:37:43 2019

@author: dan
"""



import sys
import os
import re

from CiteVista_utils import strip_tags

import en_core_web_sm, en_core_web_lg  # Part of spacy - MIT license


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc
from Federal.models import UScourtDoc







def get_MT_by_docID(docID, database="DE"):
    """
    Gets and returns the main text from a court document in the database.
    The main text is cleaned of html tags and certain content.

    docID: the docID number of hte document for which we want to get the 
    clean MT
    """
    
    if database.lower() == 'de': doc = DEcourtDoc.objects.get(pk=docID)
    elif database.lower() == 'pa': doc = PAcourtDoc.objects.get(pk=docID)
    else:
        print("Invalid database.")
        return ""

    text = doc.MainText

    text = clean_MT(text)

    return text




def clean_MT(text):
    """
    Cleans text by removing:
        (1) All footnote anchors and their corresponding html tags
        (2) All html tags
        
    """

    newtext = re.sub(r"\<a\shref\=\#FNnumber.*?\<\/a\>", "", text)
    newtext = strip_tags(newtext)
    return newtext    






def get_people_orgs(text):
    
    nlp = en_core_web_lg.load()
    doc = nlp(text)
    orgs = [x.text for x in doc.ents if x.label_ == 'ORG']
    people = [x.text for x in doc.ents if x.label_ == 'PERSON']
    #pprint([(x.text, x.label_) for x in doc.ents])

    orgdict = dict()
    for item in orgs:
        if item in orgdict.keys(): orgdict[item] += 1
        else: orgdict[item] = 1
    orgs = list(orgdict.items())
    orgs.sort(key = lambda x: x[1], reverse=True)
        
    peopledict = dict()
    for item in people:
        if item in peopledict.keys(): peopledict[item] += 1
        else: peopledict[item] = 1
    people = list(peopledict.items())
    people.sort(key = lambda x: x[1], reverse=True)    

    people = filter_people_orgs(people)

    return people, orgs
    




def filter_people_orgs(plist):
    newlist = []
    for p in plist:
        fail = False
        pro = p[0].lower()
        for word in dqList_PeopleOrgs:
            if word in pro:
                fail = True
                break
        if not fail: newlist.append(p)
    return newlist


dqList_PeopleOrgs = ['plaintiff', 'defendant', 'complaint',
                     'merger']


