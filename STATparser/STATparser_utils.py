#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 09:06:12 2019

@author: dan
"""



### Imports

import os
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse as parseDate



### Paths
rawDataDir_DESTAT = "/home/dan/Data/DelawareGov/Statutes/Raw/"
proDataDir_DESTAT = "/home/dan/Data/DelawareGov/Statutes/Processed/"
compressedDataDir_USC = "/home/dan/Data/USC/Compressed/"
rawDataDir_USC = "/home/dan/Data/USC/Raw/"
proDataDir_USC = "/home/dan/Data/USC/Processed/"
dataDir_PAlegis = '/home/dan/Data/Legis/Pennsylvania/'
rawDataDir_DERULES = '/home/dan/Data/DelawareGov/Rules/Raw/'
proDataDir_DERULES = '/home/dan/Data/DelawareGov/Rules/Processed/'
rawDataDir_PARULES = '/home/dan/Data/PACodeBulletin/Raw/'
proDataDir_PARULES = '/home/dan/Data/PACodeBulletin/Processed/'


chromeDriver = "/home/dan/ChromeDriver/chromedriver"



### Data URLs
seed_DESTAT = "https://delcode.delaware.gov"
seed_USC = "https://uscode.house.gov/download/download.shtml"
seed_PAlegis = "https://www.legis.state.pa.us/cfdocs/legis/LI/Public/cons_index.cfm"
seed_PAlegis_unconsolidated = "https://www.legis.state.pa.us/cfdocs/legis/LI/Public/ucons_index.cfm"
seed_DErules = "https://courts.delaware.gov/rules/"
seed_PArules_RCPgeneral = "http://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/231/partItoc.html"
seed_PArules_RCrimGeneral = "https://www.pacodeandbulletin.gov/Display/pacode?titleNumber=234&file=/secure/pacode/data/234/234toc.html"
seed_PArules_PARE = "http://www.pacodeandbulletin.gov/Display/pacode?titleNumber=225&file=/secure/pacode/data/225/225toc.html"
seed_PArules_appellate1 = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/210/articleII_toc.html&d=reduce"
seed_PArules_appellate2 = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/210/articleIII_toc.html&d=reduce"
seed_PArules_appellate3 = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/210/articleIIII_toc.html&d=reduce"
seed_PArules_JUVR1 = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/237/subpartIAtoc.html"
seed_PArules_JUVR2 = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/237/subpartIBtoc.html"
seed_PArules_MCCR = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/246/partItoc.html"
seed_PArules_RPROF = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/204/subpartVAtoc.html"
seed_PArules_RADM = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/204/partIVtoc.html"
seed_PArules_SENTG = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/204/partVIIItoc.html"

### RegexestitleNumber
badCharRE = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)




### Functions

def getFileList(path, ext='', recursive=False):
    fileList = []
    if not path.endswith('/'): path = path + '/'
    if recursive:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(ext): fileList.append(str(os.path.join(root, file)))
    else:
        fileList = [path + file for file in os.listdir(path)\
                    if os.path.isfile(os.path.join(path, file)) and file.endswith(ext)]
    return fileList





def getSoup(filepath):
    file = open(filepath, 'r')
    soup = BeautifulSoup(file, 'lxml')
    file.close()
    return soup





def loadLines_text_rules(filePath):

    lineList = []

    with open(filePath, 'rb') as textFile:
        textFile.seek(0)
        for newLine in textFile:
            newLine = newLine.replace(b'\xf3\xa0\x84\x8c', b'') # Very weird character; APPEARS ONLY ONCE: 'Pennsylvania/Superior/withCitations/4368527.html'
            decodedLine = newLine.decode('utf8').replace(r'\xa0', r' ') #Sometimes the reader generates files with "\xa0" instead of normal spaces
            decodedLine = badCharRE.sub("~", decodedLine) # Remove characters that cause problems for mysql (mainly 4+ byte characters, I think?)  NOTE: I ALREADY MADE SURE EVERYTHING IS UTF8mb4
            lineList.append(decodedLine)

    return lineList



def getDate(text):
    match = re.search(r"[a-z]{2,12}\.?\s?\d{1,2}\,\s?\d{2,4}", text.lower())
    if match: 
        try:
            return parseDate(match[0])
        except ValueError:
            return ""
    return ""






sectionGrabbers_destat = {r"^Title\s\d{1,3}\s":"Title",
                   r"^Chapter\s\d{1,3}([A-Z])?":"Chapter", 
                   r"^Subchapter\s[I|V|X|L|C|D|M]+":"Subchapter",
                   r"^Subtitle\s[I|V|X|L|C|D|M]+":"Subtitle",
                   r"^§\s\d+[A-Z]?(\-\d{1,5})?\s":"Section",
                   #r"^Part\s(([I|V|X|L|C|D|M]+)|(\d{1,3}))":"Part",
                   r"^Part\s(([I|V|X|L|C|D|M]+))":"Part",
                    r"^Part\s(\d{1,3})":"Part_",
                   r"^Article\s\d{1,3}([A-Z])?":"Article",}

sectionNumbers_destat = {"Title":r"Title\s(\d{1,3})",
                  "Chapter":r"Chapter\s(\d{1,3}([A-Z])?)",
                  "Subchapter":r"Subchapter\s([I|V|X|L|C|D|M]+)",
                  "Subtitle":r"Subtitle\s([I|V|X|L|C|D|M]+)",
                  "Section":r"^§\s(\d+[A-Z]?(\-\d{1,5})?)\s",
                  #"Part":r"^Part\s(([I|V|X|L|C|D|M]+)|(\d{1,3}))",
                  "Part":r"^Part\s(([I|V|X|L|C|D|M]+))",
                  "Part_":r"^Part\s(\d{1,3})",
                  "Article":r"Article\s(\d{1,3}([A-Z])?)",}
