#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 22:05:55 2019

@author: dan
"""


### Imports/Globals

import re

from OPparser_text_parties_raw import isStackedCharCap
from OPparser_lists import startList0, captionDQlist, captionTextList
from OPparser_utils import numLowerCaseWords, delTrailingNewlines

badCharRE = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)





### Main Functions

def loadLines_text(filePath):

    lineList = []

    with open(filePath, 'rb') as textFile:
        textFile.seek(0)
        for newLine in textFile:
            newLine = newLine.replace(b'\xf3\xa0\x84\x8c', b'') # Very weird character; APPEARS ONLY ONCE: 'Pennsylvania/Superior/withCitations/4368527.html'
            decodedLine = newLine.decode('utf8').replace(r'\xa0', r' ') #Sometimes the reader generates files with "\xa0" instead of normal spaces
            decodedLine = badCharRE.sub("~", decodedLine) # Remove characters that cause problems for mysql (mainly 4+ byte characters, I think?)  NOTE: I ALREADY MADE SURE EVERYTHING IS UTF8mb4
            if "‖" in decodedLine:
                decodedLine = decodedLine.replace("‖", "\"")
                if "―" in decodedLine: decodedLine = decodedLine.replace("―", "\"")
            lineList.append(decodedLine)

    return lineList





def splitBodyFront_text(lineList):

    startPos = -1
    lcBuffer = [[0,0], [0,0], [0,0], [0,0], [0,0]]


    # First, check for autostartlines
    for i, line in enumerate(lineList):
        if autoStartLine(line, i) > 0:
            startPos = autoStartLine(line, i)
            break
        if i > 150: break # stop test after first 150 lines

    # Second, do the lowercase word check
    if startPos < 0:
        for i, line in enumerate(lineList):

            if skipLine_bodyFrontSplitter(line): continue
    
            lcBuffer[4][0] = lcBuffer[3][0]
            lcBuffer[4][1] = lcBuffer[3][1]
            lcBuffer[3][0] = lcBuffer[2][0]
            lcBuffer[3][1] = lcBuffer[2][1]
            lcBuffer[2][0] = lcBuffer[1][0]
            lcBuffer[2][1] = lcBuffer[1][1]
            lcBuffer[1][0] = lcBuffer[0][0]
            lcBuffer[1][1] = lcBuffer[0][1]
            lcBuffer[0][0] = numLowerCaseWords(line)
            lcBuffer[0][1] = i

            if (lcBuffer[0][0] > 2) and (lcBuffer[1][0] > 2) and (lcBuffer[2][0] > 1):
                if not isCaptionText(line, lineList[i - 1], lineList[i - 2]):
                    startPos = lcBuffer[2][1]
                    break

            if (lcBuffer[0][0] > 2) and (lcBuffer[1][0] > 0) and (lcBuffer[2][0] > 2) and (lcBuffer[3][0] > 2):
                if not isCaptionText(line, lineList[i - 1], lineList[i - 2]):
                    startPos = lcBuffer[3][1]
                    break

            if (lcBuffer[0][0] > 5) and (lcBuffer[1][0] > 5):
                if not isCaptionText(line, lineList[i - 1], lineList[i - 2]):
                    startPos = lcBuffer[1][1]
                    break

    # Error handling - returns -1, no front, and everything as body
    if startPos == -1: 
        print("FAIL!")
        return -1, [], lineList

    # Split into body and front using the found start position
    front = lineList[:startPos]
    body = lineList[startPos:]

    return startPos, front, body





def isFormFeed(body):
    
    formFeedCounter = 0

    for line in body:
        if line.startswith('\x0c'): formFeedCounter += 1

    if formFeedCounter == 0: return False
    
    if formFeedCounter >= 1: 
        if (len(body) / formFeedCounter) > 50: return False
        else: return True






def checkLL(lineList):
    bigString = ""
    for line in lineList: bigString += line
    if len(bigString.replace('\x0c', '')) < 10: return False # Trigger if length, minus form feed characters, is less than 10
    return True





def splitPages_FF(body):

    finalBody = []
    newPage = []
    
    for line in body:
        if line.startswith('\x0c'):
            finalBody.append(newPage)
            newPage = []
            newPage.append(line.replace('\x0c', ''))
        else:
            newPage.append(line)
    finalBody.append(newPage)
    
    if len(finalBody[0]) == 0: finalBody = finalBody[1:]
    
    # Check for captions and delete all pages starting with and coming after
    # the new caption.  Added in response to orders attached to opinions
    # (see, e.g, PA common #3132411)
    newCaption = isNewCaption(finalBody)
    if newCaption > -1:
        print("New caption found.  It will be cut from the body.")
        finalBody = finalBody[:newCaption]

    return finalBody





def deletePageHeaders(pageList):
    
    uniqueLines = []
    repeatLines = []
    
    for page in pageList:
        for i, line in enumerate(page):
            #Do not count as a repeat line if line is in bottom half of page
            if len(page) > 10:
                if i / len(page) > .5: continue
            if line == '\n': continue
            if line not in uniqueLines: 
                uniqueLines.append(line)
                continue
            if line.strip().lower().startswith('id'): continue
            if numLowerCaseWords(line.replace('et al.', '')) > 3: continue
            repeatLines.append(line)

    repeatLines = [line for line in repeatLines if not (line.strip().lower().startswith('id.') or line.strip().lower().startswith('(emphasis'))]

    newPage = []
    newDoc = []

    for page in pageList:
        for i, line in enumerate(page):
            #Delete repeat lines
            if line in repeatLines: continue            
            #Delete page lines in headers (i.e., 'page 2' in first 5 lines)
            if (i < 5) and re.match('^page\s\d', line.lower()) and (len(line.strip()) < 20): continue
            newPage.append(line)
        newDoc.append(newPage)
        newPage = []

    return newDoc





def deletePageNumbers(pageList):
    
    # PASS #1:
    transform1 = []
    newPage = []
    for page in pageList:
        for line in page:
            if line.startswith('                       ') and line.strip().isnumeric() and (len(line.strip()) < 5):
                pass
            elif line.startswith('          ') and re.search('page\s\d{1,3}\sof\s\d{1,3}', line.strip().lower()):
                pass            
            elif line.startswith('          ') and re.search('^\-\s*\d{1,3}\s*\-', line.strip()):
                pass
            elif re.search('^\s{35,}\-\d{1,3}\n', line):
                pass
            elif re.search('^Page\s\d+\sof\s\d+\n', line):
                pass
            elif re.search('\[[A-Z]\-\d+\-\d+\]\s+\-\s+\d+', line):
                pass
            elif re.search('\[[A-Z]\-\d+\-\d+\]\s\[', line):
                pass
            elif re.search('\[[A-Z]\-\d+\-\d+\,\s\d+\s[A-Z]{2,3}\s\d+\]', line):
                pass
            elif re.search('\[[A-Z]\-\d+[A-Z]\s\&[A-Z]\-\d+\]', line):
                pass
            elif re.search('\s\-\s\d+\n', line) and re.search('\d{4}\]\s\-', line):
                pass
            else:
                newPage.append(line)
        transform1.append(newPage)
        newPage = []

    # PASS #2: If last non-blank line equals the page number (AND NOTHING ELSE), it is deleted
    transform2 = []
    newPage = []
    for i, page in enumerate(transform1):
        newPage = delTrailingNewlines(page)
        if len(newPage) > 0:
            if newPage[-1].strip().isnumeric():
                lastLine = int(newPage[-1].strip())
                if (lastLine == i) or (lastLine == i + 1) or (lastLine == i + 2) or (lastLine == i + 3): # Some docs start page numbers on first, second, or third page, or others 
                    newPage = newPage[:-1]
        transform2.append(newPage)

    return transform2





def deleteHTML(pageList):

    newDoc = []
    newPage = []
    
    for page in pageList:
        for line in page:
            newLine = line.replace('</pre>', '').replace('</span>', '').replace('</a>', '')
            newLine = re.sub('<pre.*?>', '', newLine)
            newLine = re.sub('<span.*?>', '', newLine)
            newLine = re.sub('<a\shref.*?>', '', newLine)
            newPage.append(newLine)
        newDoc.append(newPage)
        newPage = []

    return newDoc





def deleteMisc(pageList):
    newDoc = []
    for page in pageList:
        newPage = []
        for line in page:
            if line.strip().lower().startswith("efiled") and ("transaction" in line.lower()): continue
            newPage.append(line)
        newDoc.append(newPage)
    return newDoc





### Sub Functions

def autoStartLine(line, lineCounter):
    
    for phrase in startList0:
        if phrase in line.lower(): return lineCounter

    if line.startswith('BY JUDGE') and ('FILED:' in line):
        return lineCounter + 2

    if line.startswith('MEMORANDUM BY') and ('FILED' in line):
        return lineCounter + 2

    if line.startswith('JUSTICE ') and ('DECIDED: ' in line):
        return lineCounter + 1
    
    if ("i. introduction" in line.lower()) or ("i.  introduction" in line.lower()):
        return lineCounter

    if line.strip() == "ORDER": return lineCounter + 1

    return -1





def skipLine_bodyFrontSplitter(line):
    if line == '\n': return True
    if '<pre' in line: return True    
    return False





def isCaptionText(line0, line1, line2):
    if (':' in line0):
        if line0.find(':') == line1.find(':'): return True

    if ('§' in line0):
        if line0.find('§') == line2.find('§'): return True

    if (')' in line0):
        if line0.find(')') == line2.find(')'): return True

    if (')' in line0):
        if (line0.find(')') == line1.find(')')) and (line2 == '\n'): return True

    if ('constituting the Court en Banc' in line0) or ('constituting the Court en Banc' in line1) or ('constituting the Court en Banc' in line2):
        return True

    for word in captionTextList:
        if word in line0: return True

    return False





def isNewCaption(body):

    for i, page in enumerate(body):
    
        if page[0].strip().lower().startswith('in the commonwealth court of pennsylvania'):
            if isSpecialCharCaption1(':', page) or isSpecialCharCaption1(')', page) or isSpecialCharCaption1('§', page):
                return i
        
        if page[0].strip().lower().startswith('in the court of chancery of the state of delaware'):
            if isSpecialCharCaption1(':', page) or isSpecialCharCaption1(')', page) or isSpecialCharCaption1('§', page):
                return i
        
        for line in page:
            if line.startswith(' ' * 20) and line.strip().startswith("ORPHANS' COURT DIVISION"): return i
            if line.startswith(' ' * 5) and line.strip().startswith('IN THE COURT OF COMMON'): return i
            if line.startswith(' ' * 10) and line.strip().startswith('THE COURT OF COMMON PLEAS OF'): return i
            if line.startswith(' ' * 10) and line.strip().endswith('PLEAS OF PHILADELPHIA COUNTY'): return i

        if isStackedCharCap(")", page): return i
        if isStackedCharCap(":", page): return i
        if isStackedCharCap("§", page): return i
    
    return -1





def isSpecialCharCaption1(char, front):
    for i, line in enumerate(front):
        pos = line.find(char)
        if (pos > 0) and (len(front) >= i + 2):
            if len(front[i+1]) >= pos + 1:
                if line[pos] == front[i + 1][pos]:
                    if not captionDisqualify(line, front[i + 1]):
                        return True
    return False





def captionDisqualify(line0, line1):

    for word in captionDQlist:
        if (word in line0.lower()) or (word in line1.lower()):
            return True

    if (('(' in line0) and (')' in line0)) or (('(' in line1) and (')' in line1)):
        return True

    return False




def deleteEmptyEndPages(body):
    if len(body) == 0: return body
    if body[-1] == ['']: return deleteEmptyEndPages(body[:-1])
    else: return body

