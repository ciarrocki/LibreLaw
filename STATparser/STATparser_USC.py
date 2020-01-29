#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 09:22:05 2019

@author: dan
"""


import xml.etree.ElementTree as ET
import re


usc05 = '/home/dan/Data/USC/usc05.xml'
usc10 = '/home/dan/Data/USC/usc10.xml'






def getTOC_USC(filepath):
    root = getRoot_USC(filepath)
    toclist = []
    for e in root.iter():
        if 'toc' in e.tag:
            newtoc = []
            for i in e.iter():
                newtoc.append(i.text)
            toclist.append(newtoc)
    return toclist




def getSections_USC(filepath):
    contentRoot = getContentRoot_USC(filepath)
    sectionlist = []
    for e in contentRoot.iter():
        if tagStrip_USC(e.tag) == 'section': 
            newSection = {}
            if 'identifier' not in e.attrib.keys(): newSection['id'] = ""
            else: 
                if e.attrib['identifier'].startswith(r"/us/usc/"): newSection['id'] = e.attrib['identifier'][8:]
                else: newSection['id'] = e.attrib['identifier']
            for sectionEl in e:
                if tagStrip_USC(sectionEl.tag) == 'num': newSection['num'] = sectionEl.text
                if tagStrip_USC(sectionEl.tag) == 'heading': newSection['heading'] = sectionEl.text
                if tagStrip_USC(sectionEl.tag) == 'content':
                    newcontent = ""
                    for p in sectionEl:
                        if p.text != None: newcontent = newcontent + p.text + "<br>"
                        newSection["content"] = newcontent
            sectionlist.append(newSection)
    return sectionlist






def getChapters_USC(filepath):
    contentRoot = getContentRoot_USC(filepath)
    chapterlist = []
    for e in contentRoot.iter():
        if tagStrip_USC(e.tag) == 'chapter': chapterlist.append(e)
    return chapterlist




def getParts_USC(filepath):
    contentRoot = getContentRoot_USC(filepath)
    partlist = []
    for e in contentRoot:
        if tagStrip_USC(e.tag) == 'part': partlist.append(e)
    return partlist
    




def getContentRoot_USC(filepath):
    root = getRoot_USC(filepath)
    main = root[1]
    title = main[0]
    return title




def getRoot_USC(filepath):
    tree = ET.parse('/home/dan/Data/USC/usc05.xml')
    root = tree.getroot()
    return root




def tagStrip_USC(tagString):
    return re.sub(r"^\{.*\}", "", tagString)




    
    

