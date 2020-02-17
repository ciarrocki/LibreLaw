#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:37:43 2019

@author: dan


Scripts to extract lists of people and organizations from court documents.

Main Functions:


    get_people_orgs_batch(court, jx, model, write=True, overwrite=False):
        
        Gets the people and orgs from opinions for an entire court at a time.
        Options allow saving to the database.
        
        court:  (str)   Name of the court (official?)
        jx:     (str)   Name of the jurisdiction
        model:  (str)   "Large" (default), "Medium", or "Small"; the spaCy model
                        used for NER; soon to add custom model!
        write:  (bool)  True (default) will write the people and organizations 
                        to the database
        overwrite:      False (default) will not write people or organizations
                        to database if either field is already populated.


    get_people_orgs_by_ID(docID, database='DE'):

        Gets the people and organizations for a single document.
        
        docID: (int) the document ID for which we want people + orgs
        database: (str) the database in which to find the docID
        
        returns three items: (1) a list of people in the document
                             (2) a list of organizations in the document
                             (3) the cleaned version of the text used for 
                                 analysis
"""



import sys
import os
import re
import json

from CiteVista_utils import strip_tags, getDocCites
from CiteVista_patterns import dqList_PeopleOrgs, dqList_phrases_PeopleOrgs,\
    not_end_word

import en_core_web_sm, en_core_web_md, en_core_web_lg  # Part of spacy - MIT license


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc
from Federal.models import UScourtDoc




def get_people_orgs_batch(court="Chancery", jx="Delaware", model="large", 
                          write=True, overwrite=False):
    """Gets the people and orgs from opinions for an entire court at a time.
        Options allow saving to the database."""

    bigDict = {}

    db, ct = check_court_jx(court, jx)
    if not db: return
    docs = db.objects.filter(Court__exact=ct)
    print("Total records:", len(docs))

    print("Done: ", end="")

    for i, doc in enumerate(docs):

        if (i % 10 == 0): print(i, ". . . ", end="")

        #INITIAL CONDITION: IF OVERWRITE IS NOT SET
        if write and (not overwrite):
            if not ((doc.People == None) or (doc.People == "")) and\
                   ((doc.Organizations == None) or (doc.Organizations == "")):
                continue

        text = doc.MainText
        clean_text = clean_MT(text)
        cites = getDocCites(clean_text)
        full_cites = [getWholeCite(cite, clean_text) for cite in cites]
        processed_text = removeCites(clean_text, full_cites)

        nlp = en_core_web_lg.load()
        people, orgs = people_orgs_batchNLP(processed_text, nlp)
        people = [p for p, _ in people]
        orgs = [o for o, _ in orgs]
        docID = doc.id

        if write:
            doc.People = json.dumps(people)
            doc.Organizations = json.dumps(orgs)
            doc.save()

        newDict = {"people":people, "orgs":orgs}
        bigDict[docID] = newDict

    print("Done")
    return bigDict




def people_orgs_batchNLP(text, nlp):
    
    doc = nlp(text)
    orgs = [x.text for x in doc.ents if x.label_ == 'ORG']
    people = [x.text for x in doc.ents if x.label_ == 'PERSON']

    # Step 3: Process and filter the list of organizations
    orgdict = dict()
    for item in orgs:
        if item in orgdict.keys(): orgdict[item] += 1
        else: orgdict[item] = 1
    orgs = list(orgdict.items())
    orgs.sort(key = lambda x: x[1], reverse=True)
    orgs = filter_people_orgs(orgs)

    # Step 4: Process and filter the list of people
    peopledict = dict()
    for item in people:
        if item in peopledict.keys(): peopledict[item] += 1
        else: peopledict[item] = 1
    people = list(peopledict.items())
    people.sort(key = lambda x: x[1], reverse=True)    
    people = filter_people_orgs(people)

    return people, orgs




def check_court_jx(court, jx):

    procourt = court.lower().strip()
    projx = jx.lower().strip()

    if (projx == "de") or (projx == "delaware"):
        db = DEcourtDoc
        if procourt == "chancery": return db, "Court of Chancery"
        if procourt == "supreme": return db, "Supreme Court"
        if procourt == "superior": return db, "Superior Court"
        if procourt == "common pleas": return db, "Court of Common Pleas"
        if procourt == "family": return db, "Family Court"
        print("Invalid court.")
        return ""
    
    if (projx == "pa") or (projx == "pennsylvania"):
        db = PAcourtDoc
        if procourt == "supreme": return db, "Supreme Court"
        if procourt == "commonwealth": return db, "Commonwealth Court"
        if procourt == "superior": return db, "Superior Court"
        print("Invalid court.")
    
    if (projx == "us") or (projx == "federal"):
        db = UScourtDoc
        if procourt == "supreme": return db, "Supreme Court"
        if procourt == "third circuit": return db, "Third Circuit"
        if procourt == "second circuit": return db, "Second Circuit"
        if procourt == "ddel": return db, "District of Delaware"
        if procourt == "dnj": return db, "District of New Jersey"
        if procourt == "edpa": return db, "Eastern District of Pennsylvania"
        if procourt == "mdpa": return db, "Middle District of Pennsylvania"
        if procourt == "wdpa": return db, "Western District of Pennsylvania"

    print("Invalid jurisdiction.")
    return ""



def get_people_orgs_by_ID(docID, database="DE", model="large"):
    """Gets the people and organizations for a single document (by docID)"""

    text = get_MT_by_ID(docID, database)    
    people, orgs = get_people_orgs_from_text(text, model)

    return people, orgs, text






def get_MT_by_ID(docID, database="DE"):
    """
    Gets and returns the main text from a court document in the database.
    The main text is cleaned of html tags and citations.

    docID: the docID number of hte document for which we want to get the 
    clean MT
    """

    # Step 1: Get the text from the document
    if database.lower() == 'de': doc = DEcourtDoc.objects.get(pk=docID)
    elif database.lower() == 'pa': doc = PAcourtDoc.objects.get(pk=docID)
    else:
        print("Invalid database.")
        return ""
    text = doc.MainText

    # Step 2: Remove HTML and footnote anchors
    clean_text = clean_MT(text)

    # Step 3: get short citations (i.e., 256 A.2d 789)
    cites = getDocCites(clean_text)

    # Step 4: Get the full citations and remove them from the text
    full_cites = [getWholeCite(cite, clean_text) for cite in cites]
    processed_text = removeCites(clean_text, full_cites)

    return processed_text





def get_people_orgs_from_text(text, model="large"):
    """
    Loads and runs spaCy NLP object on the text provided.
    
    returns two lists:
        (1) tuples of people (person, number of appearances)
        (2) tuples of organizations (organization, number of appearances)
    """

    # Step 1: Check model input and load nlp object
    if model.lower() == "large": nlp = en_core_web_lg.load()
    elif model.lower() == "medium": nlp = en_core_web_md.load()
    elif model.lower() == "small": nlp = en_core_web_sm.load()
    else:
        print("Invalid NLP model.")
        return [], []
    
    # Step 2: Process the text using spaCy and get list of people and 
    #         orgnization objects
    doc = nlp(text)
    orgs = [x.text for x in doc.ents if x.label_ == 'ORG']
    people = [x.text for x in doc.ents if x.label_ == 'PERSON']
    #pprint([(x.text, x.label_) for x in doc.ents])

    # Step 3: Process and filter the list of organizations
    orgdict = dict()
    for item in orgs:
        if item in orgdict.keys(): orgdict[item] += 1
        else: orgdict[item] = 1
    orgs = list(orgdict.items())
    orgs.sort(key = lambda x: x[1], reverse=True)
    orgs = filter_people_orgs(orgs)
    
    # Step 4: Process and filter the list of people
    peopledict = dict()
    for item in people:
        if item in peopledict.keys(): peopledict[item] += 1
        else: peopledict[item] = 1
    people = list(peopledict.items())
    people.sort(key = lambda x: x[1], reverse=True)    
    people = filter_people_orgs(people)

    return people, orgs





def getWholeCite(citeMatch, text):
    """
    Returns entire cite based on match object passed.
    """

    startPosition = citeMatch.span()[0] - 1000 if citeMatch.span()[0] > 1000 else 0
    endPosition = citeMatch.span()[1] + 1000 if citeMatch.span()[0] + 1000 < len(text) else len(text) - 1
    
    #print("\n", text[citeMatch.span()[0] - 200:citeMatch.span()[1] + 200])    
    
    # Get the words that belong to the cite before the pincite (i.e., "255 A.3d 665")
    beforeText = text[startPosition:citeMatch.span()[0]]
    beforeWords = beforeText.split()
    beforeWords.reverse()
    
    lowercase_flag = False
    citeWords_before = []
    for word in beforeWords:
        if stopWord(word): break

        # If this is the second consecutive lowercase word, remove the previous
        # word from the list and end the loop
        if word[0].islower():
            if lowercase_flag:
                citeWords_before.pop()
                break
            else: lowercase_flag = True
        else: lowercase_flag = False

        citeWords_before.append(word)
    citeWords_before.reverse()

    # Get the words that come after the cite after the pincite (i.e., "255 A.3d 665")
    afterText = text[citeMatch.span()[1]:endPosition]
    afterWords = afterText.split()
    citeWords_after = []
    openParen = False
    for word in afterWords:
        
        # Four digits (i.e., year)
        if re.search("\d{4}", word):
            citeWords_after.append(word)
            break

        # Set openParen flag    
        if word.find("(") >= 0: openParen = True
    
        # Word starts with upper case letter
        if re.search("^[A-Z]", word):
            if openParen and (word.find(")") < 0): continue        
            break
        citeWords_after.append(word)

    # Make the final cite text
    citeString_before = " ".join(citeWords_before)
    citeString_after = " ".join(citeWords_after)
    cite_text =  citeString_before + " " + citeMatch.group() + " " + citeString_after

    # Get the start and end of the string
    start = 0
    end = 0

    start_of_cite = text.find(citeString_before)
    if start_of_cite > 0: 
        start = start_of_cite
        end = start_of_cite + len(cite_text)

    return cite_text, start, end





def stopWord(word):
    
    if word.endswith(".") or word.endswith(".\"") or word.endswith("?") or word.endswith("?\""): 
        if word.lower() in not_end_word: return False
        return True
    return False




def getN(citeMatch, text, n=10):
    """
    Returns n words before and after the provided cite.
    For testing.
    """

    startPosition = citeMatch.span()[0] - 1000 if citeMatch.span()[0] > 1000 else 0
    endPosition = citeMatch.span()[1] + 1000 if citeMatch.span()[0] + 1000 < len(text) else len(text) - 1

    beforeList = text[startPosition:citeMatch.span()[0]].split()    
    beforeList.reverse()        
    beforeWords = beforeList[:n]
    beforeWords.reverse()
    
    afterList = text[citeMatch.span()[1]:endPosition].split()
    afterWords = afterList[:n]
    
    return beforeWords, afterWords




def clean_MT(text):
    """
    Cleans text by removing:
        (1) All footnote anchors and their corresponding html tags
        
        (2) All html tags
        
    Used to prepare opinions for for NLP.

    """

    # (1) Remove footnote anchors
    newtext = re.sub(r"\<a\shref\=\#FNnumber.*?\<\/a\>", "", text)
    
    # (2) Remove HTML tags                 
    newtext = strip_tags(newtext)

    return newtext    
    




def filter_people_orgs(plist):
    """
    Removes unwanted items from lists of people and organizations.
    Input is a list of tuples in which first item is the person/organization
    and the second item is the number of times that person/organization
    appears in the text.

    plist: List of (people/organization, #appearances) tuples (e.g., ('Kock', 4))
    
    returns: a cleaned list of (people/organization, #) tuples
    """
    newlist = []

    for p in plist:
        
        pro_text = p[0].lower().replace("  ", " ")

        # If the name has less than 3 real characters, kick it out
        c = 0
        for character in pro_text:
            if character.isalpha(): c += 1 
        if c < 2: continue

        # If any words in dqList_PeopleOrgs is in the name, kick it out
        fail = False
        for DQword in dqList_PeopleOrgs:
            if DQword in pro_text:
                fail = True
                break
        if fail: continue

        # If the entire name equals a DQ phrase, kick it out
        fail = False
        for DQphrase in dqList_phrases_PeopleOrgs: 
            if DQphrase == pro_text: 
                fail = True
                break
        if fail: continue
    
        # If the name looks like a WL cite, kick it out
        if re.search("wl\s\d{3,}", pro_text): continue

        #
        if pro_text.startswith("del. "): continue

        # If the name starts with "the "", kick it out
        if pro_text.startswith('the \"'): continue
        if pro_text.startswith('the “'): continue

        # If the name has a large blank space, kick it out
        if "    " in pro_text: continue

        # If the line passed the tests, add it to the list
        newlist.append(p)

    return newlist





def removeCites(text, fullcites):
    newtext = text
    sorted_list_of_cites = sorted(fullcites, key=lambda x: x[1], reverse=True)
    for i in sorted_list_of_cites:
        newtext = newtext[0:i[1]] + newtext[i[2]:]
    return newtext



