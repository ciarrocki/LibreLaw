#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 06:35:10 2019

@author: dan
"""


### Imports

import re

from OPparser_utils import delExtraNewlines, isTitleCase, numLowerCaseWords, deleteSepLines, delTrailingNewlines, getMaxLL




### Main Functions

def splitFootnotes(pageList, verbose=1):
    
    FNcounter = 0
    FNflag = False
    footnotes = [(0,0)]
    bodyText = []
    newFN = []
    newPage = []
    revisedPageList = []
    spacingInfo = getLineSpacing(pageList)
    maxLL = getMaxLL(pageList)
    turnOffRunOverDetector = hasUnreadableSpacing(pageList)

    for page in pageList:
        newPage = []
        for line in page:
            newPage.append(line.replace('Â¹', '1'))
        revisedPageList.append(newPage)

    newPage = []
    for pCounter, page in enumerate(revisedPageList):
    
        ### CHECK FOR RUNOVER FOOTNOTES
        # Only check for runovers if the previous page ended with a footnote
        if (FNflag == True) and (not turnOffRunOverDetector): 
            # Runover Test #1: Based strictly on whether current page looks like a runover 
            # in itself; requires two spaces before footnotes, which is common in CLWC, 
            # but almost entirely absent from DETX
            runoverLine1 = getRunoverLine1(page, FNcounter, spacingInfo)
            if (runoverLine1 > 0) and (verbose > 0):
                print("\nRunover Detector #1: FN:", FNcounter, "page", pCounter, "line", runoverLine1)
                print("Runover Start Line:", page[runoverLine1].strip())
            # Runover Test #2: Get risk score based on last line of previous page, 
            # then use loose test to get runover start line; developed for DETX files, 
            # which do not have two spaces before footnotes
            runoverRisk = getRunoverRisk(revisedPageList[pCounter - 1], maxLL)
            if runoverRisk > 25: # THRESHOLD runover risk score
                runoverLine2 = getRunoverLine2(page, FNcounter, spacingInfo)
                if verbose > 0:
                    print("\nRunover Detecter #2: FN", FNcounter, "page", pCounter, "line", runoverLine2, "risk", runoverRisk)
                    print("Runover Start Line:", end=' ')
                    if runoverLine2 >= 0: print(page[runoverLine2].strip())
                    else: print()
            else: runoverLine2 = -1
            runover = runoverLine1 if runoverLine1 > runoverLine2 else runoverLine2 # Take the GREATER of runOverLine1 and runOverLine2
        else: runover = -1


        if (FNflag == True) and (runover < 0):
            footnotes.append( (newFN, pCounter) )
            newFN = []
            FNflag = False
        else:
            FNflag = False


        for lineCounter, line in enumerate(page):
            
            if (runover > 0) and (lineCounter == runover):
                FNflag = True
                newFN.append(line)
                lineCounter += 1
                continue

            if len(line.strip()) > 0:
                if line.strip()[0].isnumeric():
                    if re.search('^\d+', line.strip()):
                        num = int(re.search('^\d+', line.strip()).group())                    
                        if num == FNcounter + 1:
                            if (not isSectionHeader(line)) and FNlineSpacing(page, lineCounter, FNcounter):
                                if not isNotFN(line):
                                    if FNflag == True: footnotes.append( (newFN, pCounter + 1) )
                                    FNflag = True
                                    FNcounter += 1
                                    newFN = []
                                    newFN.append(line)
                                    lineCounter += 1
                                    continue

            if FNflag: newFN.append(line)
            else: newPage.append(line)
            lineCounter += 1

        bodyText.append(newPage)
        newPage = []

    #Append final footnote to list if needed
    if FNflag: footnotes.append( (newFN, len(revisedPageList)) )

    footnotes[0] = (len(footnotes) - 1), 0

    #Fix for when last page is simply an empty string ('')
    if len(bodyText) > 0: 
        if bodyText[-1] == ['']: bodyText = bodyText[:-1]

    #Delete lines that separate footnotes (when present)
    #These might be useful for other purposes; consider deleting them later
    #(or actually using them!)
    footnotes = deleteSepLines(footnotes)

    return bodyText, footnotes





### Sub Functions

def getRunoverRisk(page, maxLL):

    # Initialize
    riskScore = 0
    proPage = delTrailingNewlines(page)
    if len(proPage) <= 0: return 0
    lastLine = proPage[-1].strip()
    lastLine2 = re.sub(r"\s$", "", proPage[-1]) # Need a version that is NOT stripped at beginning (but IS stripped at the end)

    # Calculate runover risk score
    if not re.search(r"((\.)|(\.(\"|\'|\”))|(\?))$", lastLine): riskScore += 100 # If line does not end with a period, period quote, or question mark
    if len(lastLine2) > (maxLL * 0.85): riskScore += 25 # If line is close to max line length

    return riskScore





def getRunoverLine1(page, FNcounter, spacingInfo):

    lineBuffer = ['', '', '', '', '']
    lineCounter = 0 # This is not a simple counter; it does not count every line at the beginning and does not reset between the two loops below
    startFlag = False
    newDoc = []


    for line in page:
        if startFlag: newDoc.append(line)
        else:
            if line == '\n': 
                lineCounter += 1
                continue
            else:
                startFlag = True
                newDoc.append(line)
    
    offset = lineCounter
    
    startLine = -1
    for line in newDoc:

        lineBuffer[4] = lineBuffer[3]
        lineBuffer[3] = lineBuffer[2]
        lineBuffer[2] = lineBuffer[1]
        lineBuffer[1] = lineBuffer[0]
        lineBuffer[0] = line

        # AUTO STOP IF LINE IS THE NEXT FOOTNOTE
        if nextFNline(lineBuffer[0], FNcounter): break

        # TEST #1
        if autoRunover(lineBuffer[1], lineBuffer[0]):
            return lineCounter
        
        # TEST #2: Standard line analysis
        if (lineBuffer[1] == '\n') and (lineBuffer[2] == '\n'):#                #1: Line preceded by two '\n' lines  
            if not nextFNline(lineBuffer[0], FNcounter):#                       #2: Is not simply the next FN
                if len(re.findall('[a-z]', lineBuffer[0].lower())) > 3:#        #3: Has more than three a-z characters
                    if not isSectionStart(lineBuffer[0]):#                      #4: Is not a "SectionStart"
                        if runoverLineSpacing(page, lineCounter, spacingInfo):# #5: Spacing is consistent with runover FN
                            if not stopRunoverDetector(page, lineCounter):#     #6: Final check (???)
                                startLine = lineCounter
                                break

        # TEST #3: NEW SENSITIVE TEST: For footnotes without two '\n' lines before them
        #rt3 = runoverTest3(lineBuffer, FNcounter, page, lineCounter, spacingInfo)
        #if rt3 > 0: 
        #    startLine = rt3
        #    break

        # TEST #4:
        strippedLine = lineBuffer[0].strip().lower()
        if strippedLine.startswith('(footnote continued)') or strippedLine.startswith('(continued)'):
            startLine = lineCounter
            break

        lineCounter += 1

    # Give final say to any line starts with '(footnote continued)'
    for i, line in enumerate(newDoc):
        if line.lower().startswith('(footnote continued)'):
            startLine = i + offset
            break

    return startLine





def getRunoverLine2(page, FNcounter, spacingInfo):

    runOverLine = -1
    lineBuffer = ['', '', '', '', '']
    for i, line in enumerate(page):

        lineBuffer[4] = lineBuffer[3]
        lineBuffer[3] = lineBuffer[2]
        lineBuffer[2] = lineBuffer[1]
        lineBuffer[1] = lineBuffer[0]
        lineBuffer[0] = line

        if nextFNline(lineBuffer[1], FNcounter): break # Break search for runover when next footnote is found

        if lineBuffer[2] == '\n':# Find a line that is blank
            if colonCheck(lineBuffer[2], lineBuffer[3], lineBuffer[4]):
                if (len(lineBuffer[0]) > 5) and (len(lineBuffer[1]) > 40): # Two lines after the blank line are substantial/real
                    if (spacingInfo[0][2] > 0.4) and (spacingInfo[1][2] < 0.15): # Maintext is single-spaced and footnotes are not    
                        if runoverDoubleSpacing(page, i - 1, spacingInfo): # Spacing is consistent with runover line spacing (now means, primarily, not an indented block)
                            if not isSectionStart(lineBuffer[1]):
                                if not stopRunoverDetector(page, i):
                                    if i - 1 > runOverLine: runOverLine = i - 1

    return runOverLine





def getLineSpacing(pageList):

    # FIRST, split footnotes and bodytext without regard to runovers
    FNcounter = 0
    FNflag = False
    footnotes = [0]
    bodyText = []
    newFN = []
    newPage = []

    for page in pageList:
    
        for line in page:
    
            if len(line.strip()) > 0:
                if line.strip()[0].isnumeric():
                    if re.search('^\d+', line.strip()):
                        num = int(re.search('^\d+', line.strip()).group())                    
                        if num == FNcounter + 1:
                            if not isSectionHeader(line):
                                if not isNotFN(line):
                                    if FNflag == True: footnotes.append(newFN)
                                    FNflag = True
                                    FNcounter += 1
                                    newFN = []
                                    newFN.append(line)
                                    continue
    
            if FNflag: newFN.append(line)
            else: newPage.append(line)
        
        bodyText.append(newPage)
        newPage = []
        FNflag = False


    # SECOND, delete trailing and preceding lines in each page and footnote
    #         that are simply '\n' and nothing more
    bodyText = [delExtraNewlines(page) for page in bodyText]
    numFootnotes = footnotes[0]
    if len(footnotes) > 1:
        footnotes = [delExtraNewlines(footnote) for footnote in footnotes[1:]]
        footnotes = [numFootnotes] + footnotes
    
    
    # THIRD, count then number of spaces (lines that are just '\n' characters)
    spaceCounter_bt = 0
    lineCounter_bt = 0
    spaceCounter_fn = 0
    lineCounter_fn = 0
    for page in bodyText:
        for line in page:
            if line == '\n': spaceCounter_bt += 1
            lineCounter_bt += 1
    if len(footnotes) > 1:
        for fn in footnotes[1:]:
            for line in fn:
                if line == '\n': spaceCounter_fn += 1
                lineCounter_fn += 1
    else:
        spaceCounter_fn = 0
        lineCounter_fn = 0

    if lineCounter_bt > 0:
        btRatio = spaceCounter_bt / lineCounter_bt
    else: btRatio = 0

    if lineCounter_fn > 0:
        fnRatio = spaceCounter_fn / lineCounter_fn
    else: fnRatio = 0

    return [(spaceCounter_bt, lineCounter_bt, btRatio), (spaceCounter_fn, lineCounter_fn, fnRatio)]




#This is bullshit; need a better solution
def isSectionHeader(line):
    if re.search('\s{5,}\d\.\s{5,}', line): return True
    if re.search('\s{10,}\d.\s[A-Z][a-z]+\s[A-Z][a-z]+', line): return True
    if line == '                     25                                                                           26\n':
        return True
    if re.search('^\s{8}\d\)\s', line): return True
    return False




#This complete bullsht method is for exceptions that I have not figured out
#a real way to solve.
def isNotFN(line):
    
    # EXCLUDES DATES!!! (Next couple lines)
    if re.search(r'^\d{1,2}\/\d{1,2}\/\d\d', line.strip()): return True
    if re.search(r'^\d{1,2}\,\s(19|20)\d\d', line): return True

    if re.search(r"^\d{1,2}\/\d{1,2}\/(\d\d|\d\d\d\d)(\s|\.)", line.strip()): return True # Line starts with a date instead of the FN number
    if re.search('^\d+th\s[a-z]', line.strip()): return True
    if line == '1 he followed a driver he suspected was driving under the influence. Defendant\n': return True    
    if re.search('^\d\)\.\n', line): return True #PA Super 4204526
    if re.search('^\d\,\s[a-z]', line): return True #PA common 4023929 fn 7
    return False




def hasUnreadableSpacing(pageList):

    paraCounter0 = 0
    paraCounter1 = 0

    for page in pageList:
        lineBuffer = ['', '', '', '', '']
        for line in page:
            lineBuffer[4] = lineBuffer[3]
            lineBuffer[3] = lineBuffer[2]
            lineBuffer[2] = lineBuffer[1]
            lineBuffer[1] = lineBuffer[0]
            lineBuffer[0] = line

            if re.search('^[A-Za-z]', lineBuffer[0]):
                if re.search('^[A-Za-z]', lineBuffer[1]):
                    if re.search('^\s{6}[A-Z]', lineBuffer[2]):
                        if (lineBuffer[3] == '\n') and (lineBuffer[4] == '\n'):
                            paraCounter0 += 1

            if (lineBuffer[4] == '\n') and (lineBuffer[3] == '\n'):
                if re.search('^\s{13,15}[A-Z]', lineBuffer[2]):
                    if re.search('^[A-Za-z]', lineBuffer[1]):
                        if re.search('^[A-Za-z]', lineBuffer[0]):
                            paraCounter1 += 1

    if (paraCounter0 >= 10) or (paraCounter1 >= 10):
        print("RUNOVER FOOTNOTE DETECTION DISABLED: spacing is not consistently readable")
        return True
    else:
        return False





def autoRunover(line0, line1):
    # This covers many PA supreme court cases, see e.g., 4017235, 4025071
    if re.search('^\([A-Z]{0,1}continued[A-Z]{0,1}\)\n', line0):
        if len(line1) > 4:
            return True
    return False





def nextFNline(line, FNcounter):
    if re.search('^\d+', line):
        number = int(re.search('^\d+', line.strip()).group()) 
        if (number == FNcounter + 1):
            return True
    return False





def isSectionStart(line):

    if re.search('^\s*[A-Za-z]\.', line):
        if re.search('^\s*[A-Za-z]\.[A-Za-z]\.', line): #Need to exclude lines that start with A.B., e.g., "P.G., who did not appear at the termination hearing . . ."
            return True

    if line.startswith(' ' * 25):
        if isTitleCase(line.strip()):
            return True

    if re.search('III.', line):
        return True

    return False





def runoverDoubleSpacing(page, lineStart, spacingInfo):
    
    #This function stops the runOver detecter from returning True when the
    #text following the break is still part of the main text.  It works solely
    #by evaluating the number of spaces in the text

    length = len(page[lineStart:])


    #CAN THE FIRST TWO BE ELIMINATED IN LIGHT OF THE FOLLOWING TEST?

    #RETURNS FALSE IF DOUBLE-SPACED FOR NEXT 11 LINES (i.e., if there are 5 spaces in next 10 lines)
    newLineCounter = 0
    if length >= 10:
        for line in page[lineStart:lineStart + 10]:
            if line == '\n': newLineCounter += 1
        if newLineCounter >= 5:
            return False

    newLineCounter = 0
    for line in page[lineStart:]:
        if line == '\n': newLineCounter += 1
    if (length > 5) and ((newLineCounter / length) >= 0.5):
        return False

    #CONTINUES runover detector if the line starts with "(continued'
    if page[lineStart].startswith('(continued'):
        return True

    # IMPORTANT: stops runover detector if main text is double spaced
    # and the next line is a space, and the line after that has three or
    # more lower case words
    if (length >= 5) and (spacingInfo[0][2] > .3) and (spacingInfo[1][2] < .2):
        if (page[lineStart + 1] == '\n') and (numLowerCaseWords(page[lineStart + 2]) > 3):
            return False

    return True





def runoverLineSpacing(page, lineStart, spacingInfo):
    
    #This function stops the runOver detecter from returning True when the
    #text following the break is still part of the main text.  It works solely
    #by evaluating the number of spaces in the text

    length = len(page[lineStart:])


    #CAN THE FIRST TWO BE ELIMINATED IN LIGHT OF THE FOLLOWING TEST?

    #RETURNS FALSE IF DOUBLE-SPACED FOR NEXT 11 LINES (i.e., if there are 5 spaces in next 11 lines)
    newLineCounter = 0
    if length >= 11:
        for line in page[lineStart:lineStart + 11]:
            if line == '\n': newLineCounter += 1
        if newLineCounter >= 5:
            return False

    newLineCounter = 0
    for line in page[lineStart:]:
        if line == '\n': newLineCounter += 1
    if (length > 5) and ((newLineCounter / length) > 0.4):
        return False

    #CONTINUES runover detector if the line starts with "(continued'
    if page[lineStart].startswith('(continued'):
        return True

    # IMPORTANT: stops runover detector if main text is double spaced
    # and the next line is a space, and the line after that has three or
    # more lower case words
    if (length >= 5) and (spacingInfo[0][2] > .3) and (spacingInfo[1][2] < .2):
        if (page[lineStart + 1] == '\n') and (numLowerCaseWords(page[lineStart + 2]) > 3):
            return False




def stopRunoverDetector(page, lineCounter):

    line0 = page[lineCounter]

    if re.search('^/s/\s[A-Z]', line0.strip()) and line0.startswith('          '): return True
    if line0.startswith('IT IS SO ORDERED'): return True
    if line0.lower().startswith('date:'): return True
    if re.search('^judge\s\w+\sconcurs\sin', line0.strip(), re.IGNORECASE): return True
    if re.search('^\s{30,}respectfully\,\n', line0, re.IGNORECASE): return True
    if re.search(r'\w{1,2}\:\s+prothonotary', line0, re.IGNORECASE): return True

    # --------
    if len(page) > lineCounter + 1:
        line1 = page[lineCounter + 1]

    if len(page) > lineCounter + 3:
        line2 = page[lineCounter + 2]
        line3 = page[lineCounter + 3]
        if line1 == ('Prothonotary\n') and line3.startswith('Date:'):
            return True
    # ---------

    return False





def FNlineSpacing(page, lineStart, FNnum):

    length = len(page[lineStart:])

    # RETURNS FALSE IF DOUBLE-SPACED FOR NEXT 10 LINES; also returns true if
    # the next FN number starts one of the next 10 lines
    newLineCounter = 0
    if length >= 10:
        for line in page[lineStart:lineStart + 10]:
            if line == '\n': newLineCounter += 1
            if re.search(r"^" + str(FNnum+1), line): return True
        if newLineCounter >= 5:
            print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
            return False

    #THE FOLLOWING MIGHT BE TOO MUCH OF AN EXCLUSION  
    #LOOK HERE IF FOOTNOTES START TO GO MISSING

    #Gets indented text blocks that are not footnotes (hopefully . . .)
    if length >= 3:
        if re.search('^(\s{6}|\s{10})\d\.\s[A-Z]', page[lineStart]):
            if re.search('^(\s{9}|\s{13}|\s{6})[A-Za-z]', page[lineStart+1]):
                if re.search('^(\s{9}|\s{13}|\s{6})[A-Za-z]', page[lineStart+2]):
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False

    if length >= 3:
        if re.search('^\s{7}\d\.\s[A-Z]', page[lineStart]):
            if re.search('^\s{7}[A-Za-z]', page[lineStart+1]):
                if re.search('^\s{7}([A-Za-z]|\§\§)', page[lineStart+2]): # the §§ is an exception/patch for PAsuperWC#4094528
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False

    if length >= 3:
        if re.search('^\s{8}\d\.\s[A-Z]', page[lineStart]):
            if re.search('^\s{11}[A-Za-z]', page[lineStart+1]):
                if re.search('^\s{11}[A-Za-z]', page[lineStart+2]): # the §§ is an exception/patch for PAsuperWC#4094528
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False

    if length >= 3:
        if re.search('^\s{8}\d\.\s{3,}[A-Z]', page[lineStart]):
            if re.search('^\s{8}[A-Za-z]', page[lineStart+1]):
                if re.search('^\s{8}[A-Za-z]', page[lineStart+2]):
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False

    if length >= 3:
        if re.search('^\s{5}\d\.\s[A-Z]', page[lineStart]):
            if re.search('^\s{5}[A-Za-z]', page[lineStart+1]):
                if re.search('^\s{5}[A-Za-z]', page[lineStart+2]):
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False

    if length >= 3:
        if re.search('^\s{8}\d\.\s{1,4}[A-Z]', page[lineStart]):
            if re.search('^\s{11}[A-Za-z]', page[lineStart+1]):
                if re.search('^\s{11}[A-Za-z]', page[lineStart+2]):
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False
                elif length >= 4:
                    if re.search('^\s{11}[A-Za-z]', page[lineStart+3]):
                        print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                        return False

    if length >= 3:
        if re.search(r'^\s{10}\d{1,2}\.\s{0,4}[A-Z]', page[lineStart]):
            if re.search("^\s{13}[A-Za-z]", page[lineStart + 1]):
                if re.search("^\s{13}[A-Za-z]", page[lineStart + 2]):
                    print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                    return False
                elif length >= 4:
                    if re.search('^\s{13}[A-Za-z]', page[lineStart+3]):
                        print("Not FN line spacing. Footnote rejected. Line:", page[lineStart])
                        return False

    # Default is True, i.e., the line has footnote spacing
    return True





def colonCheck(line, prevLine1, prevLine2):
    if prevLine1.strip().endswith(":"): return False
    if (prevLine1.strip() == "") and (prevLine2.strip().endswith(":")): return False
    return True



