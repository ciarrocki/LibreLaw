#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 07:46:52 2019

@author: dan
"""


### Imports

from dateutil.parser import parse as parseDate
from OPparser_utils import isDate, flatten
from OPparser_lists import dateDecidedRe0, dateDecidedRe1, dateFiledRe0, dateDatedRe0, dateDatedRe1, dateDatedRe2, finalReportDateRe0, standardDateRe0, standardDateRe1





### Main Functions

def parseFront_text(front, lastPage):
    
    date = getDate_text(front, lastPage)
    court, jurisdiction, courtRank = getCourtJurisdiction_text(front)
    
    return date, court, jurisdiction, courtRank





### Sub Functions


def getDate_text(front, lastPage):

    #Flatten front; when split by WC splitter, it comes out as a list of strings
    front = flatten(front)    
    if len(front) == 0: return ''

    dateString = ''
    date = ''
    dateList = []

    # First, see if there is a "Date Decided" date, which is authoritative
    if dateDecidedRe0.search(front.lower()) != None: 
        dateString = dateDecidedRe0.search(front.lower()).group()
    elif dateDecidedRe1.search(front.lower()) != None:
        dateString = dateDecidedRe1.search(front.lower()).group()

    # Second, see if there is a 'FILED' date (note this one is case sensitive, so no .lower())
    if len(dateString) == 0:
        if dateFiledRe0.search(front) != None:
            dateString = dateFiledRe0.search(front).group()

    # Third, see if there is a 'Dated:" date in the frontmatter
    if len(dateString) == 0:
        if dateDatedRe0.search(front.lower()) != None: 
            dateString = dateDatedRe0.search(front.lower()).group()
        elif dateDatedRe1.search(front.lower()) != None:
            dateString = dateDatedRe1.search(front.lower()).group()

    # Fourth, see if there is a 'Final Report:" date in the frontmatter
    if len(dateString) == 0:
        if finalReportDateRe0.search(front.lower()) != None: 
            dateString = finalReportDateRe0.search(front.lower()).group()

    # Fifth, see if there is a 'Dated:" or ("Date:") date in the last page
    back = flatten(lastPage)    
    if len(dateString) == 0:
        if dateDatedRe0.search(back.lower()) != None: 
            dateString = dateDatedRe0.search(back.lower()).group()
        elif dateDatedRe1.search(back.lower()) != None:
            dateString = dateDatedRe1.search(back.lower()).group()
        elif dateDatedRe2.search(back.lower()) != None:
            dateString = dateDatedRe2.search(back.lower()).group()

    # Sixth, if no authoritative phrase, make a list of all dates in frontmatter
    if len(dateString) == 0:
        if standardDateRe0.search(front.lower()) != None: 
            dateList.append(standardDateRe0.search(front.lower()).group())
        if standardDateRe1.search(front.lower()) != None: 
            dateList.append(standardDateRe1.search(front.lower()).group())
        # ARBITRARILY CHOOSES FIRST OF ALL DATES IN THE DATELIST
        if len(dateList) > 0: dateString = dateList[0]

    # LAST, if possible, convert final results of date search 
    # into MySQL formatted date (string: 'yyyy-mm-dd')
    if isDate(dateString): date = parseDate(dateString, fuzzy=True).date().isoformat()
    else: date = '0001-01-01' # Default date must be compliant with mysql date format

    return date



def getCourtJurisdiction_text(front):

    #Flatten front; when split by WC splitter, it comes out as a list of strings
    front = flatten(front)

    court = ''
    jurisdiction = ''
    courtRank = 7

    if 'in the court of chancery of the state of delaware' in front.lower():
        court = 'Court of Chancery'
        jurisdiction = 'Delaware'
        courtRank = 5
    elif 'court of chancery courthouse' in front.lower():
        court = 'Court of Chancery'
        jurisdiction = 'Delaware'
        courtRank = 5
    elif ('court of chancery' in front.lower()) and ('new castle county courthouse' in front.lower()):
        court = 'Court of Chancery'
        jurisdiction = 'Delaware'
        courtRank = 5
    elif len(front) > 300:
        if ('court of chancery' in front.lower()[:300]) and ('of the' in front.lower()[:300]) and ('state of delaware' in front.lower()[:300]):
            court = 'Court of Chancery'
            jurisdiction = 'Delaware'
            courtRank = 5

    if 'in the superior court of the state of delaware' in front.lower():
        court = 'Superior Court'
        jurisdiction = 'Delaware'
        courtRank = 5

    if 'in the supreme court of the state of delaware' in front.lower():
        court = 'Supreme Court'
        jurisdiction = 'Delaware'
        courtRank = 4

    if 'in the court of common pleas of the state of delaware' in front.lower():
        court = 'Court of Common Pleas'
        jurisdiction = 'Delaware'
        courtRank = 5

    if 'in the supreme court of pennsylvania' in front.lower():
        court = 'Supreme Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 4

    if 'in the commonwealth court of pennsylvania' in front.lower():
        court = 'Commonwealth Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 5

    if ('in the superior court' in front.lower()) and ('commonwealth of pennsylvania' in front.lower()):
        court = 'Superior Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 5
    elif 'inthesuperiorcourtofpennsylvania' in front.lower().replace(' ', '').replace('\n', ''):
        court = 'Superior Court'
        jurisdiction = 'Pennsylvania'
        courtRank = 5
    elif 'in the superior court of' in front.lower():
        pos = front.lower().find('in the superior court of')
        if 'pennsylvania' in front[pos:pos+125].lower():
            court = 'Superior Court'
            jurisdiction = 'Pennsylvania'
            courtRank = 5

    

    if ('court of appeals' in front.lower()) and (('second circuit') in front.lower()):
        court = "Second Circuit"
        jurisdiction = "Federal"
        courtRank = 2

    if ('court of appeals' in front.lower()) and (('third circuit') in front.lower()):
        court = "Second Circuit"
        jurisdiction = "Federal"
        courtRank = 2



    return court, jurisdiction, courtRank



