#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 20:32:22 2019

@author: dan
"""


### Imports

import re

from OPparser_utils import fixCaseNameCase, addAmpersands, stripPeriods, cutWords
from OPparser_lists import DNPlist, partyWordsToRemove, inReFirstCut, inReSecondCut, interestFirstCut, interestSecondCut



### Main Functions

def getRawParties_LB(front):
    
    rawParties = ''

    start = front.find('<center><h1>') + 12
    end = front.find('</h1></center>')

    if (start > 0) and (end > start):
        rawParties = front[start:end]

    return rawParties




def getParties_LB(rawParties):

    parties = ''
    caseName = ''

    if rawParties.lower().startswith('in re'): 
        parties, caseName = parseInReStyle_LB(rawParties)

    elif rawParties.lower().startswith('in the matter of'):
        parties, caseName = parseInReStyle_LB(rawParties)

    elif 'v.<br>' in rawParties:
        parties, caseName = parseVstyle_LB(rawParties)
        
    elif 'COM. v. ' in rawParties: #For certain PA commonwealth cases (very few, maybe delete this?)
        parties, caseName = parseVstyle_LB(rawParties)

    elif isEstateStyle(rawParties):
        parties, caseName = parseEstateStyle(rawParties)

    elif rawParties.lower().startswith('in the interest of') or rawParties.lower().startswith('in interest of') or rawParties.lower().startswith('in int. of'):
        parties, caseName = parseInterestStyle_LB(rawParties)

    elif 'v. ' in rawParties: # Must come toward or at the end
        parties, caseName = parseVstyle_LB(rawParties)

    else:
        print('Unidentified party list style.  Cannot parse.')
        print('rawParties:', rawParties)
        return parties, caseName

    caseName = fixCaseNameCase(caseName)

    return parties, caseName



### Sub Functions

def parseVstyle_LB(rawParties):

    #TESTING
    #print("-----------------------------------------------\nOriginal:", rawParties)

    #First, change 'v.'s to carrots and deal with breaks
    rawParties = rawParties.replace('<br>v.<br>', ', ^')
    rawParties = rawParties.replace('<br>\nv.<br>', ', ^')
    rawParties = rawParties.replace(', and<br>\n', ', ')
    rawParties = rawParties.replace('<br>', ', ')
    #   NEW ADDITION!!!!!!!!!!!!!!!!!
    #   NEW ADDITION!!!!!!!!!!!!!!!!!
    rawParties = rawParties.replace(' v. ', ', ') #MUST be case sensitive search and replace

    #Second, deal with special "and" party names, e.g., 'oil and gas company'
    rawParties = addAmpersands(rawParties)

    #Third, remove unwanted text    
    for word in partyWordsToRemove:
        partyRegex = re.compile(re.escape(word), re.IGNORECASE)
        rawParties = partyRegex.sub('', rawParties)

    #Fourth, fix double/triple commas (they could fuck with next step)
    rawParties = rawParties.replace(',,,', ',')
    rawParties = rawParties.replace(',,', ',')

    #Fifth, replace 'and' with commas to separate parties
    rawParties = rawParties.replace(', and ', ', ')
    rawParties = rawParties.replace(' and ', ', ')
    rawParties = rawParties.replace('; And ', ', ')

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
    rawParties = rawParties.replace(';;', ';')
    rawParties = rawParties.replace(',;', ';')
    rawParties = rawParties.replace(';.;', ';')
    rawParties = rawParties.replace(';,;', ';')
    rawParties = rawParties.replace('^', '')
    if rawParties.endswith(';'): rawParties = rawParties[:-1]

    #Ninth, generate the caseName from the partyList string
    caseName = getCaseNameFromPartyList_LB(rawParties)

    #Tenth, strip starting and ending periods
    rawParties = stripPeriods(rawParties)
    caseName = stripPeriods(caseName)

    #TESTING
    #print("\nCase Name:", caseName)
    #print("\nParty List:", rawParties)

    return rawParties, caseName




def parseInReStyle_LB(rawParties):

    caseName = ''

    #TESTING
    #print("IN RE***************************************\nOriginal:", rawParties)

    #First, make iniital cut (only words that will NOT appear in case name)
    for word in inReFirstCut:
        rawParties = rawParties.replace(word, '')
    caseName = rawParties.strip()

    #Second, make second word cut (for cut down to party list)
    for word in inReSecondCut:
        rawParties = rawParties.replace(word, '')

    #Third, minor formatting
    rawParties = rawParties.strip()
    caseName = caseName.strip()
    if rawParties.endswith(' .'): rawParties = rawParties[:-2]
    if rawParties.endswith(','): rawParties = rawParties[:-1]
    if caseName.endswith(', .'): caseName = caseName[:-3]
    
    #Fourth, strip starting and ending periods
    rawParties = stripPeriods(rawParties)
    caseName = stripPeriods(caseName)

    #TESTING
    #print('\nCase Name:', caseName)
    #print("\nParty List:", rawParties)

    return rawParties, caseName




def parseInterestStyle_LB(rawParties):
 
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
    tempPartyList = list(rawParties)
    for i in range(0, len(rawParties) - 2):
        if (rawParties[i] == ',') and (rawParties[i+1] == ' '):
            nextWord = ''
            for j in range(i + 2, len(rawParties)):
                if rawParties[j] == ' ': break
                if rawParties[j] == '<br>': break
                nextWord += rawParties[j]
            if nextWord in DNPlist: 
                continue
            tempPartyList[i] = ';'
            #Convert tempPartyList into string
    rawParties = ''
    for char in tempPartyList: rawParties += char    

    #Tenth, strip periods
    rawParties = stripPeriods(rawParties)

    #Eleventh: strip extra leading and trailing space
    tempPartyList = rawParties.split(';')
    rawParties = ''
    for party in tempPartyList:
        rawParties += party.strip() + ';'
    if rawParties.endswith(';'): rawParties = rawParties[:-1]

    #Twelvth: some more formatting
    rawParties = rawParties.replace(';;', ';')
    rawParties = rawParties.replace(';.;', ';')

    #Thirteenth: eliminate duplicates
    #de-dupe!
    #See 6, 7, 


    parties = rawParties

    return parties, caseName




def isEstateStyle(rawParties):
    if re.match('^[A-Z][a-z]+\sEstate\.', rawParties) != None: return True
    return False




def parseEstateStyle(rawParties):
    #Trim down to caseName
    if rawParties.endswith('.'): caseName = rawParties[:-1]
    else: caseName = rawParties
    #Trim down to parties
    parties = caseName.replace('Estate', '')
    return parties, caseName




def getCaseNameFromPartyList_LB(partyListString):    
    caseName = ''
    partyList = partyListString.split(';')
    if len(partyList) < 1: return ''
    caseName = partyList[0] + ' v. ' + partyList[1]
    return caseName

