#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 20:50:17 2019

@author: dan
"""


import sys
import os

from OPparser_utils import replaceCase
from OPparser_lists import slugAbbDict, courtAbbDict


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc
from Federal.models import UScourtDoc





def add_all_slug0(database='DE'):
    if database=='DE': docs = DEcourtDoc.objects.all()
    elif database=='PA': docs = PAcourtDoc.objects.all()
    elif database=='US': docs = UScourtDoc.objects.all()
    else: 
        print("Invalid database.")
        return False

    print("Adding slug0 for", len(docs), "court documents: Completed: ", end='')
    for i, doc in enumerate(docs):
        if i % 1000 == 0: print(i, ' . . . ', end='')
        doc.Slug0 = getSlug0(doc)
        doc.save()
    print(" Done.")





def getSlug0(doc):

    casename = doc.CaseName
    casename_abb = getAbbCaseName(casename)

    date = doc.Date
    if date.year == 1: datestring = ""
    else: datestring = date.strftime("%b. %-d, %Y")

    jx = doc.Jurisdiction
    court = doc.Court
    courtabb = courtAbbDict[(jx, court)]

    if checkCitation(doc.Citation1): cite = doc.Citation1
    elif checkCitation(doc.Citation2): cite = doc.Citation2
    elif checkCitation(doc.Citation3): cite = doc.Citation3
    else: cite = ""

    if cite: 
        if datestring: slug0 = casename_abb + ", " + cite + " (" + courtabb + " " + datestring + ")"
        else: slug0 = casename_abb + ", " + cite + " (" + courtabb + ")"
    else:
        if datestring: slug0 = casename_abb + " (" + courtabb + " " + datestring + ")"
        else: slug0 = casename_abb + " (" + courtabb + ")"
    return slug0





def getAbbCaseName(casename, maxlength=150):
    wordlist = casename.strip().split()
    wordlist = [word[:-1] if word.endswith(',') else word for word in wordlist] # Remove ending commas from words
    wordlist = [replaceCase(slugAbbDict, word) for word in wordlist]
    abbCaseName = " ".join(wordlist)
    if len(abbCaseName) > 150: abbCaseName = abbCaseName[:150]    
    return abbCaseName





def checkCitation(cite):
    if cite == None: return False
    if cite == "NONE": return False
    if cite == "": return False
    return True
