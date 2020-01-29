#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 21:06:18 2019

@author: dan
"""



import os
import sys



### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc






def dedupe(database="DE", del_source="DETX"):

    if database=='DE': docs = DEcourtDoc.objects.all()
    elif database=='PA': docs = PAcourtDoc.objects.all()
    else: return False

    matchCount = 0
    deleteCount = 0
    for i, doc in enumerate(docs):
        if i % 1000 == 0: print("\n\n********** ", i, "\n\n")
        date = doc.Date
        if (date.year == 1): continue
        jx = doc.Jurisdiction
        ct = doc.Court
        matches = docs.filter(Court__exact=ct).filter(Jurisdiction__exact=jx).filter(Date=date).exclude(id=doc.id)
        
        matchFlag = False
        matchSource = ""
        for match in matches:
            titleWords = match.CaseName.split()
            wCount = 0
            for w in titleWords[:3]: 
                if w in doc.CaseName: 
                    wCount += 1
            if wCount > 2:
                if (len(doc.MainText) > 50) and (len(match.MainText) > 50):
                    ratio = len(doc.MainText) / len(match.MainText)
                    if  ((ratio > .9) and (ratio < 1.1)): 
                        mainwords = match.MainText.split()[:10]
                        docwords = doc.MainText.split()[:10]
                        mtcount = 0
                        for w in mainwords[:10]:
                            if w in docwords: mtcount += 1
                        if mtcount > 7:
                            matchFlag = True
                            matchCount += 1
                            matchSource = match.Source
                            break

        if matchFlag:
            if (doc.Source == del_source) and (matchSource != del_source):
                deleteCount += 1                
                print("DELETE:")
                print("\tdeleteID:", doc.id, "\n\tdeleteCaseName:", doc.CaseName, "\n\tdeleteSource:", doc.Source)
                print("\tmatchID:", match.id, "\n\tmatchCaseName:", match.CaseName, "\n\tmatchSource:", match.Source)

    print("matchCount:", matchCount)
    print("deleteCount:", deleteCount)



