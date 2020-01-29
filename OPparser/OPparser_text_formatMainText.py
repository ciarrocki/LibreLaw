#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 07:32:00 2019

@author: dan
"""


### Imports

import re, pprint, copy
from OPparser_utils import isTitleCase2, delExcessLineSpaces, getMaxLL
from OPparser_lists import firstEntryTokens, secondEntryTokens, firstToSecond, headerDict, puncEndRE, DelSupremeParaStart





### Main Functions

def formatMainText_text(mainText, FNs, verbose=0):

    revisedMT = delExcessLineSpaces(mainText)

    maxLL = getMaxLL(revisedMT)

    lineSpaceQ = getLineSpaceQ(revisedMT)

    sectionHeadings = getSectionHeadings(revisedMT, verbose)

    indentedBlocks = getIndentedBlocks(revisedMT, sectionHeadings)

    # Need to do paragraphs BEFORE adding HTML for footnote anchors or anything 
    # further; the HTML will make it impossible to do line-length analysis.
    paraStarts = getParagraphs(revisedMT, sectionHeadings, indentedBlocks, maxLL, lineSpaceQ, verbose)

    if verbose > 1:    
        print("\nMax Line Length (98% or 99%):", maxLL)
        print("Line-Space Quotient:", lineSpaceQ)    
        print("\n*** SECTION HEADINGS ***")
        for key in sectionHeadings.keys():
            if sectionHeadings[key] > 0: 
                print(key, sectionHeadings[key], revisedMT[key[0]][key[1]], end='')
                if not revisedMT[key[0]][key[1]].endswith('\n'): print()    
        print("\n*** INDENTED BLOCKS ***")
        for key in indentedBlocks.keys():
            if indentedBlocks[key]: 
                print(key, revisedMT[key[0]][key[1]], end='')
                if not revisedMT[key[0]][key[1]].endswith('\n'): print()
        print("\n*** PARAGRAPH STARTS ***")
        for key in paraStarts.keys():
            if paraStarts[key]:
                print(key, revisedMT[key[0]][key[1]], end='')
                if not revisedMT[key[0]][key[1]].endswith('\n'): print()    

    revisedMT = formatAnchorLines(revisedMT, FNs)

    bigString = convertToHTML(revisedMT, paraStarts, indentedBlocks, sectionHeadings)

    return bigString





### Sub Functions

def convertToHTML(text, paragraphs, blocks, headers):
    
    # Add HTML to each line as needed
    newText = []
    pCounter = 0
    for pageNum, page in enumerate(text):
        newPage = []
        for lineNum, line in enumerate(page):
            if paragraphs[(pageNum, lineNum)]: 
                newPage.append("</p><p id='p" + str(pCounter) + "'>" + line)
                pCounter += 1
            elif headers[(pageNum, lineNum)]: newPage.append('<h3>' + line + '</h3>')
            elif blocks[(pageNum, lineNum)]: newPage.append('<blockquote>' + line + '</blockquote>')              
            else: newPage.append(line)  
        newText.append(newPage)
    
    # Flatten into one big string
    bigString = ''
    for page in newText:
        for line in page:
            if line == '\n': continue
            else: bigString = bigString + line
    
    # Replace all newline characters with spaces
    bigString = bigString.replace('\n', ' ')
    
    # Eliminate starting </p> and add ending </p>
    if bigString.startswith('</p>'): bigString = bigString[4:]
    if not bigString.endswith('</p>'): bigString = bigString + '</p>'
    
    # Remove certain double-HTML, e.g.: </blockquote><blockquote> BUT NOT FOR PARAGRAPHS!!!!!
    bigString = bigString.replace('</blockquote><blockquote>', '')
    bigString = bigString.replace('</h3><h3>', '')

    return bigString




def getParagraphs(text, sectionHeadings, indentedBlocks, maxLL, lineSpaceQ, verbose):
    """ Go through each line of text and determine whether each line is a 
        paragraph start or not.  Relies primarily on getPscore()."""

    paraDict = dict()
    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            
            # Disqualify line if it is a space
            if line == '\n':
                paraDict[(pageNum, lineNum)] = False
                continue
            
            # Disqualify line if it is a section heading or an indented block
            if sectionHeadings[(pageNum, lineNum)] > 0: 
                paraDict[(pageNum, lineNum)] = False
                continue
            elif indentedBlocks[(pageNum, lineNum)]:
                paraDict[(pageNum, lineNum)] = False
                continue

            # Disqualify line if isNotParagraph function returns True
            if isNotParagraph(pageNum, lineNum, line, text):
                paraDict[(pageNum, lineNum)] = False
                continue

            # Get the pScore for the line
            # If the pScore is >= 100, it is deemed a paragraph start
            pScore = getPscore(pageNum, lineNum, line, text, maxLL, lineSpaceQ, sectionHeadings)
            if pScore >= 100: paraDict[(pageNum, lineNum)] = True
            else: paraDict[(pageNum, lineNum)] = False # Default is NOT a paragraph start

    return paraDict





def getPscore(pageNum, lineNum, line, text, maxLL, lineSpaceQ, sectionHeadings):
    """ Generates the pScore for the line.
        The pScore is the likelihood that the line starts a paragraph."""
    pScore = 0
    
    if (pageNum == 0) and (lineNum == 0): return 100 # Auto para start if first line of body 

    # Return 0 if a blank line
    if not line.strip(): return 0 

    # Get wordlist, the previous 2 lines and next 2 lines (the current line is supplied) (remember, there will be a lot of line-spaces)
    wordlist = line.split()
    if lineNum <= 0: prevLine0 = "<START>"
    else: prevLine0 = text[pageNum][lineNum - 1]    
    if lineNum <= 1: prevLine1 = "<START>"
    else: prevLine1 = text[pageNum][lineNum - 2]    
    if lineNum >= len(text[pageNum]) - 1: nextLine0 = "<END>"
    else: nextLine0 = text[pageNum][lineNum + 1]
    if lineNum >= len(text[pageNum]) - 2: nextLine1 = "<END>"
    else: nextLine1 = text[pageNum][lineNum + 2]

    ### Calculate pScore

    # Evaluate characteristics of current line
    if line.startswith("  "): pScore += 75 # Line starts with TWO spaces
    if line.strip()[0].isupper(): pScore += 25 # Line stars with capital letter
    if re.search(r'^(\'|\"|\“)\[[A-Z]', line.strip()): pScore += 25 # Line starts with capitalized quote, e.g.: 
    if re.search(r'^\d{1,2}\.', line.strip()): pScore += 25
    if DelSupremeParaStart.search(line): return 100 # Auto para start if it meets the DE supreme start line regex
    if line.strip().startswith("/s/"): return 100 # Auto para start if it is a signature line: /s/ Joseph R. Slights III 
    if re.search(r"^\*{5,}$", line.strip()): return 100 # Auto para start if it is a "*****" sep line

    # Evaluate characteristics of previous line    
        # Auto para start if previous line is a section heading
    if lineNum > 0: 
        if sectionHeadings[(pageNum, lineNum-1)] > 0: return 100
    if lineNum > 1: 
        if (text[pageNum][lineNum-1].strip() == '') and sectionHeadings[(pageNum, lineNum-2)] > 0: return 100
        # Moderate bump if line is first on the page
    if prevLine0 == "<START>": pScore += 17
        # Most Important Part!!: Whether previous line looks like end of a paragraph!
    if prevLine0.strip() != '':
        if len(prevLine0) < maxLL - 20: pScore += 50 # Length of previous line is less than 20 less than max line length
        if len(wordlist[0]) + len(prevLine0) < maxLL - 3: pScore += 50 # Get Another 50 if the first word of the new line would fit on the old line
        if puncEnd(prevLine0): pScore += 50 # Previous line ends in punctuation
    elif prevLine1.strip() != '':
        if len(prevLine1) < maxLL - 20: pScore += 50 # Length of previous line is less than 20 less than max line length
        if puncEnd(prevLine1): pScore += 50 # Previous line ends in punctuation
        if len(wordlist[0]) + len(prevLine1) < maxLL - 3: pScore += 50 # Get Another 50 if the first word of the new line would fit on the old line

    # TEST!
    #if pageNum == 1: print(pScore, "***", line)

    return pScore






def puncEnd(line):
    modline = line.strip().lower()
    if puncEndRE.search(modline): return True
    return False




def isNotParagraph(pageNum, lineNum, line, text):
    return False





def getSectionHeadings(text, verbose=0):
    """ Returns a dict with index of (pageNum, lineNum) and value is whether line is a section heading.
        The value for each entry in the dict should be -1 if not part of a section heading, 1 for level 1 heading, 2 for level 2 heading, etc."""

    headerTypes, headerLevels = getHeaderTypesLevels(text, verbose)
    headerLines = getHeaderLines(headerTypes, headerLevels, text)
    revisedHeaderLines = addFollowLines(headerLines, text)

    sectionHeadDict = getFinalHeaderDict(revisedHeaderLines, headerLevels, text)

    if verbose > 2:
        print("\n*** HEADER TYPES ***")
        print(headerTypes)
        print("\n*** HEADER LEVELS ***")
        pprint.pprint(headerLevels)
        print("\n*** FIRST HEADER LINES ***")
        pprint.pprint(headerLines, width=125)
        print("\n*** REVISED HEADER LINES ***")
        pprint.pprint(revisedHeaderLines, width = 125)    

    return sectionHeadDict





def getFinalHeaderDict(headerLines, headerLevels, text):

    finalHeaders = dict()
    for key in headerLines.keys():
        for pageNum, lineNum, line in headerLines[key]:
            finalHeaders[(pageNum, lineNum)] = headerLevels[key]

    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            if (pageNum, lineNum) in finalHeaders.keys():
                finalHeaders[(pageNum, lineNum)] = finalHeaders[(pageNum, lineNum)]
            else:
                finalHeaders[(pageNum, lineNum)] = 0

    return finalHeaders





def addFollowLines(headerLines, text):
    revisedHeaderLines = copy.deepcopy(headerLines)
    for key in revisedHeaderLines.keys():
        recordCounter = 0
        for pageNum, lineNum, line in revisedHeaderLines[key]:
            newLines = checkFollowLines(pageNum, lineNum, line, text)
            for n in range(0, newLines):
                recordCounter += 1
                revisedHeaderLines[key].insert(recordCounter, (pageNum, lineNum + 1 + n, text[pageNum][lineNum + 1 + n]) )
            recordCounter += 1
    return revisedHeaderLines





def checkFollowLines(pageNum, lineNum, line, text):
    
    for n in range(0, 15):
        # Dealbreakers:
        # If the next line is a space ('\n') or is over the page length, we are done and return the number of lines we have traversed
        if lineNum + 1 + n >= len(text[pageNum]) - 1: return n
        if text[pageNum][lineNum + 1 + n] == '\n': return n
        # Necessities:
        # Unless one of the two conditions is met, we are done and return the number of lines we have traversed.
        if isTitleCase2(line) and isTitleCase2(text[pageNum][lineNum + 1 + n]): continue
        if line.isupper() and text[pageNum][lineNum + 1 + n].isupper(): continue
        return n
    
    return 0





def getHeaderLines(headerTypes, headerLevels, text):

    headerCounters = dict()
    for headerType in headerTypes:
        headerCounters[headerType] = 0

    headerLines = dict()
    for headerType in headerTypes:
        headerLines[headerType] = []

    prevHeader = ('<START>', -1)

    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            if line == '\n': continue
            if not line.strip().split(): continue
            token0 = line.strip().split()[0]
            for headerType in headerTypes:
                #print("headerType:", headerType)
                #print("headerCounters[headerType]:", headerCounters[headerType])
                if headerCounters[headerType] >= 30:
                    print("Error: formatMainText: Max header counter exceeded")
                    continue
                if token0 == headerDict[headerType][headerCounters[headerType]]:
                    # Use loose title case checker
                    if isTitleCase2(line.strip()):
                        #print("Token:", token0, 'Line:', line)
                        headerCounters[headerType] += 1
                        headerLines[headerType].append((pageNum, lineNum, line))
                        # Reset lower level (but higher number, i.e., 6 is a lower level than 2) counter when a higher level is encountered
                        if headerLevels[headerType] < prevHeader[1]:
                            headerCounters[prevHeader[0]] = 0
                        prevHeader = (headerType, headerLevels[headerType])
    
    return headerLines





def getHeaderTypesLevels(text, verbose):
    firstEntryLines = []
    secondEntryLines = []
    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            if checkFirstEntryToken(line):
                firstEntryLines.append(line)
            if checkSecondEntryToken(line):
                secondEntryLines.append(line)

    secondEntryFlat = ''
    for line in secondEntryLines: secondEntryFlat += line

    finalCandidates = []
    for line in firstEntryLines:
        firstWord = line.strip().split()[0]
        if firstToSecond[firstWord] in secondEntryFlat: finalCandidates.append(line)
    
    if verbose > 1: 
        print("\n*** FINAL CANDIDATES FOR SECTION HEADER TYPES ***")
        pprint.pprint(finalCandidates, width=125)

    headerTypes = []
    for line in finalCandidates:
        if isTitleCase2(line): headerTypes.append(line.strip().split()[0])
        elif line.isupper(): headerTypes.append(line.strip().split()[0])

    # Remove dupes, WITHOUT CHANGING ORDER
    newList = []
    for item in headerTypes:
        if item not in newList: newList.append(item)
    headerTypes = newList

    headerLevels = dict()
    for i, hType in enumerate(headerTypes):
        headerLevels[hType] = i + 1

    return headerTypes, headerLevels





def checkFirstEntryToken(line):
    if line.strip() == '': return False
    lineStart = line.strip().split()[0]
    for token in firstEntryTokens:
        if lineStart == token:
            return True
    return False


def checkSecondEntryToken(line):
    if line.strip() == '': return False
    lineStart = line.strip().split()[0]
    for token in secondEntryTokens:
        if lineStart == token:
            return True
    return False





def getIndentedBlocks(text, sectionHeadings):
    """Returns a dict with index (pageNum, lineNum), each value of which is
       True or False.  True means the line is part of an indented block.  False 
       means the line is not part of an indented block."""
    
    leadSpaceDict = {}
    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            if line == '\n': leadingSpaces = -1
            # Set lead spaces to 0 if it is a section heading
            elif sectionHeadings[(pageNum, lineNum)] > 0: leadingSpaces = 0
            elif re.search("^\s+", line) != None:
                leadingSpaces = len(re.search("^\s+", line).group())
            else:
                leadingSpaces = 0
            leadSpaceDict[(pageNum, lineNum)] = leadingSpaces
            #print(leadingSpaces, line)

    # Go through each line and build indented blocks dictionary
    indentedBlocks = {}
    for pageNum, page in enumerate(text):
        for lineNum, line in enumerate(page):
            # Get the data for the current line, previous line, and next line
            leadSpaces = leadSpaceDict[(pageNum, lineNum)]
            if sectionHeadings[(pageNum, lineNum)] > 0: leadSpaces = 0
            if lineNum == 0: 
                prevLine = "<START>"
                prevLineLeadSpaces = -1
            else:
                prevLine = text[pageNum][lineNum - 1]
                prevLineLeadSpaces = leadSpaceDict[(pageNum, lineNum - 1)]
            if lineNum == len(page) - 1: 
                nextLine = "<END>"
                nextLineLeadSpaces = -1
            else:
                nextLine = text[pageNum][lineNum + 1]
                nextLineLeadSpaces = leadSpaceDict[(pageNum, lineNum + 1)]
            # Evaluate data to make a call
            if leadSpaces > 1:
                if (nextLineLeadSpaces > 1) or (prevLineLeadSpaces > 1):
                    indentedBlocks[(pageNum, lineNum)] = True
                    continue
            # Default is that the line is NOT part of an indented block
            indentedBlocks[(pageNum, lineNum)] = False

    return indentedBlocks





def getLineSpaceQ(text):
    numLines = sum([len(page) for page in text])
    if numLines == 0: return 0
    numLineSpaces = len([line for page in text for line in page if line == '\n'])        
    return numLineSpaces / numLines





def formatAnchorLines(mainText, FNs):
    """ Loop through all footnotes and revise the "anchor lines" - the lines 
        that contain the anchor for each footnote. The revised anchor lines 
        contain HTML for formatting the footnote anchors."""

    # Build dictionary of lines that need to be revised.  Index is (pageNum, lineNum)
    newAnchorLines = {}
    for fnNum, (_, pageNum) in enumerate(FNs):

        fnFoundFlag = False
        if fnNum == 0: continue    

        # First attempt to find footnote anchor (current page using rock-solid methods)    
        for lineNum, line in enumerate(mainText[pageNum - 1]):            
            if re.search(r'\D' + str(fnNum) + r'\s', line):
                if (pageNum, lineNum) in newAnchorLines.keys():
                    revisedLine = editAnchorLine(fnNum, newAnchorLines[(pageNum, lineNum)])
                else:
                    revisedLine = editAnchorLine(fnNum, line)
                newAnchorLines[(pageNum, lineNum)] = revisedLine
                fnFoundFlag = True
                break

        # Second attempt to find footnote anchor (previous page using rock-solid methods)    
        if (not fnFoundFlag) and (pageNum - 2 >= 0):
            for lineNum, line in enumerate(mainText[pageNum - 2]):
                if re.search(r'\D' + str(fnNum) + r'\s', line): 
                    if (pageNum, lineNum) in newAnchorLines.keys():
                        revisedLine = editAnchorLine(fnNum, newAnchorLines[(pageNum, lineNum)])
                    else:
                        revisedLine = editAnchorLine(fnNum, line)
                    newAnchorLines[(pageNum, lineNum)] = revisedLine
                    fnFoundFlag = True
                    break

        # Third attempt to find footnote anchor (current page using more inclusive but less reliable/accurate methods)
        if not fnFoundFlag:
            for lineNum, line in enumerate(mainText[pageNum - 1]):
                if re.search(r'\D' + str(fnNum) + r'(\]|\;|\—)', line):
                    if (pageNum, lineNum) in newAnchorLines.keys():
                        revisedLine = editAnchorLine(fnNum, newAnchorLines[(pageNum, lineNum)])
                    else:
                        revisedLine = editAnchorLine(fnNum, line)
                    newAnchorLines[(pageNum, lineNum)] = revisedLine
                    fnFoundFlag = True
                    break

        # FINAL attempt to find footnote anchor (simply looks for the number ANYWHERE)
        if not fnFoundFlag:
            for lineNum, line in enumerate(mainText[pageNum - 1]):
                if re.search(str(fnNum), line):
                    if (pageNum, lineNum) in newAnchorLines.keys():
                        revisedLine = editAnchorLine(fnNum, newAnchorLines[(pageNum, lineNum)])
                    else:
                        revisedLine = editAnchorLine(fnNum, line)
                    newAnchorLines[(pageNum, lineNum)] = revisedLine
                    fnFoundFlag = True
                    break
        
        if not fnFoundFlag:
            print("Footnote anchor for footnote", fnNum, "not found.")

    #pprint.pprint(newAnchorLines, width=100)

    # Build revised text that replaces anchor lines with the revised anchor lines
    newPageList = []    
    for pageNum, page in enumerate(mainText):
        newPage = []
        for lineNum, line in enumerate(page):
            if (pageNum + 1, lineNum) in newAnchorLines.keys():
                newPage.append(newAnchorLines[(pageNum + 1, lineNum)])
            else:
                newPage.append(line)
        newPageList.append(newPage)

    return newPageList





def editAnchorLine(fnNum, line):
    
    newText = "<a href='#FNnumber" + str(fnNum) + "' class='FNanchor' name='FNanchor" + str(fnNum) + "'>" + str(fnNum) + "</a>"
    
    if re.search(r'\D' + str(fnNum) + r'\s', line) != None:
        newLine = re.sub(r'(\D)' + str(fnNum) + r'(\s)', r'\1' + newText + r'\2', line)    
    elif re.search(r'\D' + str(fnNum) + r'\s', line) != None:
        newLine = re.sub(r'(\D)' + (str(fnNum)) + r'(\s)', r'\1' + newText + r'\2', line)
    elif re.search(r'\D' + str(fnNum) + r'\]', line) != None:
        newLine = re.sub(r'(\D)' + (str(fnNum)) + r'(\])', r'\1' + newText + r'\2', line)
    elif re.search(str(fnNum), line) != None:
        newLine = re.sub(str(fnNum), newText, line)
    else:
        newLine = line
    
    return newLine







#NOT IN USE
def getHeaderLevels(headerLines):
    """ Assigns a level (1, 2, 3, etc.) to each of the detected header types.
        Done purely in order of appearance, i.e., first header type is level 1,
        second header type is level 2, etc."""
    firstHeaderLines = []
    for key in headerLines:
        firstHeaderLines.append(headerLines[key][0])    
    sortedFirstHeaderLines = sorted(firstHeaderLines)

    headerLevels = dict()
    for i, (_, __, line) in enumerate(sortedFirstHeaderLines):
        headerLevels[line.strip().split()[0]] = i + 1
    
    return headerLevels





