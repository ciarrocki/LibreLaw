#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:35:53 2019

@author: dan
"""


### Imports

from OPparser_utils import deleteSepLines, getFileList
from OPparser_text_bodySplitter import loadLines_text, splitBodyFront_text, isFormFeed, checkLL, splitPages_FF, deletePageHeaders, deletePageNumbers, deleteHTML, deleteMisc, deleteEmptyEndPages
from OPparser_text_FNsplitter import splitFootnotes
from OPparser_text_formatMainText import formatMainText_text
from OPparser_text_parseFront import parseFront_text
from OPparser_text_formatFNs import formatFootnotes_text
from OPparser_text_parties import getParties_text
from OPparser_lawbox import splitLawbox, formatFootnotes_LB, getCourtJx_LB, getCite1_LB, getDate_LB, add_para_IDs
from OPparser_lawbox_parties import getRawParties_LB, getParties_LB
from OPparser_toDjango import saveOpToDjango



### Main Functions



def parseAndSaveOP_all(jx='DE'):
    """
    Script to proccess all downloaded files and save them into the database
    """
    
    if jx == 'DE':
        flist1 = getFileList("/home/dan/Data/CourtListener/Processed/Delaware", ".clwc", True)
        flist2 = getFileList("/home/dan/Data/CourtListener/Processed/Delaware", ".cltx", True)
        flist3 = getFileList("/home/dan/Data/DelawareGov/Processed/", ".detx", True)
        flist_tx = flist1 + flist2 + flist3
        flist_lb = getFileList("/home/dan/Data/CourtListener/Processed/Delaware", ".cllb", True)
        for f in flist_tx:
            parseAndSaveOP_text(f)        
        for f in flist_lb:
            parseAndSaveOP_LB(f)


    if jx == 'PA':
        flist1 = getFileList("/home/dan/Data/CourtListener/Processed/Pennsylvania", ".clwc", True)
        flist2 = getFileList("/home/dan/Data/CourtListener/Processed/Pennsylvania", ".cltx", True)
        flist_tx = flist1 + flist2
        flist_lb = getFileList("/home/dan/Data/CourtListener/Processed/Pennsylvania", ".cllb", True)
        for f in flist_tx:
            parseAndSaveOP_text(f)
        for f in flist_lb:
            parseAndSaveOP_LB(f)

    # ONLY DOES LB OPINIONS
    # EXPAND TO INCLUDE SECOND AND THIRD CIRCUIT WC FILES
    if jx == 'US':
        flist_lb = getFileList("/home/dan/Data/CourtListener/Processed/Federal", ".cllb", True)
        print("Parsing", len(flist_lb), " US opinion files. Completed: ", end='')
        for i, f in enumerate(flist_lb):
            if i % 1000 == 0: print(i, " . . . ", end='')
            parseAndSaveOP_LB(f)
        print("Done.")

    return True





def parseAndSaveOP_text(filePath):
    data = parseOP_text(filePath)
    saveOpToDjango(data)
    return True





def parseAndSaveOP_LB(filePath):
    data = parseOP_LB(filePath)
    saveOpToDjango(data)
    return True





def parseOP_text(filePath, verbose=0):
    """
    Script to parse plain text file; these are raw text files from court 
    listener, from the Delaware government website, or any text file
    """

    # 1. Initial check of file type
    if filePath.endswith(".clwc"): source = "CLWC"
    elif filePath.endswith(".cltx"): source = "CLTX"
    elif filePath.endswith(".detx"): source = "DETX"
    else:
        data = {"filepath":filePath}
        print("Cannot parse: invalid file")
        return data

    # 2. Load raw text lines
    lineList = loadLines_text(filePath)
    if not checkLL(lineList):
        data = {"filepath":filePath, "linelist":lineList, "source":source}
        print("Cannot parse: file contains no text")
        return data

    # 3. Split raw text lines into front and rawbody
    splitStatus, front, rawBody = splitBodyFront_text(lineList)
    if not isFormFeed(rawBody):
        data = {"filepath":filePath, "linelist":lineList, "splitstatus":splitStatus, 
                "front":front, "rawbody":rawBody, "source":source}
        print("Cannot parse: pages not separated by form feed characters")
        return data

    # 4. Process rawbody into bodytext    
    rawBody = splitPages_FF(rawBody)
    body = deletePageHeaders(rawBody)    
    body = deletePageNumbers(body)
    body = deleteHTML(body)
    body = deleteMisc(body)
    body = deleteSepLines(body)
    body = deleteEmptyEndPages(body)

    # 5. Split footnotes; format maintext and footnotes
    bodytext, footnotes = splitFootnotes(body, verbose)
    maintext = formatMainText_text(bodytext, footnotes, verbose)
    finalFNs = formatFootnotes_text(footnotes)

    # 6. Extract data from front (also use the body for date in case it is not found in the front)
    if body == []: body = ['']
    date, court, jurisdiction, courtRank = parseFront_text(front, body[-1])
    parties, casename, fullcaption = getParties_text(front)

    # 7. Save to dictionary
    data = {"source":source, "front":front, "maintext":maintext, 
            "footnotes":finalFNs, "court":court, "jurisdiction":jurisdiction, 
            'courtrank':courtRank, "partylist":parties, "casename":casename, 
            "fullcaption":fullcaption, "date":date, "filepath":filePath,
            "body":bodytext, 'oldfn':footnotes, 'rawbody': rawBody}

    return data





def parseOP_LB(filePath):
    """
    Script to parse 'lawbox' opinion type from court listener; these are 
    very well-formatted html files.  When available, use lawbox opinions.
    """
    source = "CLLB"
    front, maintext, rawFNs = splitLawbox(filePath)
    maintext = add_para_IDs(maintext)
    rawparties = getRawParties_LB(front)
    partylist, casename = getParties_LB(rawparties)
    footnotes = formatFootnotes_LB(rawFNs)
    court, jurisdiction, courtRank = getCourtJx_LB(front)
    citation1 = getCite1_LB(front)
    date = getDate_LB(front)
    if date == "": date = "0001-01-01" # Default/None value must be in valid mysql format

    data = {"source":source, "front":front, "maintext":maintext, 
            "footnotes":footnotes, "court":court, "jurisdiction":jurisdiction, 'courtrank':courtRank, 
            "citation1":citation1, "partylist":partylist, "casename":casename, 
            "fullcaption":rawparties, "date":date, "filepath":filePath}

    return data







