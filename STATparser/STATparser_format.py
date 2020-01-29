#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 22:36:55 2019

@author: dan
"""


import re



def formatSections_DE(sections):
    newSections = []
    for sec in sections:
        newSect = {}
        newSect['sectiontype'] = sec['sectiontype']
        newSect['number'] = sec['number']
        newSect['title'] = sec['title']
        newSect['sectionstack'] = sec['sectionstack']
        newSect['text'] = formatSecText(sec['text'])
        newSections.append(newSect)
    
    return newSections




def formatSecText(linelist):
    text = "<p>"
    sectionStack = []

    for i, line in enumerate(linelist):
        
        proline = line.strip().replace('\n', ' ')
        
        # New paragraph for section history (DE statutes)
        if re.search(r"\(\d\sdel\.\sc\.\s\d{4}\,\s\§\s\d{2,5}", proline.lower()):
            pos = re.search(r"\(\d\sdel\.\sc\.\s\d{4}\,\s\§\s\d{2,5}", proline.lower()).span()[0]
            proline = proline[:pos] + "</p><p>" + proline[pos:]

        # New paragraph for explanatory notes (PA rules)
        if (proline == "Explanatory Note"):
            if linelist[i-1].strip() == "":
                proline = "</p><p>Explanatory Note</p><p>"

        # New paragraph for official notes (PA rules of civil procedure, e.g.)
        if proline.startswith("Official Note:"):
            if linelist[i-1].strip() == "":
                proline = proline.replace("Official Note:", "</p><p>Official Note:</p><p>")

        # New paragraph for source (PA rules)
        if (proline == "Source"):
            if linelist[i-1].strip() == "":
                proline = "</p><p>Source</p><p>"

        # New paragraph for comments (PA Rules of Evidence)
        if (proline == "Comment"):
            if linelist[i-1].strip() == "":
                proline = "</p><p>Comment</p><p>"

        # New paragraph for Committee Explanatory Reports (PA Rules of Evidence)
        if (proline == "Committee Explanatory Reports:"):
            if linelist[i-1].strip() == "":
                proline = "</p><p>Committee Explanatory Reports:</p><p>"

        # Determine whether or not this line STARTS A NEW PARAGRAPH
        sLevel = getSectionLevel(proline, sectionStack)
        
        # Add text to big string
        if sLevel > 0: text = text + "</p><p>" + proline
        else: text = text + " " + proline
    
    text = text + "</p>"

    return text




### -------------------------------------------------------------





def getSectionLevel(line, sectionStack):
    proline = line.lower()
    if re.search(r"^\([a-z]\)\s", proline): return 1
    if re.search(r"^\(\d\)\s", proline): return 1

    if re.search(r"^\(a{2,3}\)\s", proline): return 1

    if re.search(r"^\(ii\)\s", proline): return 1
    if re.search(r"^\(iii\)\s", proline): return 1
    if re.search(r"^\(iv\)\s", proline): return 1
    if re.search(r"^\(v\)\s", proline): return 1
    if re.search(r"^\(vi\)\s", proline): return 1
    if re.search(r"^\(vii\)\s", proline): return 1
    if re.search(r"^\(viii\)\s", proline): return 1
    if re.search(r"^\(ix\)\s", proline): return 1
    if re.search(r"^\(x\)\s", proline): return 1
    if re.search(r"^\(xii\)\s", proline): return 1
    
    return 0








def addPrevNext_DE(sections, titleNum):

    newSections0 = []
    prevSection = 0
    prevTitle = ""
    for section in sections:
        newSection = section
        if prevSection == 0:
            prevLink = ""
        else:
            prevLink = "<a href='/Delaware/statutes/" + titleNum + "/" + "'>" + "§ " + prevSection + " - " + prevTitle + "</a>"
        newSection['previous'] = prevLink
        newSections0.append(newSection)
        if section['sectiontype'] == 'Section': 
            prevSection = section['number']
            prevTitle = section['title']

    newSections1 = []
    nextSection = 0
    nextTitle = ""
    for section in reversed(newSections0):
        newSection = section
        if nextSection == 0:
            nextLink = ""
        else:
            nextLink = "<a href='/Delaware/statutes/" + titleNum + "/" + nextSection + "'>" + "§ " + nextSection + " - " + nextTitle + "</a>"
        newSection['next'] = nextLink
        newSections1.append(newSection)
        if section['sectiontype'] == 'Section':
            nextSection = section['number']
            nextTitle = section['title']

    newSections2 = [section for section in reversed(newSections1)]

    return newSections2