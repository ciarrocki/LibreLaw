#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 20:21:39 2019

@author: dan
"""


### Imports

import re

from OPparser_lists import DNPlist, inReFirstCut, inReSecondCut, interestFirstCut, interestSecondCut, IMOfirstCut, IMOsecondCut, partyWordsToRemove
from OPparser_utils import cutWords, cutWords2, addAmpersands, stripPeriods, fixCaseNameCase
from OPparser_text_parties_raw import getRawParties_text





### Main Functions

def getParties_text(front):

    rawParties = getRawParties_text(front)
    fullCaption = rawParties

    if rawParties == '':
        print("Cannot extract raw parties from front.")
        return '', '', fullCaption

    parties = ''
    caseName = ''

    if rawParties.lower().startswith('in re'): 
        parties, caseName = parseInReStyle_text(rawParties)
    elif rawParties.lower().startswith('in the matter of'):
        parties, caseName = parseInReStyle_text(rawParties)
    elif ' v. ' in rawParties:
        parties, caseName = parseVstyle_text(rawParties)
    elif 'COM. v. ' in rawParties: #For certain PA commonwealth cases (very few, maybe delete this?)
        parties, caseName = parseVstyle_text(rawParties)
    elif isEstateStyle_text(rawParties):
        parties, caseName = parseEstateStyle_text(rawParties)
    elif isInterestStyle_text(rawParties):
        parties, caseName = parseInterestStyle_text(rawParties)
    elif isIMOstyle_text(rawParties):
        parties, caseName = parseIMOstyle_text(rawParties)
    else:
        print('Unidentified party list style.  Cannot parse.')
        print('rawParties:', rawParties)
        return parties, caseName, rawParties

    caseName = fixCaseNameCase(caseName)

    return parties, caseName, fullCaption





### Sub Functions

def parseVstyle_text(rawParties):

    #First, change 'v.'s to carrots and deal with breaks
    rawParties = rawParties.replace('<br>v.<br>', ', ^')
    rawParties = rawParties.replace(' v. ', ', ^')
    rawParties = rawParties.replace('<br>\nv.<br>', ', ^')
    rawParties = rawParties.replace(', and<br>\n', ', ')
    rawParties = rawParties.replace('<br>', ', ')
    rawParties = rawParties.replace(' v. ', ', ') #MUST be case sensitive search and replace

    #Second, deal with special "and" party names, e.g., 'oil and gas company'
    rawParties = addAmpersands(rawParties)

    #Third, remove unwanted text    
    rawParties = re.sub(r'appeal of\:', ',', rawParties, flags=re.IGNORECASE) # Need to do this before next step to maintain proper commas between parties

    for word in partyWordsToRemove:
        partyRegex = re.compile(re.escape(word), re.IGNORECASE)
        rawParties = partyRegex.sub('', rawParties)
    rawParties = re.sub(r"NO\.\s\d\d\-\d\d\d", ',', rawParties) # Remove case numbers from PA Superior Court cases (see, e.g., /home/dan/Data/CourtListener/Processed/Pennsylvania/Superior/withCitations/4281696.html)

    rawParties = re.sub(r"_{3,}", " ", rawParties) # Remove lines made of underscores

    # Remove workers compensation appeal board parentheticals (see Pennsylvania/Commonwealth/withCitations/4032662.html)
    rawParties = PAworkersComp(rawParties)

    #Fourth, fix double/triple commas (they could fuck with next step)
    rawParties = rawParties.replace(',,,', ',')
    rawParties = rawParties.replace(',,', ',')

    #Fifth, replace 'and' with commas to separate parties
    rawParties = rawParties.replace(', and ', ', ')
    rawParties = rawParties.replace(' and ', ', ')
    rawParties = rawParties.replace('; And ', ', ')
    rawParties = rawParties.replace(' AND ', ', ')

    #Sixth, replace commas with semi-colons for final separation of parties
    tempPartyList = list(rawParties)
    for i in range(0, len(rawParties) - 2):
        if (rawParties[i] == ',') and (rawParties[i+1] == ' '):
            nextWord = ''
            for j in range(i + 2, len(rawParties)):
                if rawParties[j] == ' ': break
                if rawParties[j] == '<br>': break
                nextWord += rawParties[j]
            if nextWord in DNPlist: continue
            tempPartyList[i] = ';'
            #Convert tempPartyList into string
    rawParties = ''
    for char in tempPartyList: rawParties += char

    #Seventh, formatting and minor fixes
    rawParties = rawParties.replace('; ; ', '; ')
    rawParties = rawParties.replace(';  ; ', '; ')
    rawParties = rawParties.replace(' ;', ';')
    rawParties = rawParties.replace(',^', '; ^')
    rawParties = rawParties.replace('&amp;', '&')
    rawParties = rawParties.replace('  ', ' ')
    #Seventh, if applicable, put the first party after the 'v.' in the second 
    #position (so the two parties used for the name are easily available)
    tempPartyList = rawParties.split(';')
    partyCounter = 0
    afterVpos = -1
    for party in tempPartyList:
        if party.lstrip().startswith('^'):
            afterVpos = partyCounter
            break
        partyCounter += 1

    if (len(tempPartyList) > 1) and (afterVpos > 1):
        temp = tempPartyList[afterVpos]
        del tempPartyList[afterVpos]
        tempPartyList.insert(1, temp)
    #Convert tempPartyList into string
    rawParties = ''
    for element in tempPartyList:
        rawParties += element.strip() + ';'

    #Eighth, final formatting
    rawParties = rawParties.replace(';;;', ';')
    rawParties = rawParties.replace(';;', ';')
    rawParties = rawParties.replace(',;', ';')
    rawParties = rawParties.replace(';.;', ';')
    rawParties = rawParties.replace(';,;', ';')
    rawParties = rawParties.replace('^', '')
    rawParties = rawParties.replace(';/;', ';')
    rawParties = rawParties.replace('; ', ';')
    if rawParties.endswith(';'): rawParties = rawParties[:-1]
    if rawParties.startswith(';'): rawParties = rawParties[1:]
    #Ninth, generate the caseName from the partyList string
    caseName = getCaseNameFromPartyList_text(rawParties)

    #Tenth, strip starting and ending periods
    rawParties = stripPeriods(rawParties)
    caseName = stripPeriods(caseName)
    #Elevent, dedupe party list
    rawParties = deDupe(rawParties)

    return rawParties, caseName



def deDupe(caseName):
    caseNameList = caseName.split(';')
    deDupedList = list(set(caseNameList))
    deDupedString = ";".join(deDupedList)
    return deDupedString




def parseInReStyle_text(rawParties):

    caseName = ''

    #TESTING
    #print("IN RE***************************************\nOriginal:", rawParties)

    #First, make iniital cut (only words that will NOT appear in case name)
    caseName = cutWords2(inReFirstCut, rawParties)
    caseName = removeDates(caseName)

    #Second, make second word cut (for cut down to party list)
    rawParties = cutWords2(inReSecondCut, caseName)

    #Third, minor formatting
    rawParties = rawParties.strip()
    caseName = caseName.strip()
    if rawParties.endswith(' .'): rawParties = rawParties[:-2]
    if rawParties.endswith(','): rawParties = rawParties[:-1]
    if caseName.endswith(', .'): caseName = caseName[:-3]

    #Fourth, strip starting and ending periods
    rawParties = stripPeriods(rawParties)
    caseName = stripPeriods(caseName)

    return rawParties, caseName




def isInterestStyle_text(rawParties):
    if rawParties.lower().startswith('in the interest of') or rawParties.lower().startswith('in interest of') or rawParties.lower().startswith('in int. of'):
        return True
    return False


def parseInterestStyle_text(rawParties):
 
    caseName = ''

    # First, make first cut of words (for caseName)
    rawParties = cutWords(interestFirstCut, rawParties)

    #Second, delete some HTML
    startLoc = rawParties.find('<sup>')
    endLoc = rawParties.find('</sup>')
    if (startLoc > -1) and (endLoc > -1):
        rawParties = rawParties[:startLoc] + rawParties[endLoc + 6:]

    #Third, formatting for caseName
    rawParties = rawParties.replace('&amp;', '&')
    if '<br>\n' in rawParties:
        caseName = rawParties[:rawParties.find('<br>\n')]
    else:
        caseName = rawParties
    if ' appeal of:' in caseName.lower():
        position = caseName.lower().find(' appeal of')
        caseName = caseName[:position]

    #Fourth, some additional formatting
    rawParties = rawParties.replace('<br>\n', ';')    
    rawParties = rawParties.replace(';;', ';')

    #Fifth, make second cut of words (for party list)
    rawParties = cutWords(interestSecondCut, rawParties)

    #Sixth, additional formatting
    rawParties = rawParties.strip()
    if rawParties.endswith(';'): rawParties = rawParties[:-1]
    if rawParties.endswith(', .'): rawParties = rawParties[:-3]
    if rawParties.endswith(', .'): rawParties = rawParties[:-3]
    caseName = caseName.strip()
    if caseName.endswith(';'): caseName = caseName[:-1]
    if caseName.endswith(', '): caseName = caseName[:-2]
    if caseName.endswith(', .'): caseName = caseName[:-3]
    
    caseName = stripPeriods(caseName)
    
    #Seventh, deal with special "and" party names, e.g., 'oil and gas company'
    rawParties = addAmpersands(rawParties)

    #Eighth, replace 'and' with commas to separate parties (also fix double and triple commas)
    rawParties = rawParties.replace(',,,', ',')
    rawParties = rawParties.replace(',,', ',')
    rawParties = rawParties.replace(', and ', ', ')
    rawParties = rawParties.replace(' and ', ', ')
    rawParties = rawParties.replace('; And ', ', ')

    #Ninth, replace commas with semi-colons for final separation of parties
    rawParties = sepParties(rawParties)

    #Tenth, strip periods, leading space, and trailingspace
    rawParties = stripPeriods(rawParties)
    rawParties = stripSpaces(rawParties)

    #Eleventh: some more formatting
    rawParties = rawParties.replace(';;', ';')
    rawParties = rawParties.replace(';.;', ';')

    #Twelvth: de-dupe the party list for exact duplicates
    parties = deDupe(rawParties)

    return parties, caseName



def isEstateStyle_text(rawParties):
    if re.match('^[A-Z][a-z]+\sEstate\.', rawParties): return True
    return False


def parseEstateStyle_text(rawParties):
    #Trim down to caseName
    if rawParties.endswith('.'): caseName = rawParties[:-1]
    else: caseName = rawParties
    #Trim down to parties
    parties = caseName.replace('Estate', '')
    return parties, caseName




def isIMOstyle_text(rawParties):
    if rawParties.startswith("IMO:"): return True
    return False


def parseIMOstyle_text(rawParties):

    caseName = cutWords2(IMOfirstCut, rawParties)
    caseName = removeDates(caseName)
    if caseName.endswith(", "): caseName = caseName[:-2]

    parties = cutWords2(IMOsecondCut, caseName)
    parties = parties.replace(", AND", ",").replace(", and", ",").replace(", And", ",")
    parties = sepParties(parties)
    parties = stripSpaces(parties)

    return parties, caseName




def getCaseNameFromPartyList_text(partyListString):
    caseName = ''
    partyList = partyListString.split(';')
    if len(partyList) < 2: return ''
    caseName = partyList[0] + ' v. ' + partyList[1]
    return caseName




def PAworkersComp(rawParties):
    if "Workers' Compensation Appeal Board" in rawParties:
        rawParties = re.sub(r"\s\([A-Z](\w|\s)+\)", '', rawParties)
    return rawParties




def sepParties(rawParties):
    partyList = list(rawParties)
    for i in range(0, len(rawParties) - 2):
        if (rawParties[i] == ',') and (rawParties[i+1] == ' '):
            nextWord = ''
            for j in range(i + 2, len(rawParties)):
                if rawParties[j] == ' ': break
                if rawParties[j] == '<br>': break
                nextWord += rawParties[j]
            if nextWord in DNPlist: 
                continue
            partyList[i] = ';'
            #Convert partyList back into string
    rawParties = ''
    for char in partyList: rawParties += char    
    return rawParties



def stripSpaces(rawParties):
    tempPartyList = rawParties.split(';')
    rawParties = ''
    for party in tempPartyList:
        rawParties += party.strip() + ';'
    if rawParties.endswith(';'): rawParties = rawParties[:-1]
    if rawParties.endswith(','): rawParties = rawParties[:-1]
    return rawParties


def removeDates(string):
    return re.sub(r"\w{3,9}\s\d{1,2}\,\s(\d\d\d\d|\d\d)", "", string)


