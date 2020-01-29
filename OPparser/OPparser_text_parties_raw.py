#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 20:28:53 2019

@author: dan
"""


### Imports

import re

from OPparser_utils import delTrailingNewlines, flatten, delPrecedingNewlines, removeCaseNos
from OPparser_lists import endReCaptionList, captionDQlist, PAsuperDelList, stackedCharStartLines, caseNoRE1, caseNoRE2, caseNoRE3





### Main Functions

def getRawParties_text(front):

    rawParties = ''
    
    if isSpecialCharCaption(')', front):
        rawParties = getRawParties_SpecialChar(front, ')')
    elif isSpecialCharCaption(':', front):
        rawParties = getRawParties_SpecialChar(front, ':')    
    elif isSpecialCharCaption('§', front):
        rawParties = getRawParties_SpecialChar(front, '§')
    elif isPAsuperAppeal(front):
        rawParties = getRawParties_PAsuper(front)
    elif isREcaption(front):
        rawParties = getRawParties_RE(front)
    elif isOneLiner(front):
        rawParties = getRawParties_OneLiner(front)
    # The following party methods were added to address opinions from the
    # DelawareGov website; the foregoing parties parsers do not work on the 
    # vast majority of opinions from the DelawareGov website.
    elif isStackedCharCap(')', front):
        rawParties = getRawParties_StackedChar(front, ')')
    elif isStackedCharCap('§', front):
        rawParties = getRawParties_StackedChar(front, '§')
    elif isStackedCharCap(':', front):
        rawParties = getRawParties_StackedChar(front, ':')

    else:
        print("Cannot parse: unidentified caption type.")
        print(front)

    return rawParties





### Sub Functions

def isStackedCharCap(char, front):

    for i, line in enumerate(front):
        line0 = removeCaseNos(line)
        if line0 == char:
            if len(front) > i + 2:
                line1 = removeCaseNos(front[i+1])
                line2 = removeCaseNos(front[i+2])
                if (line1 == char) and ((line2 == char) or (line2 == '')):
                       return True

    return False





def getRawParties_StackedChar(front, char):

    end = getEndLine_StackedChar(front, char)
    start = getStartLine_StackedChar(front, char)
    rawParties = front[start:end]
    rawParties = flatten(rawParties)
    rawParties = rawParties.replace(char, "")
    rawParties = rawParties.replace("\n", " ")
    rawParties = re.sub(r"\s{2,}", " ", rawParties)
    rawParties = removeCaseNos(rawParties)
    rawParties = rawParties.strip()

    return rawParties





def getStartLine_StackedChar(front, char):
    for i, line in enumerate(front):
        for phrase in stackedCharStartLines:
            if line.strip().lower().startswith(phrase):
                if len(front) > i + 2:
                    for phrase2 in stackedCharStartLines: # SOME COURT TITLES AT TOP ARE TWO LINES LONG; NEED TO RETURN the second line + 1, not the first line + 1
                        if front[i+1].strip().lower().startswith(phrase2): return i + 2
                        if front[i+2].strip().lower().startswith(phrase2): return i + 3
                    else: return i + 1
                else: return i + 1
    return 0





def getEndLine_StackedChar(front, char):
    pos = 0
    for i, line in enumerate(front):
        line0 = removeCaseNos(line)
        if line0 == char:
            if len(front) > i + 1:
                line1 = removeCaseNos(front[i+1])
                if line1 == char:
                    if i > pos: pos = i
    return pos





def isREcaption(front):

    if isSpecialCharCaption(')', front): return False
    if isSpecialCharCaption(':', front): return False
    if isSpecialCharCaption('§', front): return False

    for line in front:
        if line.strip().lower().startswith('re:') or line.strip().lower().startswith('re '):
            return True

    return False




def isSpecialCharCaption(char, front):

    lineCounter = 0
    for line in front:
        pos = line.find(char)
        if (pos > 0) and (len(front) >= lineCounter + 2):
            if len(front[lineCounter+1]) >= pos + 1:
                if line[pos] == front[lineCounter + 1][pos]:
                    if not captionDisqualify(line, front[lineCounter + 1]):
                        return True
        lineCounter += 1

    return False



def captionDisqualify(line0, line1):

    for word in captionDQlist:
        if (word in line0.lower()) or (word in line1.lower()):
            return True

    if (('(' in line0) and (')' in line0)) or (('(' in line1) and (')' in line1)):
        return True

    return False



def getRawParties_SpecialChar(front, char):

    rawParties = ''

    lineCounter = 0
    for line in front:
        if char in line:
            break
        lineCounter += 1
    start = lineCounter

    firstMissFlag = False    
    for line in front[start:]:
        if char not in line:
            if firstMissFlag: break
            else: firstMissFlag = True
        lineCounter += 1
    if len(front) > lineCounter + 1:    
        if char not in front[lineCounter]: end = lineCounter - 1
        else: end = lineCounter
    else: end = lineCounter

    for line in front[start:end]:
        prev1 = ''
        prev2 = ''
        for character in line:
            if (character == char) and (not skipChar(prev1, prev2)):
                rawParties += ' '
                break
            else:
                rawParties += character
            prev2 = prev1
            prev1 = character

    rawParties = " ".join(rawParties.split())

    return rawParties



def skipChar(prev1, prev2):
    if (prev1 == 'F') and (prev2 == 'O'): return True
    if (prev1 == 'E') and (prev2 == 'R'): return True
    return False




def getRawParties_RE(front):

    rawParties = ''

    # Delete unwanted text at the BEGINNING of front
    lineCounter = 0
    startPos = 0
    for line in front:
        if line.strip().lower().startswith('re:') or line.strip().lower().startswith('re '):
            startPos = lineCounter
            break
        lineCounter += 1
    rawParties = front[startPos:]

    # Delete unwanted text at the END of front
    endPos = -1
    if len(rawParties) > 1:
        startFlag = False
        for i, line in enumerate(rawParties[1:]):
            if line.strip(): startFlag = True # Addresses cases where there is 
            if (line == '\n') and startFlag: # a "Re:" followed by a blank line ("\n") followed by the relevant text.
                endPos = i
                break
            elif (line == '\n'): continue
            stopFlag = False
            for word in endReCaptionList:
                if line.strip().lower().startswith(word): 
                    endPos = i
                    stopFlag = True
            if stopFlag: break
    if endPos > -1:
        rawParties = rawParties[:endPos + 1]

    #Flatten
    tempParties = ''
    for line in rawParties:
        tempParties += line

    # Some formatting and REMOVAL OF CASE NUMBERS
    rawParties = tempParties.replace('\n', ' ')
    rawParties = rawParties.strip()
    rawParties = re.sub('^[Rr][Ee]\:*\s', '', rawParties) #remove re: text itself
    rawParties = rawParties.strip()
    rawParties = " ".join(rawParties.split())
    rawParties = re.sub('C\.A\.\sNo\.\s\d{3,5}\-[A-Z]{2,4}', '', rawParties)
    rawParties = re.sub('(Consol\.\s)?C\.A\.\sNo\.\s\d{4}\-\d{4}\-\w{2,4}', '', rawParties)
    rawParties = re.sub('Civil\sAction\sNo\.\s\d{3,5}\-[A-Z]{2,4}', '', rawParties)
    rawParties = re.sub('Civil\sAction\sNo\.\s\d{4}\-\s*\d{4}\-[A-Z]{2,3}', '', rawParties)
    rawParties = re.sub('C\.A\.\s\d{4}\-\d{4}\-[A-Z]{2,3}', '', rawParties)
    rawParties = re.sub('C\.A\.\sNo\.\s[A-Z]\d\d[A-Z]\-\d\d\-\d\d\d\s[A-Z]{3}', '', rawParties)
    rawParties = re.sub('Def\.*\sID\#\s\d{5,}(\s+\w+\-*\d+)*', '', rawParties)
    rawParties = re.sub('[A-Z]\d\d[A-Z]\-\d\d\-\d\d\d\s[A-Z]{3}', '', rawParties)
    rawParties = re.sub('ID\s*\#\s*\d{5,}', '', rawParties)
    rawParties = rawParties.strip()
    if rawParties.endswith(','): rawParties = rawParties[:-1]
    if rawParties.endswith(';'): rawParties = rawParties[:-1]
    if rawParties.endswith(', .'): rawParties = rawParties[:-3]

    return rawParties




def isPAsuperAppeal(front):

    if isSpecialCharCaption(')', front): return False
    if isSpecialCharCaption(':', front): return False
    if isSpecialCharCaption('§', front): return False

    maxIndex = len(front) - 1
    lineCounter = 0
    appealTextFlag = False
    superiorCourtFlag = False
    PAflag = False

    for line in front:
        if line.strip().lower().startswith("appeal from the"):
            if lineCounter + 2 <= maxIndex:
                if front[lineCounter + 1].strip().lower().startswith("in the court of common pleas"):
                    appealTextFlag = True                    
        if "in the superior court" in line.lower():
            superiorCourtFlag = True
        if "pennsylvania" in line.lower():
            PAflag = True
        lineCounter += 1

    if appealTextFlag and superiorCourtFlag and PAflag: return True
    else: return False




def getRawParties_PAsuper(front):

    rawParties = ''

    # Delete lines at start and end of front that are not part of the caption
    rawParties = deleteLinesPAsuper(front)

    # Delete certain unwanted text
    rawParties = [line.replace(word, '') for word in PAsuperDelList for line in rawParties]

    # Delete righthand column, i.e., anything at index 47 or above
    rawParties = [line[:47] if len(line) >= 47 else line for line in rawParties]        

    # Flatten parties into a string   
    newRawParties = ''
    for line in rawParties:
        newRawParties += line

    # Some formatting
    newRawParties = newRawParties.strip().replace('\n', ' ')
    newRawParties = " ".join(newRawParties.split())

    return newRawParties




def deleteLinesPAsuper(front):
    
    #Delete unwanted lines at the start
    newFront = []
    startFlag = False
    for line in front:
        if not startFlag:
            if line.strip().startswith('<pre'): continue
            elif line.strip().startswith('</pre'): continue
            elif line.startswith('\n'): continue
            elif line.strip().startswith('NON-PRECEDENTIAL'): continue
            elif line.strip().startswith('NON -PRECEDENTIAL'): continue
            elif line == '': continue
            else:
                startFlag = True
                newFront.append(line)
        else:
            newFront.append(line)

    #Delete unwanted lines at the end
    maxIndex = len(newFront) - 1
    lineCounter = 0
    endPos = -1
    for line in newFront:
        if line.strip().lower().startswith("appeal from the"):
            if lineCounter + 1 <= maxIndex:
                if newFront[lineCounter + 1].strip().lower().startswith("in the court of common pleas"):
                    endPos = lineCounter
                    break
        lineCounter += 1
    if endPos > -1:
        newFront = newFront[:endPos]
    newFront = delTrailingNewlines(newFront)

    return newFront




def isOneLiner(front):
    for i, line in enumerate(front):
        if (' : ' in line) or (' ) ' in line) or (' § ' in line):
            if "c.a. no." in line.lower():
                return True
    return False




def getRawParties_OneLiner(front):
    """ Gets 
    """
    rawParties = ''
    lineNum = -1

    for i, line in enumerate(front):
        if (' : ' in line) or (' ) ' in line) or (' § ' in line):
            if "c.a. no." in line.lower():
                lineNum = i
                break

    if lineNum > -1:
        line = front[lineNum]
        splitPos = max([line.rfind(':'), line.rfind(')'), line.rfind('§')])
        rawParties = line[:splitPos].strip()

    return rawParties






"""
def testCaptionID(path):

    flist = getFileList(path, ext='.html', recursive=False)
    parenCounter = 0
    colonCounter = 0
    sectionCounter = 0
    REcounter = 0
    PAsuperAppealCounter = 0
    noIDcounter = 0
    multiCounter = 0
    noIDlist = []
    parenList = []
    colonList = []
    sectionList = []
    RElist = []
    PAsuperAppealList = []
    multiList = []
    multiFlag = False


    for file in flist:

        opinion = parseFile_WC(file)
        IDflag = False
        multiFlag = False

        if not (isSpecialCharCaption(')', opinion[1]) or isSpecialCharCaption(':', opinion[1]) or isSpecialCharCaption('§', opinion[1]) or isREcaption(opinion[1]) or isPAsuperAppeal(opinion[1])):
            noIDcounter += 1
            noIDlist.append((file, opinion[1]))
            continue

        if isSpecialCharCaption(')', opinion[1]):
            parenCounter += 1
            parenList.append((file, opinion[1]))
            IDflag = True

        if isSpecialCharCaption(':', opinion[1]):
            colonCounter += 1
            colonList.append((file, opinion[1]))
            if IDflag: multiFlag = True
            IDflag = True

        if isSpecialCharCaption('§', opinion[1]):
            sectionCounter += 1
            sectionList.append((file, opinion[1]))
            if IDflag: multiFlag = True
            IDflag = True

        if isREcaption(opinion[1]):
            REcounter += 1
            RElist.append((file, opinion[1]))
            if IDflag: multiFlag = True
            IDflag = True

        if isPAsuperAppeal(opinion[1]):
            PAsuperAppealCounter += 1
            PAsuperAppealList.append((file, opinion[1]))
            if IDflag: multiFlag = True
            IDflag = True

        if multiFlag: 
            multiCounter += 1
            multiList.append((file, opinion[1]))


    print("\nnumber of files:", len(flist))
    print("noIDcounter:", noIDcounter)
    print("parenCounter:", parenCounter)
    print("colonCounter:", colonCounter)
    print("sectionCounter:", sectionCounter)
    print("REcounter:", REcounter)
    print("PAsuperAppealCounter:", PAsuperAppealCounter)
    print("multiple:", multiCounter)

    return noIDlist, parenList, colonList, sectionList, RElist, PAsuperAppealList, multiList
"""
