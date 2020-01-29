#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 19:24:01 2019

@author: dan
"""


### Imports

import re
from dateutil.parser import parse as parseDate

from OPparser_utils import numLowerCaseWords, isDate
from OPparser_lists import dateDecidedRe0, dateDecidedRe1, standardDateRe0, standardDateRe1



### Main Functions


def add_para_IDs(maintext):

    newtext = ""
    p_list = maintext.split("<p>")

    for i, para in enumerate(p_list):
        newtext = newtext + "<p id='p" + str(i) + "'>" + para

    return newtext



def splitLawbox(path):

    fullText = ''
    fns = ''
    mainText = ''

    with open (path, 'r') as file:
        fullText = file.read()

    # Get start location from Court line
    bodyStartPara = frontFromCourt(fullText)
    
    # LOWERCASE WORD COUNT!
    if bodyStartPara == -1:        
        for i, paragraph in enumerate(fullText.split('<p>')):
            modParagraph = paragraph.replace('<center>', '').replace('</center>', '').replace('<b>', '').replace('</b>', '').replace('<br>', '').replace('<h1>', '').replace('</h1>', '').replace('<div>', '').replace('and', '').replace('the', '').replace('of', '').replace('et al.', '')
            if numLowerCaseWords(modParagraph) > 6:
                bodyStartPara = i
                break

    if len(fullText.split('<p>')) > bodyStartPara: bodyStartLoc = fullText.find(fullText.split('<p>')[bodyStartPara])
    else:
        bodyStartLoc = 0
        print("HIT!")
    front = fullText[:bodyStartLoc]
    body = fullText[bodyStartLoc:]

    if '<h2>NOTES</h2>' in body:
        fns = body.split(sep='<h2>NOTES</h2>')[-1]
        mainText = body.split(sep='<h2>NOTES</h2>')[0]
    else:
        mainText = body

    #Delete some HTML
    mainText = mainText.replace('</div>', '')

    # Change all footnote anchors to our custom HTML format
    mainText = re.sub(r'\<sup\>\[(\d+)\]\<\/sup\>', r"<a href=#FNnumber\1 class='FNanchor' name='FNanchor\1'>\1</a>", mainText)

    return front, mainText, fns





def formatFootnotes_LB(fns):
    newFNs = fns
    for fnNumber in range(1, 1000):
        if ('<p>[' + str(fnNumber) + ']') in fns:
            newFNs = newFNs.replace('<p>[' + str(fnNumber) + ']', "<p><a href=#FNanchor" + str(fnNumber) + " class='FNnumber' name='FNnumber" + str(fnNumber) + "'>" + str(fnNumber) + ' </a>')
        else:
            break
    return newFNs





def getCourtJx_LB(front):

    court = ''
    jurisdiction = ''
    courtRank = 7

    #Delaware State Courts (Jurisdiction = Delaware)
    if '<center><p><b>Court of Chancery' in front:
        court = 'Court of Chancery'
        jurisdiction = 'Delaware'
        courtRank = 5
    elif '<center><p><b>Supreme Court of Delaware' in front:
        court = 'Supreme Court'
        jurisdiction = 'Delaware'
        courtRank = 4
    elif '<center><p><b>Superior Court of Delaware' in front:
        court = 'Superior Court'
        jurisdiction = 'Delaware'
        courtRank = 5
    elif '<center><p><b>Family Court of Delaware' in front:
        court = 'Family Court'
        jurisdiction = 'Delaware'
        courtRank = 6
    elif '<center><p><b>Delaware Court on the Judiciary' in front:
        court = 'Court on the Judiciary'
        jurisdiction = 'Delaware'
        courtRank = 6

    #Pennsylvania State Courts (Jurisdiction = Pennsylvania)
    elif '<center><p><b>supreme court of pennsylvania' in front.lower():
        court = 'Supreme Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 4
    elif '<center><p><b>Commonwealth Court of Pennsylvania' in front:
        court = 'Commonwealth Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 5
    elif '<center><p><b>Superior Court of Pennsylvania' in front:
        court = 'Superior Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 5
    elif '<center><p><b>Court of Judicial Discipline of Pennsylvania' in front:
        court = 'Court of Judicial Discipline'
        jurisdiction = 'Pennsylvania'
        courtRank = 6

    #Federal District Courts in the Third Circuit (Jurisdiction=United States)
    elif ('<center><p><b>United States District Court, D. Delaware' in front) or ('<center><p><b>United States District Court D. Delaware' in front) or ('District Court, D. Delaware' in front):
        court = 'District of Delaware'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, D. New Jersey' in front) or ('<center><p><b>District Court, D. New Jersey' in front) or ('<center><p><b>United States District Court D. New Jersey' in front):
        court = 'District of New Jersey'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, E.D. Pennsylvania' in front) or ('<center><p><b>United States District Court, E. D. Pennsylvania' in front) or ('<center><p><b>United States District Court E. D. Pennsylvania' in front) or ('<center><p><b>United States District Court, E. D. Pa.' in front) or ('<center><p><b>District Court, E. D. Pennsylvania' in front):
        court = 'Eastern District of Pennsylvania'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, M. D. Pennsylvania' in front) or ('<center><p><b>United States District Court, M.D. Pennsylvania' in front):
        court = 'Middle District of Pennsylvania'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, W. D. Pennsylvania' in front) or ('<center><p><b>United States District Court, W.D. Pennsylvania' in front) or ('<center><p><b>District Court, W. D. Pennsylvania' in front) or ('<center><p><b>United States District Court W. D. Pennsylvania' in front):
        court = 'Western District of Pennsylvania'
        jurisdiction = 'United States'
        courtRank = 3

    #Federal District Courts in the Second Circuit (Jurisdiction=United States)
    elif ('<center><p><b>United States District Court, S.D. New York' in front) or ('<center><p><b>District Court, S. D. New York' in front) or ('<center><p><b>United States District Court, S. D. New York' in front):
        court = 'Southern District of New York'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, E.D. New York' in front) or ('<center><p><b>United States District Court, E. D. New York' in front):
        court = 'Eastern District of New York'
        jurisdiction = 'United States'
        courtRank = 3
    elif ('<center><p><b>United States District Court, N.D. New York' in front):
        court = 'Northern District of New York'
        jurisdiction = 'United States'
        courtRank = 2
    elif ('<center><p><b>United States District Court, W.D. New York' in front) or ('<center><p><b>District Court, W. D. New York' in front) or ('<center><p><b>United States District Court, W. D. New York' in front):
        court = 'Western District of New York'
        jurisdiction = 'United States'
        courtRank = 2
    elif ('<center><p><b>United States District Court, D. Connecticut' in front) or ('<center><p><b>District Court, D. Connecticut' in front) or ('<center><p><b>United States District Court, D. Connecticut' in front):
        court = 'District of Connecticut'
        jurisdiction = 'United States'
        courtRank = 2
    elif ('<center><p><b>United States District Court, D. Vermont' in front) or ('<center><p><b>District Court, D. Vermont' in front) or ('<center><p><b>United States District Court, D. Vermont' in front):
        court = 'District of Vermont'
        jurisdiction = 'United States'
        courtRank = 2

    #Federal Circuit Courts and SCOTUS (Jurisdiction=United States)
    elif ('<center><p><b>Supreme Court of United States' in front):
        court = 'Supreme Court'
        jurisdiction = 'United States'
        courtRank = 1
    elif ('<center><p><b>Circuit Court of Appeals, Second Circuit' in front) or ('<center><p><b>United States Court of Appeals, Second Circuit' in front):
        court = 'Second Circuit'
        jurisdiction = 'United States'
        courtRank = 2
    elif ('<center><p><b>Circuit Court of Appeals, Third Circuit' in front) or ('<center><p><b>United States Court of Appeals, Third Circuit' in front):
        court = 'Third Circuit'
        jurisdiction = 'United States'
        courtRank = 2

    return court, jurisdiction, courtRank





def getDate_LB(front):

    if len(front) == 0: return ''

    dateString = ''
    date = ''
    dateList = []

    # First see if there is a "Date Decided" date, which is authoritative
    if dateDecidedRe0.search(front.lower()) != None:
        dateString = dateDecidedRe0.search(front.lower()).group()
    elif dateDecidedRe1.search(front.lower()) != None:
        dateString = dateDecidedRe1.search(front.lower()).group()

    # Second, if no authoritative phrase, make a list of all dates in frontmatter
    if len(dateString) == 0:
        if standardDateRe0.search(front.lower()) != None:
            dateList.append(standardDateRe0.search(front.lower()).group())
        if standardDateRe1.search(front.lower()) != None:
            dateList.append(standardDateRe1.search(front.lower()).group())
        # ARBITRARILY CHOOSES FIRST OF ALL DATES IN THE DATELIST
        if len(dateList) > 0: dateString = dateList[0]

    # LAST, if possible, convert final results of date search
    # into MySQL formatted date (string: 'yyyy-mm-dd')
    if isDate(dateString): 
        date = parseDate(dateString, fuzzy=True).date().isoformat()
    else: 
        date = "0001-01-01" # Default/None value must be in valid mysql format

    return date





def getCite1_LB(front):

    citation = ''

    citationStart = front.find('<center><b>') + 11
    citationEnd = front.find('</b></center>')

    if (citationStart > 0) and (citationEnd > citationStart):
        citation = front[citationStart:citationEnd]

    # Minor formatting, including removing the year parenthetical, which
    # appears to always be included in CourtListener lawbox files.
    citation = re.sub(r'\(\d\d\d\d\)', '', citation)
    citation = citation.lstrip().rstrip()

    return citation





### Sub Functions

def frontFromCourt(fullText):

    for i, para in enumerate(fullText.split('<p>')):
        if 'Superior Court of Pennsylvania' in para:
            return i + 1
        if 'Supreme Court of Pennsylvania' in para:
            return i + 1
        if 'Commonwealth Court of Pennsylvania' in para:
            return i + 1
        if 'Court of Judicial Discipline of Pennsylvania' in para:
            return i + 1
        if 'Court of Chancery of Delaware' in para:
            return i + 1
        if 'Superior Court of Delaware' in para:
            return i + 1
        if 'Supreme Court of Delaware' in para:
            return i + 1
        if 'Family Court of Delaware' in para:
            return i + 1
        if 'Delaware Court on the Judiciary' in para:
            return i + 1
        if 'Court on the Judiciary of Delaware' in para:
            return i + 1
        if ('United States District Court, E.D. Pennsylvania' in para) or ('United States District Court, E. D. Pennsylvania' in para) or ('United States District Court E. D. Pennsylvania' in para) or ('United States District Court, E. D. Pa.' in para) or ('District Court, E. D. Pennsylvania' in para):
            return i + 1
        if ('United States District Court, D. Delaware' in para) or ('District Court, D. Delaware' in para) or ('United States District Court D. Delaware' in para):
            return i + 1

    return -1 # Returns -1 if this fails



