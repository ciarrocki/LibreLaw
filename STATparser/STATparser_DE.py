#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 21:32:26 2019

@author: dan
"""



# Testing Paths
ctt = "/home/dan/Data/DelawareGov/Statutes/Processed/constitution.txt"
t1 = "/home/dan/Data/DelawareGov/Statutes/Processed/title1.txt"
t2 = "/home/dan/Data/DelawareGov/Statutes/Processed/title2.txt"
t3 = "/home/dan/Data/DelawareGov/Statutes/Processed/title3.txt"
t4 = "/home/dan/Data/DelawareGov/Statutes/Processed/title4.txt"
t5 = "/home/dan/Data/DelawareGov/Statutes/Processed/title5.txt"
t6 = "/home/dan/Data/DelawareGov/Statutes/Processed/title6.txt"
t7 = "/home/dan/Data/DelawareGov/Statutes/Processed/title7.txt"
t8 = "/home/dan/Data/DelawareGov/Statutes/Processed/title8.txt"
t9 = "/home/dan/Data/DelawareGov/Statutes/Processed/title9.txt"
t10 = "/home/dan/Data/DelawareGov/Statutes/Processed/title10.txt"
t11 = "/home/dan/Data/DelawareGov/Statutes/Processed/title11.txt"
t12 = "/home/dan/Data/DelawareGov/Statutes/Processed/title12.txt"
t13 = "/home/dan/Data/DelawareGov/Statutes/Processed/title13.txt"


### Imports

import re
import copy

from STATparser_toDjango import saveDEtreeRecord, saveDEstatRecords
from STATparser_format import formatSections_DE, addPrevNext_DE
from STATparser_utils import proDataDir_DESTAT, getFileList, sectionGrabbers_destat, sectionNumbers_destat




### Main Functions


def parseAndSave_DEtitle_all():
    allTitles = getFileList(proDataDir_DESTAT, ext='.txt', recursive=False)
    allTitles = [t for t in allTitles if not t.endswith('constitution.txt')]
    print("Progress: " + " " * (len(allTitles) - 11) + "|")
    for f in allTitles:
        print("*", end='')
        parseAndSaveTitle_DE(f)
    print(" Done\nMaking custom trees . . . ", end='')
    makeCustomTrees_DE()
    print(" Done.")




def parseAndSaveTitle_DE(filepath, verbose=0):
    data = parseTitle_DE(filepath, verbose)
    saveDEtreeRecord(data)
    saveDEstatRecords(data)
    return True




def makeCustomTrees_DE():
    
    # NUMBER 100: General Corporation Law
    createTree_DEcode(8, 101, 398, "Delaware General Corporation Law", "Delaware General Corporation Law", 100, "Title", "Delaware General Corporation Law")
    
    # NUMBER 101: Limited Liability Company Act
    createTree_DEcode(6, "18-101", "18-1208", "Delaware Limited Liability Company Act", "Delaware Limited Liability Company Act", 101, "Title", "Delaware Limited Liability Company Act")

    # NUMBER 102: Residential Landlord-Tenant Code
    createTree_DEcode(25, 5101, 5907, "Delaware Residential Landlord-Tenant Code", "Delaware Residential Landlord-Tenant Code", 102, "Title", "Delaware Residential Landlord-Tenant Code")

    # NUMBER 103: Personal Income Tax
    createTree_DEcode(30, 1101, 1243, "Delaware Personal Income Tax", "Delaware Personal Income Tax", 103, "Title", "Delaware Personal Income Tax")

    # NUMBER 104: Court and Judicial Procedure
    createTree_DEcode(10, 3101, 5403, "Delaware Court and Judicial Procedure", "Delaware Court and Judicial Procedure", 104, "Title", "Delaware Court and Judicial Procedure")

    return True    



def parseTitle_DE(filepath, verbose=0):

    # STEP #1: Load the raw text and do some minor processing
    rawlines = loadlines_DEstat(filepath)
    prolines = deletePageNums_stat(rawlines)
    prolines, repeatLines = deleteRepeatLines(prolines)

    # STEP #2: Break statute into "sections" (see below for more detail)
    rawsections = getSections_DE(prolines, rawlines)

    # STEP #3: Get the title number (e.g., 8) and title title (e.g., Corporations)
    titleTitle, titleNum = getTitleNumTitle_DE(rawsections)

    # STEP #4: Remove the first layer (i.e., the "Title" sectionType layer)
    rawsections = rawsections[1:]

    # STEP #5: Generate the HTML that will be displayed on the titleView website
    bigHTML = getTreeHTML_DE(rawsections, titleNum)

    # STEP #7: Fill in the data source
    source = "https://delcode.delaware.gov"

    # STEP #8: Format the Sections
    formattedSections = formatSections_DE(rawsections)

    # STEP #9: Get previous and next section links
    finalSections = addPrevNext_DE(formattedSections, titleNum)
    
    finalSections = addCitation_destat(finalSections, titleNum)

    # STEP #10: Generate Full Name
    fullName = "Title " + str(titleNum) + " - " + titleTitle

    data = {"number":titleNum, "nameText":titleTitle,
            "bigHTML":bigHTML, "source":source,
            "filepath":filepath, "sections":finalSections,
            "fullName":fullName, "type": "Title", "smallHTML": "",
            "description":""}

    # DEBUGGING
    #with open("/home/dan/Desktop/test.html", 'w') as f:
    #    f.write(data['titleHTML'])

    return data



def addCitation_destat(sections, titlenum):
    newsections = []
    for sec in sections:
        tempsec = sec
        tempsec['Citation0'] = str(titlenum) + " Del. C. § " + tempsec['number']        
        newsections.append(tempsec)
    return newsections




def createTree_DEcode(title, startSection, endSection, fullName, nameText, number, treeType, description):
    
    filepath = proDataDir_DESTAT + "title" + str(title) + ".txt"
    data = parseTitle_DE(filepath)

    
    if type(startSection) == str:
        # A dashed section is "18-101", e.g.; common in DE Title 6, e.g.
        if isDashedSection(startSection): startSection = getDashedSectionNum(startSection)
        else: startSection =  int(re.sub("\D", "", startSection)) # Simply remove all non-digit characters and cast as an int 
    
    if type(endSection) == str:
        # A dashed section is "18-101", e.g.; common in DE Title 6, e.g.
        if isDashedSection(endSection): endSection = getDashedSectionNum(endSection)
        else: endSection =  int(re.sub("\D", "", endSection)) # Simply remove all non-digit characters and cast as an int         
    
    treeSections = []    
    currentSection = 0
    virgin = True
    startPos = 0
    for i, section in enumerate(data["sections"]):
        if section["sectiontype"] == "Section": 
            if isDashedSection(section["number"]): currentSection = getDashedSectionNum(section["number"])
            else: currentSection = int(re.sub("\D", "", section["number"]))
        if ((currentSection >= startSection) and (currentSection <= endSection)):
            if virgin:
                virgin = False
                startPos = i
            treeSections.append(section)

    for section in reversed(data["sections"][:startPos]):
        if section["sectiontype"] != "Section": treeSections = [section] + treeSections
        else: break

    # Find last section that is actually a section (and not a header)
    endPos = len(treeSections)
    for section in reversed(treeSections):
        if (section['sectiontype'] == "Section"): break
        endPos -= 1

    # Cut empty sections (unwanted headers) from end of list
    treeSections = treeSections[:endPos]

    treeSec1 = treeSections

    # Cut first section(header) if it is the sole header of its level 
    # This addresses situations where the entire tree would be contained in the first header
    # Repeat this process as necessary until first header is not a single header
    #print("Section 0 sectionstack:", treeSections[0]['sectionstack'])
    while True:
        baseStackLength = len(treeSections[0]['sectionstack'])
        multiBaseFlag = False
        for section in treeSections[1:]:
            if len(section['sectionstack']) <= baseStackLength:
                multiBaseFlag = True
                break
        if not multiBaseFlag: 
            treeSections = treeSections[1:] # if there were not multiple headers at highest level, need to trim list and repeat
        else: 
            break # If there are multiple headers at highest level, we're done


    treeSec2 = treeSections

    treeHTML = getTreeHTML_DE(treeSections, title)
    
    data = {}
    data["fullName"] = fullName
    data["type"] = treeType
    data["number"] = number
    data["nameText"] = nameText
    data["description"] = description
    data["bigHTML"] = treeHTML
    data["smallHTML"] = ""
    data["source"] = "DEgovStats"
    data["filepath"] = filepath

    saveDEtreeRecord(data)
    
    return treeSec1, treeSec2



    

def isDashedSection(numText):
    if re.search(r"\d{1,3}\-\d{2,5}", numText): return True
    return False



def getDashedSectionNum(numText):
    hits = re.search(r"(\d{1,3})\-(\d{2,5})", numText)
    newNumString = hits[1] + hits[2].zfill(5)
    finalNum = int(newNumString)
    return finalNum




def getTitleNumTitle_DE(sections):
    """ v0.1 - Simply looks for the first section of sectionType "Title" and 
        then gets the title and number of that section."""

    title = ""
    num = -1
    for sec in sections:
        if sec['sectiontype'] == 'Title':
            title = sec['title']
            num = sec['number']
            break

    return title, num





def getTreeHTML_DE(sections, titleNum):

    titleHTML = ""
    sectionStack = []
    maxlevel = getMaxLevel_DE(sections)
    for i, sec in enumerate(sections):

        if sectionStack == None: 
            sectionStack.append(sec['sectiontype'])
            titleHTML += "<details><summary>" + sec['sectiontype'] +\
                " " + sec['number'] + " " + sec['title'] + "</summary>"

        elif sec['sectiontype'] in sectionStack: 
            place = sectionStack.index(sec['sectiontype'])            
            numCloses = len(sectionStack) - place
            if sections[i-1]['sectiontype'] == maxlevel: numCloses -= 1
            #if sec['sectiontype'] == maxlevel: numCloses = 0
            for c in range(numCloses): titleHTML += "</details>"
            sectionStack = sectionStack[:place] + [sec['sectiontype']]
            margin = len(sectionStack) * 10
            if sec['sectiontype'] != maxlevel:
                titleHTML += "<details style='margin-left: " + str(margin) + "px'><summary>"\
                        + sec['sectiontype'] +" " + sec['number'] + " "\
                        + sec['title'] + "</summary>"
            else:
                anchor = "<a href='/Delaware/statutes/" + str(titleNum) + "/" + sec['number'] + "'>"
                titleHTML += anchor + sec['sectiontype'] +" " + sec['number'] + " " + sec['title'] + "</a>"

        else: 
            sectionStack.append(sec['sectiontype'])
            margin = len(sectionStack) * 10
            if sec['sectiontype'] != maxlevel:
                titleHTML += "<details style='margin-left: " + str(margin) + "px'><summary>"\
                        + sec['sectiontype'] +" " + sec['number'] + " "\
                        + sec['title'] + "</summary>"
            else:
                anchor = "<a href='/Delaware/statutes/" + str(titleNum) + "/" + sec['number'] + "'>"
                titleHTML += anchor + sec['sectiontype'] +" " + sec['number'] + " " + sec['title'] + "</a>"

    return titleHTML





def getMaxLevel_DE(sections):
    sectionDict = {}
    for sec in sections:
        if sec['sectiontype'] not in sectionDict.keys(): 
            sectionDict[sec['sectiontype']] = 1
        else:
            sectionDict[sec['sectiontype']] += 1
    sectionList = [i for i in sectionDict.items()]
    sortedList = sorted(sectionList, key=lambda tup: tup[1])
    return sortedList[-1][0]





def getSections_DE(linelist, rawlines):

    # Get all lines that match one of the patterns in the keys of sectionGrabbers
    basetree = []
    for i, line in enumerate(linelist):
        for pattern in sectionGrabbers_destat.keys():
            if re.search(pattern, line.strip()):
                if i < len(linelist) - 1: line2 = linelist[i+1]
                else: line2 == "<END>"
                if not sectionDQ_DE(line, line2):
                    basetree.append((i, sectionGrabbers_destat[pattern], line))

    # Add lines that might have been cut
    newBranches = []
    for line in rawlines:
        if line == basetree[0][2]: break
        for pattern in sectionGrabbers_destat.keys():
            if re.search(pattern, line.strip()): 
                if (-1, sectionGrabbers_destat[pattern], line) not in newBranches: 
                    newBranches.append((-1, sectionGrabbers_destat[pattern], line))
    basetree = newBranches + basetree

    # Get types of sections, in hierarchical order
    sectionOrder = []
    for lineNum, sectionType, line in basetree:
        if sectionType not in sectionOrder: 
            sectionOrder.append(sectionType)
    #print(sectionOrder)

    # Get section numbers (e.g.: "§ 102 Contents of certificate of incorporation" is 102)
    tree2 = []
    for lineNum, sectionType, line in basetree:
        if re.search(sectionNumbers_destat[sectionType], line):
            number = re.search(sectionNumbers_destat[sectionType], line)[1]
        else:
            print("ERROR")
            number = ""
        tree2.append((lineNum, sectionType, number, line))

    # Get section titles, text start lines, and text endlines
    tree3 = []
    for i, (lineNum, sectionType, number, line) in enumerate(tree2):
        # Title and startline
        bareline = re.sub(sectionNumbers_destat[sectionType], "", line)
        if len(bareline.strip()) < 3:
            if linelist[lineNum+1].strip() != "": 
                title = linelist[lineNum+1].strip()
                startline = lineNum + 2
            elif linelist[lineNum+2].strip() != "": 
                title = linelist[lineNum+2].strip()
                startline = lineNum + 3
            else:
                print("ERROR")
                title = ""
        else: 
            title = bareline.strip()
            startline = lineNum + 1
        title = formatTitle_DE(title)
        # Endline
        if lineNum == -1: endline = -1
        elif i >= len(tree2) - 1: endline = len(linelist) - 1
        else: endline = tree2[i+1][0] - 1 # Next entry's lineNum - 1
        tree3.append((sectionType, number, title, startline, endline))

    # Loop to collect the text and SECTIONSTACK
    sections0 = []
    sectionStack = []
    sectionStack2 = []
    for sectionType, number, title, startline, endline in tree3:

        if len(sectionStack) == 0:
            sectionStack.append((sectionType, number, title))
            sectionStack2.append(sectionType)
        elif sectionType in sectionStack2:
            place = sectionStack2.index(sectionType)
            sectionStack = sectionStack[:place] + [(sectionType, number, title)]
            sectionStack2 = sectionStack2[:place] + [sectionType]
        elif sectionType not in sectionStack2:
            sectionStack.append((sectionType, number, title))
            sectionStack2.append(sectionType)
    
        #print(sectionStack)
        
        tempstack = copy.deepcopy(sectionStack)
        
        data = {"sectiontype":sectionType, "number":number, "title":title,
                "text":linelist[startline:endline+1], 
                "sectionstack":tempstack}        
        sections0.append(data)

    # Delete redundant headers (i.e., the "Part" issue, see Title 3, where the part reappears before every chapter)
    sections = []
    for i, sec in enumerate(sections0):
        if i > 0:
            if (sec['sectiontype'], sec['number'], sec['title']) in sections0[i-1]['sectionstack']:
                continue
        sections.append(sec)

    return sections





def formatTitle_DE(text):
    title = text.strip()
    title = re.sub(r"^\-\s+", "", text) # Starting dashes (e.g.: Title 8 - Corporations)
    return title





def loadlines_DEstat(filepath):
    # Load raw lines from text file
    rawtext = []
    with open(filepath) as f:
        rawtext = f.readlines()
    # Minor cleanup (remove form feed/page sep characters)
    protext = [line.replace("\x0c", "") for line in rawtext]
    return protext





def deletePageNums_stat(linelist):
    proList = []
    length = len(linelist)
    for i, line in enumerate(linelist): 
        if re.search(r"^Page\s?\d{1,3}(\s?of\s?\d{1,3})?$", line):
            if i + 1 <= length - 1:
                if linelist[i+1].strip() == '':
                    continue
        proList.append(line)
    return proList





def deleteRepeatLines(linelist, verbose=0):

    # Build dict showing number of times each line appears
    lineDict = {}
    for line in linelist:
        if line in lineDict.keys(): lineDict[line] += 1
        else: lineDict[line] = 1

    # Calculate repeat threshold
    halfpercent = int(len(linelist) *.005)
    thresh = halfpercent if halfpercent >= 10 else 10
    if verbose > 1: print("halfpercent:", halfpercent, "threshold:", thresh)

    # Build list of lines that repeat above threshold
    repeatList = []
    for key in lineDict.keys():
        if (lineDict[key] >= thresh) and (key.strip() != ""): 
            repeatList.append(key)
    if verbose > 1: print("repeatList:", repeatList)

    # Build new linelist that does not contain repeating lines
    proList = [line for line in linelist if line not in repeatList]

    return proList, repeatList



def sectionDQ_DE(line, line2):
    if re.search(r"^\s?Title\s\d{1,3}\s[a-z]", line): return True # Line starts with "Title #" and then the next word starts with a lowercase letter.  E.G.: "Title 9 may be satisfied by . . . "
    if re.search(r"^Title\s\d{1,3}\s\[repealed\]\)\swith", line): return True # "Title 30 [repealed]) with the". Addresses specific problem in 12 Del. C. 2304
    if re.search(r"^\s+Article\s\d{1,3}\s[a-z]", line): return True # Line starts with "Article #" and then the next word starts with a lowercase letter.  E.G.: "Article 2 shall . . . "
    if re.search(r"^Article\s\d{1,3}\.", line): return True
    if re.search(r"^Article\s\d{1,3}\,\sChapter\s\d{1,3}\sof\sthe", line): return True # "Article 10, Chapter 65 of the Revised": specific situation in 17 Del. C. 517
    if re.search(r"^Chapter\s\d{1,3}\sor\sC", line): return True
    if re.search(r"^Chapter\s\d{1,3}([A-D])?\sof", line): return True
    if re.search(r"^Chapter\s\d{1,3}\sand\/or", line): return True
    if re.search(r"^Chapter\s\d\,\sTitle\s", line): return True # Starts with "Chapter #, Title". E.G.: "Chapter 3, Title 30"  Addresses specific problem in 12 Del. C. 1167
    if re.search(r"^Chapter\s\d{1,4}\)\sin\sthe", line): return True # "Chapter 85) in the individual’s". Specific problem in 19 Del. C. 3326
    if re.search(r"^Chapter\s\d{1,3}\,\s\d{1,3}\sor\s", line): return True # Chapter 23 , 27 or 29 of this "; problem in 30 Del. C. 2010
    if re.search(r"^Section\s\d+\set\sseq\.\)", line): return True
    if re.search(r"^§\s\d{1,5}\sof\sthe\sU\.S\.\s", line): return True # "§ 457 of the U.S. Internal Revenue Code". Specific problem in 18 Del. C. 4403
    if re.search(r"^§\s\d{1,5}\sof\sTitle\s\d{1,3}", line): return True # "§ 4218 of Title 11" see 10 Del. C. 1025
    if re.search(r"^Subtitle\s[A-Z]\sof\sthe", line): return True
    if re.search(r"^Part\s\d{1,2}\sof", line): return True
    if re.search(r"^Part\s[A-Z]{1,5}\sof", line): return True
    if re.search(r"^Part\s\d{1,5}\sin\sits", line): return True # "Part 395 in its entirety" Problem in 21 Del. C. 4707
    if re.search(r"^Part\sD\s[a-z]", line): return True # Line starts with "Part D " and then next character is lower case. E.G. "Part D coverage."
    if line.startswith("Part"):
        if ("Protection From Abuse Proceedings" in line2) or ("Adult Proceedings" in line2): return True
    if re.search(r"Subchapter\s[A-Z]{1,8}\,\sChapter\s\d{1,3}\sof\sTitle\s\d{1,3}\sof\sthe\sU\.", line): return True # "Subchapter XVIII , Chapter 7 of Title 42 of the U.S.C.". Specific situation in 18 Del. C. 4403
    
    return False
    

