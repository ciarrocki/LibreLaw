#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 09:44:52 2019

@author: dan
"""


import re
from STATparser_utils import getSoup

from STATparser_utils import dataDir_PAlegis, seed_PAlegis
from STATparser_toDjango import savePAstatRecords, savePAtreeRecord


allTitles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 
             20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 
             37, 38, 39, 40, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 
             54, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 
             72, 73, 74, 75, 76, 77, 78, 79]





def parseAndSave_PAlegis_all(verbose=0):
    print("Progress: " + " " * (len(allTitles) - 11) + "|")
    for t in allTitles:
        parseAndSaveLegis_PA(t, verbose=verbose)
        print("*", end='')
    print(" Done.")





def parseAndSaveLegis_PA(title, verbose=0):
    
    bigHTML, sectionsDict, titleNum, titleName, filepath = parseLegis_PA(title, verbose)
    source = "Legis - " + seed_PAlegis
    fullName = str(titleNum) + " - " + titleName
    treeType = "Title"
    number = titleNum
    nameText = titleName
    description = ""
    smallHTML = ""

    savePAstatRecords(sectionsDict, title, source, filepath)
    savePAtreeRecord(fullName, treeType, number, nameText, description, 
                     bigHTML, smallHTML, source, filepath)

    return True





def parseLegis_PA(title, verbose=0):
    
    # SKIP TITLE 46 - REPEALED!
    if title == 46: return "", dict(), 46, "Title 46 - Legislature (Repealed)", "/home/dan/Data/Legis/Pennsylvania/title46.html"

    # Get the filepath:
    filepath = dataDir_PAlegis + "title" + str(title).zfill(2) + ".html"
    filepath = filepath.replace("00", "0") # Fix odd case: constitution is title0.html (not title00.html)

    # get beautifulsoup object
    soup = getSoup(filepath)
    if referToUncodified(soup):
        bigHTML = getReferToUncodifiedHTML(title, soup)
        return bigHTML, dict(), title, "Title " + str(title), filepath

    # Parse
    # Step 1: Split HTML file into list of paragraph elements
    plist = soup.find_all("p")
    # Step 2: Split list of paragraph elements into two lists: TOC and body
    titleNum, titleName, tocPlist, bodyPlist = splitPlist(plist)
    # Step 3: Get treeview HTML and preliminary sections dictionary
    bigHTML, sections = parseTOC(tocPlist, int(title), titleName, verbose=verbose)
    # Step 4: Get text of each of the sections
    sections = getSectionText(sections, bodyPlist)
    # Step 5: Add Citation0
    sections = add_citation0_pastat(sections, titleNum)

    return bigHTML, sections, titleNum, titleName, filepath





def add_citation0_pastat(sections, titlenum):
    
    newsections = {}
    for k in sections.keys():
        tempsec = sections[k]
        tempsec['Citation0'] = str(titlenum) + " Pa.C.S. § " + tempsec['number']        
        newsections[k] = tempsec
    return newsections






def getSectionText(sections, bodyPlist, verbose=0):

    writeOn = False
    for p in bodyPlist:
        
        ptext = p.text.strip()

        # Determine if write should be turned on, and initialize if so
        if isSectionOn_GST(ptext): 
            sectionNum, textTitle = getSecNumTitle(ptext, verbose)
            if (sectionNum in sections.keys()): 
                sections[sectionNum]["text"] = ""
                writeOn = True
            else:
                writeOn = False
    
        # Determine if write should be turned off
        if isWriteOff_GST(ptext):
            writeOn = False
    
        # If write is on, write to appropriate section
        if writeOn:
            #if sections[sectionNum]["text"] == "": sections[sectionNum]["text"] = "<p>"
            #sections[sectionNum]["text"] = sections[sectionNum]["text"] + "</p><p>" + ptext
            pro_p = process_para_html(str(p))
            sections[sectionNum]["text"] = sections[sectionNum]["text"] + pro_p

    """# Go through sections and add ending "</p>" to all sections with text
    for k in sections.keys():
        if ('text' in sections[k].keys()) and (sections[k]['text'] != ""): 
            sections[k]['text'] = sections[k]['text'] + "</p>"
    """

    return sections





def process_para_html(html):
    
    newhtml = re.sub(r"line\-height\:\d{1,2}\.\d{4}in\;", "", html)
    
    return newhtml



def isSectionOn_GST(text):
    if text.startswith("§"): return True
    return False




def isWriteOff_GST(text):
    text = text.lower()
    if text.startswith("chapter"): return True
    if text.startswith("subchapter"): return True
    if text.startswith("part"): return True
    return False




def referToUncodified(soup):
    text = soup.text
    if "Editorial Note:  A program of codification and compilation of" in text: return True
    return False





def getReferToUncodifiedHTML(title, plist):
    return "ENTER EDITORIAL NOTE HERE"




def parseTOC(tocPlist, titleNum, titleName, verbose=0):
    sectionStack = ["title"]
    numberStack = [str(titleNum)]
    fullStack = ["Title " + str(titleNum) + " - " + titleName]
    sectionList = []
    bigHTML = ""

    for p in tocPlist:
        
        # CASE 1: It's nothing - skip
        ptext = p.text.strip().replace("\xa0", "")
        if (ptext == "") or (ptext == None): continue
        if skipline_parseTOC(ptext):
            if verbose > 0: print("SKIP:", ptext)
            continue
        # CASE 2: It's a heading, not a substantive section
        if not ptext.startswith("§"):
            sectionType, sectionNum, titleText = processSectionText(ptext)
            if runOverLine_TOC(ptext): # special case - modify last section if this is a runover line
                if verbose > 0: print("RUNOVER:", ptext)
                lastSummary = bigHTML.rfind("</summary>")
                bigHTML = bigHTML[:lastSummary] + " " + ptext + bigHTML[lastSummary:]
                fullStack[-1] = fullStack[-1] + " " + ptext
                continue
            if sectionType in sectionStack:
                place = sectionStack.index(sectionType)
                closures = len(sectionStack) - place
                for n in range(closures): bigHTML = bigHTML + "</details>"
                sectionStack = sectionStack[:place] + [sectionType]
                numberStack = numberStack[:place] + [sectionNum]
                fullStack = fullStack[:place] + [sectionType.title() + " " + sectionNum + " - " + titleText]
                margin = (len(sectionStack) * 10) - 10
                bigHTML = bigHTML + "<details style='margin-left: " + str(margin) + "px'><summary>" + ptext + "</summary>"
            else:
                sectionStack = sectionStack + [sectionType]
                numberStack = numberStack + [sectionNum]
                fullStack = fullStack + [sectionType.title() + " " + sectionNum + " - " + titleText]
                margin = (len(sectionStack) * 10) - 10
                bigHTML = bigHTML + "<details style='margin-left: " + str(margin) + "px'><summary>" + ptext + "</summary>"
        
        # CASE 3: It's a substantive section (not a heading)
        else:
            if repealedPA(ptext): 
                if verbose > 0: print("REPEAL SKIP:", ptext)
                continue
            newSec = dict()
            secNum, textTitle = getSecNumTitle(ptext, verbose)
            newSec["number"] = secNum
            newSec["title"] = textTitle
            newSec["sectionstack"] = fullStack + ["Section" + " " + str(secNum) + " - " + textTitle]
            newSec["sectiontype"] = "Section"
            sectionList.append(newSec)            
            margin = (len(sectionStack) * 10) - 10
            bigHTML = bigHTML + "<a href='/Pennsylvania/statutes/" + str(titleNum) + "/" + str(secNum) + "' style='margin-left: " + str(margin) + "px'>" + ptext + "</a>"
            

    # Add closing </details> tags
    for i in range(len(sectionStack)): bigHTML = bigHTML + "</details>"


    # Add "previous" and "next" links to each of the sections
    for i, sec in enumerate(sectionList):
        if i == 0: 
            sec["previous"] = ""
        else: 
            sec["previous"] = "<a href='/Pennsylvania/statutes/" + str(titleNum) + "/" + sectionList[i-1]["number"] + "'>" + "§ " + sectionList[i-1]["number"] + " - " + sectionList[i-1]["title"] + "</a>"
        if i + 1 >= len(sectionList): 
            sec["next"] = ""
        else: 
            sec["next"] = "<a href='/Pennsylvania/statutes/" + str(titleNum) + "/" + sectionList[i+1]["number"] + "'>" + "§ " + sectionList[i+1]["number"] + " - " + sectionList[i+1]["title"] + "</a>"


    # Turn sectionList into a dictionary indexed by sectionNum
    sections = dict()
    for sec in sectionList:
        sections[sec["number"]] = sec

    return bigHTML, sections





def runOverLine_TOC(ptext):
    if ptext.startswith("PART "): return False
    if ptext.startswith("Chapter "): return False
    if ptext.startswith("ARTICLE "): return False
    if ptext.startswith("Subchapter "): return False
    if ptext.startswith("§"): return False
    if ptext.startswith("SUBPART "): return False
    if ptext.isupper(): return True
    return False





def repealedPA(ptext):
    if re.search(r"^\§\s\d{1,5}\s\-\s\§\s\d{1,5}", ptext): 
        if "repealed" in ptext.lower(): return True
    return False





def getSecNumTitle(text, verbose=0):
    texttitle = ""
    num = ""
    if re.search(r"^\§\s(\d{1,6}(\.\d+)?)\.\s", text):
        num = re.search(r"^\§\s(\d{1,6}(\.\d+)?)\.\s", text)[1]
        texttitle = re.sub(r"^\§\s(\d{1,6}(\.\d+)?)\.\s", "", text)
    elif re.search("^\§\s(\d[A-Z0-9]{1,5}(\.\d)?)\.\s", text):
        num = re.search("^\§\s(\d[A-Z0-9]{1,5}(\.\d)?)\.\s", text)[1]
        texttitle = re.sub("^\§\s(\d[A-Z0-9]{1,5}(\.\d)?)\.\s", "", text)
    else:
        if verbose > 0: print("Cannot parse section title text:", text)
    texttitle = texttitle.strip()
    return num, texttitle





def processSectionText(text):
    
    if text.startswith("PARTICULAR"): return "", "", text
    
    if text.startswith("PART"):  
        if re.search("^PART\s([A-Z]{1,5})$", text):# ODD CASE FIRST (eg, "PART III" on one line, with nothing else at all - texttitle is on next line)
            num = re.search("^PART\s([A-Z]{1,5})$", text) [1]
            titleText = ""
            return "part", num, titleText
        num = re.search(r"^PART\s([A-Z]{1,5})(\-[A-Z])?\.\s", text)[1] # NORMAL CASE IF ODD DOES NOT HIT; normal case is, e.g.: "PART II. GENERAL PROVISIONS"
        titleText = re.sub(r"^PART\s([A-Z]{1,5})(\-[A-Z])?\.\s", "", text).strip()
        return "part", num, titleText

    if text.startswith("Chapter"):
        num = re.search(r"^Chapter\s((\d{1,4}[A-Z]?)|(\d[A-Z]\d{1,2}))\.\s", text)[1]
        titleText = re.sub(r"^Chapter\s((\d{1,4}[A-Z]?)|(\d[A-Z]\d{1,2}))\.\s", "", text).strip()
        return "chapter", num, titleText
    
    if text.startswith("Subchapter"):
        num = re.search(r"^Subchapter\s([A-Z]{1,5})\.(\d\.)?\s", text)[1]
        titleText = re.sub(r"^Subchapter\s([A-Z]{1,5})\.(\d\.)?\s", "", text).strip()
        return "subchapter", num, titleText

    if text.startswith("SUBPART"):
        num = re.search(r"^SUBPART\s([A-Z0-9]{1,5})\.\s", text)[1]
        titleText = re.sub(r"^SUBPART\s([A-Z0-9]{1,5})\.\s", "", text).strip()
        return "subpart", num, titleText

    return "", "", text





def splitPlist(plist):
    
    tocPlist = []
    bodyPlist = []
    titleNum = -1
    nameList = []
    
    for i, p in enumerate(plist):
        ptext = p.text
        plower = ptext.lower()
        if re.search(r"TITLE\s(\d{1,2})", ptext):
            titleNum = int(re.search(r"TITLE\s(\d{1,2})", ptext)[1])
            continue
        if "CONSTITUTION" in ptext:
            titleNum = 0
            nameList.append(ptext)
        if (("part" in plower) or ("chapter" in plower) or ("§" in plower) or ("article" in plower) or ('CONSTITUTION' in ptext)):
             startpos = i
             break
        nameList.append(ptext)

    breakpos = -1
    for i, p in enumerate(plist[startpos+1:]):
        if ("TITLE " + str(titleNum)) in p.text:
            breakpos = (startpos + i)
            break
        if "CONSTITUTION" in p.text:
            breakpos = (startpos + i)
            break
        if p.text == "PART I": # SPECIAL CASE FOR TITLE 8 - not caught by first if statement above
            breakpos = (startpos + i)
            break
        if ((titleNum == 72) and (p.text.strip().startswith("CHAPTER 17"))): # SPECIAL CASE FOR TITLE 72 - all repealed I believe
            breakpos = (startpos + i)
            break

    tocPlist = plist[startpos:breakpos]
    bodyPlist = plist[breakpos:]
    name = stripTitleName(nameList)

    return titleNum, name, tocPlist, bodyPlist,





def stripTitleName(nameList):
    name = ""
    for line in nameList:
        if ("table of contents" in line.lower()): continue
        if line.strip() == "": continue
        name = name + " " + line
    name = name.strip()
    return name




def skipline_parseTOC(text):
    if "(Deleted by amendment)" in text: return True
    if "(Reserved)" in text: return True
    return False





