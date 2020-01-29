#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 17:13:30 2019

@author: dan



"""





import re
import os
import sys
from dateutil.parser import parse


from CiteVista_utils import WLrawCitesDir
from CiteVista_utils import getFileList, isDate
from CiteVista_patterns import WLsearchPatterns, findCites_keywords, WLdateRE


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc
from Federal.models import UScourtDoc





def add_all_WL_cites(searchfilepath, database="DE", verbose=0, 
                     overwrite=False, skip_reported=True):
    """


    """

    if database=='DE': docs = DEcourtDoc.objects.all()
    elif database=='PA': docs = PAcourtDoc.objects.all()
    elif database=='US': docs = UScourtDoc.objects.all() 
    else: 
        print("Invalid database.")
        return False

    total = len(docs)
    print("Adding WL cites for", total, "records.")
    num_lines = sum(1 for line in open(searchfilepath))
    print("Number of lines in WL searchfile:", num_lines)
    skipCounter = 0
    successCounter = 0
    failCounter = 0
    print("Completed: ", end="")

    for i, doc in enumerate(docs):
        if i % 100 == 0: print(i, ". . . ", end='')

        # Skip Conditions
        if not overwrite: 
            if (doc.Citation3 != "") or (doc.Citation3 == "NONE"): 
                skipCounter += 1
                continue
        if skip_reported:
            if (doc.Citation1 != ""): 
                skipCounter += 1
                continue

        # Initialize basic document variables: PATTERNSET, date
        date = doc.Date
        patternSet = genKeyWords(doc.CaseName)
        if verbose > 0: print("Search Patterns:", patternSet)

        # Generate longList: All lines in the searchfile that match any of the keywords
        longList = []
        with open(searchfilepath, 'r') as searchfile:
            for line in searchfile.readlines():
                for pattern in patternSet:
                    if re.search(pattern, line, flags=re.IGNORECASE):
                        longList.append(line)

        # General shortList: go through longList and keep cites that match date
        shortList = []
        for line in longList:
            match = line.split(';')
            if len(match) != 3: continue
            pos = match[1].find(match[0]) + len(match[0])
            afterText = match[1][pos:]
            dateMatch = re.search(WLdateRE, afterText) # Only returns the FIRST match (if any)
            if dateMatch: dateText = dateMatch[0] # Pull out date group
            else: continue
            if isDate(dateText): citeDate = parse(dateText, fuzzy=True)
            else: continue
            if (citeDate.year == date.year) and (citeDate.month == date.month) and (citeDate.day == date.day):
                shortList.append(match)

        # Generate Final WL Cite Prediction:
        finalPrediction = ""
        shortCiteList = [item[0] for item in shortList]
        shortCiteSet = set(shortCiteList)
        finalList = list(shortCiteSet)
        if len(shortCiteSet) == 0: finalPrediction = ""
        elif len(shortCiteSet) == 1: finalPrediction = finalList[0]
        else:
            if verbose > 0: print("Multiple WL cites found.")
            finalPrediction = ""
    
        # Add to database
        if finalPrediction: 
            successCounter += 1
            doc.Citation3 = finalPrediction
        else: 
            failCounter += 1
            doc.Citation3 = "NONE"
        doc.save()

    # Final Report
    print("\nDone.")
    print("Success:", successCounter)
    print("Fail:", failCounter)
    print("Skip:", skipCounter)

    return True
    
    
    




def getWLcite(docID, searchfilepath, database='DE', verbose=0, add=False):
    
    if database=='DE': doc = DEcourtDoc.objects.get(pk=docID)
    elif database=='PA': doc = PAcourtDoc.objects.get(pk=docID)
    else: return False
    date = doc.Date
    patternSet = genKeyWords(doc.CaseName)
    if verbose > 0: print("Search Patterns:", patternSet)

    # Generate longList: All lines in the searchfile that match any of the keywords
    longList = []
    with open(searchfilepath, 'r') as searchfile:
        for line in searchfile.readlines():
            for pattern in patternSet:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    longList.append(line)

    # General shortList: go through longList and keep cites that match date
    shortList = []
    for line in longList:
        match = line.split(';')
        if len(match) != 3: continue
        pos = match[1].find(match[0]) + len(match[0])
        afterText = match[1][pos:]
        dateMatch = re.search(WLdateRE, afterText) # Only returns the FIRST match (if any)
        if dateMatch: dateText = dateMatch[0] # Pull out date group
        else: continue
        if isDate(dateText): citeDate = parse(dateText, fuzzy=True)
        else: continue
        if (citeDate.year == date.year) and (citeDate.month == date.month) and (citeDate.day == date.day):
            shortList.append(match)

    # Generate Final WL Cite Prediction:
    finalPrediction = ""
    shortCiteList = [item[0] for item in shortList]
    shortCiteSet = set(shortCiteList)
    finalList = list(shortCiteSet)
    if len(shortCiteSet) == 0: finalPrediction = ""
    elif len(shortCiteSet) == 1: finalPrediction = finalList[0]
    else:
        if verbose > 0: print("Multiple WL cites found.")
        finalPrediction = ""

    if add:
        if finalPrediction: doc.Citation3 = finalPrediction
        else: doc.Citation3 = "NONE"
        doc.save()
        return True

    return finalPrediction, shortList, longList




def gen_WL_searchfile(savepath, searchpath, recursive=False, beforeText=100, afterText=50):

    flist = getFileList(searchpath, ext="", recursive=recursive)
    print(len(flist))
    with open(savepath, 'w') as savefile:        

        for f in flist:
            with open(f, 'r') as searchfile:
                searchtext = searchfile.read()
                for pattern in WLsearchPatterns:
                    for matchobj in re.finditer(pattern, searchtext, flags=re.IGNORECASE):
                        if (matchobj.span()[0] - beforeText) < 0: start = 0
                        else: start = matchobj.span()[0] - beforeText
                        if (matchobj.span()[1] + afterText) > len(searchtext) - 1: end = len(searchtext) - 1
                        else: end = matchobj.span()[1] + afterText
                        matchtext = searchtext[start:end].replace(';', '^')
                        cite = matchobj[0].replace(";", '^')
                        savetext = cite + ';' + matchtext + ';' + f
                        savetext = savetext.replace("\n", "") + "\n"
                        savefile.write(savetext)

    return True








def genKeyWords(caseName):

    wordlist = caseName.strip().split()

    # Remove ending commas
    wordlist = [word if not word.endswith(',') else word[:-1] for word in wordlist]
    # Remove backslashes
    wordlist = [word.replace("\\", '') for word in wordlist]
    # Remomve unwanted words
    wordlist = [word for word in wordlist if word.lower() not in findCites_keywords]
    # Remove short words
    wordlist = [word for word in wordlist if len(word) > 3]
    # Remove words that have no letters
    wordlist = [word for word in wordlist if re.search(r"[a-z]", word.lower())]
    # Remove words that contain parentheses
    wordlist = [word for word in wordlist if not (('(' in word) or (')' in word))]
    # Remove duplicates
    wordset = set(wordlist)
    wordlist = list(wordset)

    return wordlist

