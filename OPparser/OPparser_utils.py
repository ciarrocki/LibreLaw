#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 09:34:01 2019

@author: dan
"""


### Imports

import os
import re
from dateutil.parser import parse as parseDate

from OPparser_lists import validEndPeriodWords, sepLinesList, caseNoRE1, caseNoRE2, caseNoRE3, caseNoRE4, caseNoRE5




### Globals

CaseNameCaseList = ["LLC", "LP", "LLP", "SS", "II", "III", "IV", "V", "VI", 
                    "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", 
                    "XVI", "XVII", "XVIII", "XIX", "XX", "CDO"]



### Paths

chromeDriver = "/home/dan/ChromeDriver/chromedriver"
rawDataDir_DEGOV = "/home/dan/Data/DelawareGov/Raw/"
proDataDir_DEGOV = "/home/dan/Data/DelawareGov/Processed/"
rawDataDir_CL = "/home/dan/Data/CourtListener/Raw/Extracted/"
compressedDataDir_CL = "/home/dan/Data/CourtListener/Raw/Compressed/"
proDataDir_CL = "/home/dan/Data/CourtListener/Processed/"



### Data URLs

seed_DEGOV = 'https://courts.delaware.gov/opinions'


seed_DECL = {'del': 'https://www.courtlistener.com/api/bulk-data/opinions/del.tar.gz',
             'delch': 'https://www.courtlistener.com/api/bulk-data/opinions/delch.tar.gz',
             'delsuperct': 'https://www.courtlistener.com/api/bulk-data/opinions/delsuperct.tar.gz',
             'delctcompl': 'https://www.courtlistener.com/api/bulk-data/opinions/delctcompl.tar.gz',
             'delfamct': 'https://www.courtlistener.com/api/bulk-data/opinions/delfamct.tar.gz',
             'deljudct': 'https://www.courtlistener.com/api/bulk-data/opinions/deljudct.tar.gz'}

seed_PACL = {'pa': 'https://www.courtlistener.com/api/bulk-data/opinions/pa.tar.gz',
             'pasuperct': 'https://www.courtlistener.com/api/bulk-data/opinions/pasuperct.tar.gz',
             'pacommwct': 'https://www.courtlistener.com/api/bulk-data/opinions/pacommwct.tar.gz',
             'cjdpa': 'https://www.courtlistener.com/api/bulk-data/opinions/cjdpa.tar.gz'}


seed_USCL = {'scotus':'https://www.courtlistener.com/api/bulk-data/opinions/scotus.tar.gz',
             'ca2':'https://www.courtlistener.com/api/bulk-data/opinions/ca2.tar.gz',
             'ca3':'https://www.courtlistener.com/api/bulk-data/opinions/ca3.tar.gz', 
             'ded':'https://www.courtlistener.com/api/bulk-data/opinions/ded.tar.gz',
             'deb':'https://www.courtlistener.com/api/bulk-data/opinions/deb.tar.gz', 
             'paed':'https://www.courtlistener.com/api/bulk-data/opinions/paed.tar.gz', 
             'pamd':'https://www.courtlistener.com/api/bulk-data/opinions/pamd.tar.gz', 
             'pawd':'https://www.courtlistener.com/api/bulk-data/opinions/pawd.tar.gz', 
             'paeb':'https://www.courtlistener.com/api/bulk-data/opinions/paeb.tar.gz', 
             'pamb':'https://www.courtlistener.com/api/bulk-data/opinions/pamb.tar.gz', 
             'pawb':'https://www.courtlistener.com/api/bulk-data/opinions/pawb.tar.gz',
             'njd':'https://www.courtlistener.com/api/bulk-data/opinions/njd.tar.gz', 
             'njb':'https://www.courtlistener.com/api/bulk-data/opinions/njb.tar.gz',}
#             'nyeb':'https://www.courtlistener.com/api/bulk-data/opinions/nyeb.tar.gz', 
#             'nynb':'https://www.courtlistener.com/api/bulk-data/opinions/nynb.tar.gz', 
#             'nysb':'https://www.courtlistener.com/api/bulk-data/opinions/nysb.tar.gz', 
#             'nywb':'https://www.courtlistener.com/api/bulk-data/opinions/nywb.tar.gz', 
#             'nyed':'https://www.courtlistener.com/api/bulk-data/opinions/nyed.tar.gz', 
#             'nynd':'https://www.courtlistener.com/api/bulk-data/opinions/nynd.tar.gz', 
#             'nysd':'https://www.courtlistener.com/api/bulk-data/opinions/nysd.tar.gz', 
#             'nywd':'https://www.courtlistener.com/api/bulk-data/opinions/nywd.tar.gz',
#             'ctd':'https://www.courtlistener.com/api/bulk-data/opinions/ctd.tar.gz', 
#             'ctb':'https://www.courtlistener.com/api/bulk-data/opinions/ctb.tar.gz',
#             'vtd':'https://www.courtlistener.com/api/bulk-data/opinions/vtd.tar.gz', 
#             'vtb':'https://www.courtlistener.com/api/bulk-data/opinions/vtb.tar.gz'}


### Functions

def fixCaseNameCase(caseName):
    wordlist = caseName.strip().split()
    newlist = []
    for word in wordlist:
        if word.isupper():
            if word not in CaseNameCaseList: 
                newword = getTitle0(word)
                newlist.append(newword)
            else: newlist.append(word)
        else: newlist.append(word)
    newtext = ' '.join(newlist)
    newtext = newtext.replace("In Re", "In re") # AD HOC FIX
    return newtext





def removeCaseNos(text):
    text = caseNoRE3.sub("", text) # Remove case numbers #1 (Del Superior Style) ORDER MATTERS: THIS IS MORE "GREEDY" THAN OTHERS; RUNNING THE OTHERS FIRST WILL LEAVE FRAGMENTS OF CASE NUMBERS THIS ONE WAS MEANT TO CATCH!!!
    text = caseNoRE1.sub("", text) # Remove case numbers #2 (Del Supreme Style)
    text = caseNoRE2.sub("", text) # Remove case numbers #3 (Del Chancery Old Style)
    text = caseNoRE4.sub("", text)
    text = caseNoRE5.sub("", text)
    text = text.strip()
    return text






def getFileList(path, ext='', recursive=False):
    fileList = []
    if not path.endswith('/'): path = path + '/'
    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(ext): fileList.append(str(os.path.join(root, file)))
    else:
        fileList = [path + file for file in os.listdir(path)\
                    if os.path.isfile(os.path.join(path, file)) and file.endswith(ext)]
    return fileList





def numLowerCaseWords(string):
    wordList = string.split()
    numLCwords = 0
    for word in wordList:
        if word.islower(): numLCwords += 1
    return numLCwords





def getTitle0(word):
    newword = word.title()
    if "'" in word:
        pos = word.find("'")
        if len(word) > pos + 1:
            newword = newword[:pos+1] + newword[pos+1].lower() + newword[pos+2:]
    return newword





def addAmpersands(rawParties):
    rawParties = rawParties.replace('Oil and Gas', 'Oil & Gas')
    rawParties = rawParties.replace('Oil and Refining', 'Oil & Refining')
    rawParties = rawParties.replace('Current and Former', 'Current & Former')
    rawParties = rawParties.replace('Health, Education and Welfare', 'Health Education & Welfare')
    rawParties = rawParties.replace("PENSION AND RETIREMENT", "PENSION & RETIREMENT")
    rawParties = rawParties.replace('OFFICERS AND FIREFIGHTERS', 'OFFICERS & FIREFIGHTERS')
    return rawParties





def stripPeriods(partyString):

    newPartyString = ''
    partyList = partyString.split(';')

    for party in partyList:

        removeEndPeriod = False
        removeStartPeriod = False

        if party.endswith('.'):
            removeEndPeriod = True
            for word in validEndPeriodWords:
                if party.lower().endswith(word): removeEndPeriod = False
            if len(partyString) >= 4:
                if (partyString[-3] == '.') and (partyString[-2].isupper()) and (partyString[-4].isupper()):
                    removeEndPeriod = False

        if party.startswith('.'): removeStartPeriod = True

        if removeEndPeriod and removeStartPeriod: newPartyString += party[1:-1] + ';'
        elif removeEndPeriod: newPartyString += party[:-1] + ';'
        elif removeStartPeriod: newPartyString += party[1:] + ';'
        else: newPartyString += party + ';'

    if newPartyString.endswith(';'): newPartyString = newPartyString[:-1]

    # Remove starting and ending spaces from each entry in the party list
    finalPartyList = [party[1:] if party.startswith(' ') else party for party in newPartyString.split(';')]
    finalPartyList = [party[:-1] if party.endswith(' ') else party for party in finalPartyList]
    finalPartyString = ';'.join(finalPartyList)

    return finalPartyString





def replaceCase(replaceDict, word):

    # ONLY works on uppercase, lowercase, and titlecase words
    upperFlag = False
    titleFlag = False
    lowerFlag = False
    if word.isupper(): upperFlag = True
    elif word.istitle(): titleFlag = True
    elif word.islower(): lowerFlag = True
    else:
        return word

    if word.lower() in replaceDict.keys(): newword = replaceDict[word.lower()]
    else: newword = word

    if lowerFlag: return newword
    elif upperFlag: return newword.upper()
    elif titleFlag: return newword[0].upper() + newword[1:] # Fixes cases like "emp't", which would return "Emp'T' if we simply did neword.title()
    else: return word

 



def cutWords(wordList, string):
    for word in wordList:
        searchFlag = True
        while searchFlag == True:
            startPos = string.lower().find(word)
            if startPos > -1: 
                string = string[:startPos] + string[startPos + len(word):]
            else:
                searchFlag = False
    return string





def cutWords2(wordList, string):
    for word in wordList:
        regex = re.compile(re.escape(word), re.IGNORECASE)
        string = regex.sub('', string)
    string = string.strip()
    return string





def isDate(string):    
    try:
        parseDate(string, fuzzy=True).date().isoformat()
        return True
    except:
        return False





def deleteSepLines(pageList):

    if len(pageList) < 2:
        return pageList
    
    else:
        newPageList = []
        for page in pageList:
            if type(page) == int:
                newPageList.append(page)
            else:
                newPage = [line for line in page if (line not in sepLinesList)]
                newPageList.append(newPage)
        return newPageList





#Delete preceding and trailing lines that are just '\n' and nothing else
def delExtraNewlines(lineList):
    lineList = delPrecedingNewlines(lineList)
    lineList = delTrailingNewlines(lineList)
    return lineList

#Recursively delete preceding lines that are just '\n' or spaces and nothing else
def delPrecedingNewlines(lineList):
    if len(lineList) < 1: return lineList
    if lineList[0].strip() == '': return delPrecedingNewlines(lineList[1:])
    else: return lineList

#Recursively delete trailing lines that are just '\n' or spaces and nothing else
def delTrailingNewlines(lineList):
    if len(lineList) < 1: return lineList
    if lineList[-1].strip() == '': return delTrailingNewlines(lineList[:-1])
    else: return lineList





def isTitleCase(string):
    
    wordReplace = {'of':'Of', 'the':'The', 'and':'And', 'a':'A', 'for':'For', 
                   'to':'To', 'on':'On', 'with':'With', 'that':'That', '\n':''}
    wordList = string.split()
    newWordList = []
    for word in wordList:
        if word in wordReplace.keys(): newWordList.append(wordReplace[word])
        else:newWordList.append(word)
    newstring = ' '.join(newWordList)

    return newstring.istitle()



# Significantly more permissive than the last one; used for section-header detection in mainText formatting
def isTitleCase2(string):

    if len(string) == 0: return False
    
    # Remove all numbers and some misc punctuation
    newstring = re.sub('\d+', '', string)
    newstring = newstring.replace(' . ', '')
    if newstring.startswith('.'): newstring = newstring[1:]

    # Remove apostrophe's and quotation marks
    newstring = newstring.replace('’', '').replace('\'', '').replace('\"', '')

    # Remove lowercase section heading characters
    newstring = re.sub(r'^[a-z]\.(\s+[A-Z])', r'\1', newstring) # E.G.: "a. Approval of the Merger"
    newstring = re.sub(r'\([a-z]\)', '', newstring) # Fixes cases like: "Section 1.2(c)"

    # Set of tokens that can be lowercase in titles
    wordSet = {'of', 'the', 'and', 'a', 'an', 'for', 'to', 'on', 'with', 
               'that', 'in', 'is', '\n'}

    # Create list of words; return True if the list is empty (i.e., the 
    # previous operations removed all words)
    wordList = newstring.strip().split()
    if len(wordList) == 0: return True

    # Main Loop: counts number of impermissible lower case words
    lcCounter = 0
    for word in wordList:
        if word[0].isupper(): continue
        if word in wordSet: continue
        lcCounter += 1

    # Compute "Lowercase Quotient", i.e. the ratio of imperissible lower case words to words
    lcQ = lcCounter / len(wordList)

    # Returns True if there are NO impermissible LC words; might need to tune how this works
    return (lcQ == 0)





def flatten(listOfStrings):
    flatVersion = ''
    for line in listOfStrings:
        flatVersion += line
    return flatVersion





def delExcessLineSpaces(text):
    newText = []
    for page in text:
        newPage = delPrecedingLineSpaces(page)
        newPage = delTrailingLineSpaces(newPage)
        newText.append(newPage)
    return newText


def delPrecedingLineSpaces(page):
    if page == []: return page
    if page[0].strip() == '': return delPrecedingLineSpaces(page[1:])
    else: return page


def delTrailingLineSpaces(page):
    if page == []: return page
    if page[-1].strip() == '': return delTrailingLineSpaces(page[:-1])
    else: return page





def getMaxLL(text):
    lineLens = sorted([len(line) for page in text for line in page])
    if len(lineLens) > 350: maxLen = lineLens[int(.99 * len(lineLens))]
    elif len(lineLens) > 0: maxLen = lineLens[int(.98 * len(lineLens))]
    else: maxLen = 0
    return maxLen






def getCtDirFromCLlink(text):

    saveDir = ""
    if "del.tar" in text: saveDir = "/Delaware/Supreme/"
    elif "delch.tar" in text: saveDir = "/Delaware/Chancery/"
    elif "delsuperct.tar" in text: saveDir = "/Delaware/Superior/"
    elif "delctcompl.tar" in text: saveDir = "/Delaware/CommonPleas/"
    elif "delfamct.tar" in text: saveDir = "/Delaware/Family/"
    elif "deljudct.tar" in text: saveDir = "/Delaware/Judicial/"

    elif 'pa.tar' in text: saveDir = "/Pennsylvania/Supreme/"
    elif 'pacommwct.tar' in text: saveDir = "/Pennsylvania/Commonwealth/"
    elif 'pasuperct.tar' in text: saveDir = "/Pennsylvania/Superior/"
    elif 'cjdpa.tar' in text: saveDir = "/Pennsylvania/Judicial/"
    
    elif 'scotus.tar' in text: saveDir = "/Federal/scotus/"
    elif 'ca2' in text: saveDir = "/Federal/ca2/"
    elif 'ca3' in text: saveDir = "/Federal/ca3/"
    elif 'ded' in text: saveDir = "/Federal/ded/"
    elif 'deb' in text: saveDir = "/Federal/deb/"
    elif 'paed' in text: saveDir = "/Federal/paed/"
    elif 'pamd' in text: saveDir = "/Federal/pamd/"
    elif 'pawd' in text: saveDir = "/Federal/pawd/"
    elif 'paeb' in text: saveDir = "/Federal/paeb/"
    elif 'pamb' in text: saveDir = "/Federal/pamb/"
    elif 'pawb' in text: saveDir = "/Federal/pawb/"
    elif 'njd' in text: saveDir = "/Federal/njd/"
    elif 'njb' in text: saveDir = "/Federal/njb/"
    elif 'nyed' in text: saveDir = "/Federal/nyed/"
    elif 'nynd' in text: saveDir = "/Federal/nynd/"
    elif 'nysd' in text: saveDir = "/Federal/nysd/"
    elif 'nywd' in text: saveDir = "/Federal/nywd/"
    elif 'nyeb' in text: saveDir = "/Federal/nyeb/"
    elif 'nynb' in text: saveDir = "/Federal/nynb/"
    elif 'nysb' in text: saveDir = "/Federal/nysb/"
    elif 'nywb' in text: saveDir = "/Federal/nywb/"
    elif 'ctd' in text: saveDir = "/Federal/ctd/"
    elif 'ctb' in text: saveDir = "/Federal/ctb/"
    elif 'vtd' in text: saveDir = "/Federal/vtd/"
    elif 'vtb' in text: saveDir = "/Federal/vtb/"

    else: saveDir = ""
    
    return saveDir



