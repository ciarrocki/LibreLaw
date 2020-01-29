#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 22:38:02 2019

@author: dan
"""


### Imports

import os
import sys
import re




### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEstat, DEtree
from Pennsylvania.models import PAstat, PAtree






### Main Functions

def saveDEtreeRecord(indata):
    database = 'DEtree'
    # Load values from the parser's output dict
    titleData = indata
    # Save the information to Django through its database API
    createTreeRecord(titleData, database)
    return True




def savePAtreeRecord(fullName, treeType, number, nameText, description, bigHTML, smallHTML, source, filepath):
    database = 'PAtree'
    data = dict()
    data["fullName"] = fullName
    data["type"] = treeType
    data["number"] = number
    data["nameText"] = nameText
    data["description"] = description
    data["bigHTML"] = bigHTML
    data["smallHTML"] = smallHTML
    data["source"] = source
    data["filepath"] = filepath
    createTreeRecord(data, database)
    return True






def saveDEruleTree(fullName, treeType, number, nameText, description, bigHTML, smallHTML, source, filepath):
    database = 'DEtree'
    data = dict()
    data["fullName"] = fullName
    data["type"] = treeType
    data["number"] = number
    data["nameText"] = nameText
    data["description"] = description
    data["bigHTML"] = bigHTML
    data["smallHTML"] = smallHTML
    data["source"] = source
    data["filepath"] = filepath
    createTreeRecord(data, database)
    return True
 





def savePAruleTree(fullName, treeType, number, nameText, description, bigHTML, smallHTML, source, filepath):
    database = 'PAtree'
    data = dict()
    data["fullName"] = fullName
    data["type"] = treeType
    data["number"] = number
    data["nameText"] = nameText
    data["description"] = description
    data["bigHTML"] = bigHTML
    data["smallHTML"] = smallHTML
    data["source"] = source
    data["filepath"] = filepath
    createTreeRecord(data, database)
    return True






def saveDErule(title, number, text, treeNumber, filepath, citation0, previous, next0, rulesname):
    data = {}
    data['Title'] = title
    data['SectionType'] = "Rule"
    data['TitleNum'] = treeNumber
    data['Number'] = number
    data['Text'] = text
    data['Previous'] = previous
    data['Next'] = next0
    data['Source'] = "DE Government Website"
    data['Filepath'] = filepath
    data['Tree0'] = rulesname
    data['Tree1'] = ""
    data['Tree2'] = ""
    data['Tree3'] = ""
    data['Tree4'] = ""
    data['Tree5'] = ""
    data['Tree6'] = ""
    data['Tree7'] = ""
    data['Tree8'] = ""
    data['Tree9'] = ""
    data['Citation0'] = citation0
    data['Citation1'] = ""
    createStatRecord(data, 'DEstat')
    return True





def savePArule(title, number, text, treeNumber, filepath, citation0, previous, next0, rulesname):
    data = {}
    data['Title'] = title
    data['SectionType'] = "Rule"
    data['TitleNum'] = treeNumber
    data['Number'] = number
    data['Text'] = text
    data['Previous'] = previous
    data['Next'] = next0
    data['Source'] = "PA Code and Bulletin (pacodeandbulletin.gov)"
    data['Filepath'] = filepath
    data['Tree0'] = rulesname
    data['Tree1'] = ""
    data['Tree2'] = ""
    data['Tree3'] = ""
    data['Tree4'] = ""
    data['Tree5'] = ""
    data['Tree6'] = ""
    data['Tree7'] = ""
    data['Tree8'] = ""
    data['Tree9'] = ""
    data['Citation0'] = citation0
    data['Citation1'] = ""
    data['ActAct'] = 0
    data['ActYear'] = 0
    data['ActPL'] = 0
    data['Date'] = "0001-01-01"

    createStatRecord(data, 'PAstat')
    return True






def saveDEstatRecords(indata):
    
    database = 'DEstat'
    
    for sec in indata["sections"]:

        secData = {}
        secData['Title'] = sec['title']
        secData['SectionType'] = sec['sectiontype']
        secData['TitleNum'] = indata['number']
        secData['Number'] = sec['number']
        secData['Text'] = sec['text']
        secData['Previous'] = sec['previous']
        secData['Next'] = sec['next']
        secData['Source'] = indata['source']
        secData['Filepath'] = indata['filepath']
        secData['Citation0'] = sec['Citation0']
        secData['Citation1'] = ""
        for i, item in enumerate(sec['sectionstack']):
            key = "Tree" + str(i)
            secData[key] = item[0] + " " + item[1] + " - " + item[2]
        for j in range(i+1, 10):
            key = "Tree" + str(j)
            secData[key] = ""
        createStatRecord(secData, database)

    return True




def savePAstatRecords(sectionsDict, titleNum, source, filepath):

    database = 'PAstat'

    for sectionNumKey, sec in sectionsDict.items():

        if 'text' not in sec.keys(): sec['text'] = ""
        
        secData = {}
        secData['Title'] = sec['title']
        secData['SectionType'] = sec['sectiontype']
        secData['TitleNum'] = str(titleNum)
        secData['Number'] = sec['number']
        secData['Text'] = sec['text']
        secData['Previous'] = sec['previous']
        secData['Next'] = sec['next']
        secData['Source'] = source
        secData['Filepath'] = filepath
        secData['Citation0'] = sec['Citation0']
        secData['Citation1'] = ""

        # Date field is special; must default to "0001-01-01"
        if 'date' in sec.keys():
            if sec['date'] != "": secData['Date'] = sec['date']
            else: secData['Date'] = "0001-01-01"
        else: secData['Date'] = "0001-01-01"

        # This data is not relevant to codified statutes
        secData['ActAct'] = 0
        secData['ActYear'] = 0
        secData['ActPL'] = 0

        for i, item in enumerate(sec['sectionstack']):
            key = "Tree" + str(i)
            secData[key] = item
        for j in range(i+1, 10):
            key = "Tree" + str(j)
            secData[key] = ""
    
        createStatRecord(secData, database)

    return True




def savePAunconsolidated(data):
    secData = {}

    # These are the only fields populated for unconsolidated statutes
    secData['ActAct'] = data['act']
    secData['ActYear'] = data['year']
    secData['ActPL'] = data['PL']
    secData['Title'] = data['title']
    secData['SectionType'] = "Act"
    secData['TitleNum'] = str(data['titlenum'])
    secData['Text'] = data['maintext']
    secData['Source'] = "PAlegis"

    # Date field is special; must default to "0001-01-01"
    if 'date' in data.keys():
        if data['date'] != "": secData['Date'] = data['date']
        else: secData['Date'] = "0001-01-01"
    else: secData['Date'] = "0001-01-01"

    # These fields are not applicable for unconsolidated statutes
    secData['Number'] = ""
    secData['Previous'] = ""
    secData['Next'] = ""    
    secData['Filepath'] = ""
    secData['Tree0'] = ""
    secData['Tree1'] = ""
    secData['Tree2'] = ""
    secData['Tree3'] = ""
    secData['Tree4'] = ""
    secData['Tree5'] = ""
    secData['Tree6'] = ""
    secData['Tree7'] = ""
    secData['Tree8'] = ""
    secData['Tree9'] = ""
    secData['Citation0'] = ""
    secData['Citation1'] = ""

    # Need to save twice when TWO tables are specified! TRICKY
    if re.search(r"(\d{1,2})\s?\,\s?(\d{1,2})", secData["TitleNum"]):
        match = re.search(r"(\d{1,2})\s?\,\s?(\d{1,2})", secData["TitleNum"])
        titleNum1 = match[1]
        titleNum2 = match[2]
        secData['TitleNum'] = titleNum1
        createStatRecord(secData, "PAstat")
        secData['TitleNum'] = titleNum2
        createStatRecord(secData, "PAstat")
    else:    
        createStatRecord(secData, "PAstat")







### Sub Functions

def createTreeRecord(data, database):
    
    if database == 'DEtree': newTree = DEtree()
    elif database == 'PAtree': newTree = PAtree()
    else:
        print("createTreeRecord failed: invalid database")
        return

    newTree.fullName = data["fullName"]
    newTree.type = data["type"]
    newTree.number = data["number"]
    newTree.nameText = data["nameText"]
    newTree.description = data["description"]
    newTree.bigHTML = data["bigHTML"]
    newTree.smallHTML = data["smallHTML"]
    newTree.source = data["source"]
    newTree.filepath = data["filepath"]
    newTree.save()

    return True





def createStatRecord(data, database):
    
    if database == 'DEstat': newStat = DEstat()
    elif database == 'PAstat': newStat = PAstat()
    else:
        print("createDEstatRecord failed: invalid database")
        return
    
    newStat.Title = data['Title'][:350]
    newStat.SectionType = data['SectionType'][:200]
    newStat.TitleNum = data['TitleNum']
    newStat.Number = data['Number'][:50]
    newStat.Text = data['Text']
    newStat.Previous = data['Previous'][:400]
    newStat.Next = data['Next'][:400]
    newStat.Source = data['Source'][:150]
    newStat.Filepath = data['Filepath'][:150]
    newStat.Tree0 = data['Tree0'][:350]
    newStat.Tree1 = data['Tree1'][:350]
    newStat.Tree2 = data['Tree2'][:350]
    newStat.Tree3 = data['Tree3'][:350]
    newStat.Tree4 = data['Tree4'][:350]
    newStat.Tree5 = data['Tree5'][:350]
    newStat.Tree6 = data['Tree6'][:350]
    newStat.Tree7 = data['Tree7'][:350]
    newStat.Tree8 = data['Tree8'][:350]
    newStat.Tree9 = data['Tree9'][:350]
    newStat.Citation0 = data['Citation0']
    newStat.Citation1 = data['Citation1']

    if database == 'PAstat':
        newStat.ActAct = data['ActAct']
        newStat.ActYear = data['ActYear']
        newStat.ActPL = data['ActPL']
        newStat.ActDate = data['Date']

    newStat.save()
    
    return True


