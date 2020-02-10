#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:37:43 2019

@author: dan


Scripts to extract lists of people and organizations from court documents.

Main Functions:

    get_people_orgs_by_ID(docID, database='DE'):
        
        docID: (in) the document ID for which we want people + orgs
        database: the database in which to find the docID
        
        returns three items: (1) a list of people in the document
                             (2) a list of organizations in the document
                             (3) the cleaned version of the text used for 
                                 analysis
"""



import sys
import os
import re

from CiteVista_utils import strip_tags, getDocCites
from CiteVista_patterns import dqList_PeopleOrgs, dqList_phrases_PeopleOrgs

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







def get_people_orgs_by_ID(docID, database="DE"):
    
    text = get_MT_by_ID(docID, database)    
    people, orgs = get_people_orgs_from_text(text)
    
    return people, orgs, text






def get_MT_by_ID(docID, database="DE"):
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

    clean_text = clean_MT(text)

    cites = getDocCites(clean_text)

    full_cites = [getWholeCite(cite, text) for cite in cites]

    processed_text = removeCites(text, full_cites)

    return processed_text





def get_people_orgs_from_text(text):
    """
    Loads and runs spaCy NLP object on the text provided.
    
    returns two lists:
        (1) tuples of people (person, number of appearances)
        (2) tuples of organizations (organization, number of appearances)
    """

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
    orgs = filter_people_orgs(orgs)
    
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



not_end_word = ["v.", 
                "corp.", "co.", "inc.", 'hldgs.',
                "del.", "del.supr.", "del.ch."]



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

        # If any words in dqList_PeopleOrgs is in name, kick it out
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

        # If the name starts with "the "", kick it out
        if pro_text.startswith('the \"'): continue
        if pro_text.startswith('the “'): continue

        # If the name has a large blank space, kick it out
        if "    " in pro_text: continue

        # If the line passed the tests, add it
        newlist.append(p)

    return newlist





def removeCites(text, fullcites):
    newtext = text
    sorted_list_of_cites = sorted(fullcites, key=lambda x: x[1], reverse=True)
    for i in sorted_list_of_cites:
        newtext = newtext[0:i[1]] + newtext[i[2]:]
    return newtext



