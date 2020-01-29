#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 22:38:02 2019

@author: dan
"""


### Imports

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
from Federal.models import UScourtDoc




### Main Functions

def saveOpToDjango(indata):
    
    # Record MUST have a valid jurisdiction, otherwise it cannot be saved
    # to Django (i.e., don't know which database to put it in)
    if "jurisdiction" not in indata.keys():
        print("Cannot save to Django: no jurisdiction")
        return False
    elif indata['jurisdiction'] == "Delaware": database = "DEcourtDoc"
    elif indata['jurisdiction'] == "Pennsylvania": database = "PAcourtDoc"
    elif indata['jurisdiction'] == "United States": database = "UScourtDoc"
    else:
        print("Cannot save to Django: invalid jurisdiction")
        return False

    # Default Values
    savedata = dict()
    savedata["OCCaseNo"] = 0
    savedata["jurisdiction"] = ""
    savedata["court"] = ""
    savedata["courtrank"] = 7
    savedata["date"] = "0001-01-01" # Must be in a valid mysql date format
    savedata["casename"] = ""
    savedata["fullcaption"] = ""
    savedata["partylist"] = ""
    savedata["caseno"] = ""
    savedata["doctype"] = "Opinion"
    savedata["title"] = "Opinion"
    savedata["maintext"] = ""
    savedata["footnotes"] = ""
    savedata["citation1"] = ""
    savedata["source"] = ""
    savedata["filepath"] = ""

    # Overwrite default values where data from the opinion is available;
    # any field from the opinion data that is not already in the "outdata" 
    # dictionary will not be used
    for key in indata.keys():
        if key in savedata.keys(): savedata[key] = indata[key]

    # Save the information to Django through its database API
    createDjangoRecord(savedata, database)

    return True





### Sub Functions

def createDjangoRecord(data, database):

    if database == 'DEcourtDoc': newCourtDoc = DEcourtDoc()
    elif database == 'PAcourtDoc': newCourtDoc = PAcourtDoc()
    elif database == 'UScourtDoc': newCourtDoc = UScourtDoc()
    else:
        print("createDjangoRecord failed: invalid database/jurisdiction")
        return

    newCourtDoc.OCCaseNo = data['OCCaseNo']
    newCourtDoc.Jurisdiction = data['jurisdiction']
    newCourtDoc.Court = data['court']
    newCourtDoc.CourtRank = data['courtrank']
    newCourtDoc.Date = data['date']
    newCourtDoc.CaseName = data['casename']
    newCourtDoc.FullCaption = data['fullcaption']
    newCourtDoc.PartyList = data['partylist']
    newCourtDoc.CaseNo = data['caseno']
    newCourtDoc.DocType = data['doctype']
    newCourtDoc.Title = data['title']
    newCourtDoc.MainText = data['maintext']
    newCourtDoc.Footnotes = data['footnotes']
    newCourtDoc.Citation1 = data['citation1']
    newCourtDoc.Source = data['source']
    newCourtDoc.Filepath = data['filepath']

    newCourtDoc.save()

    return True

