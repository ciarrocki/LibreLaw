#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 19:15:30 2019

@author: dan
"""


### IMPORTS

import re
import os

import psycopg2
from bs4 import BeautifulSoup
from dateutil.parser import parse as parseDate

from CiteVista_patterns import citePatterns_all


### PATHS

corporaDir = "/home/dan/Data/CiteVista/Corpora/"
WLrawCitesDir = "/home/dan/Data/CiteVista/rawWL/"
CiteMatrixDir = "/home/dan/Data/CiteVista/CiteMatrix/"

password = open("/home/dan/LibreLaw/config").read()[:-1]


def save_text_all(jurisdiction="DE", mode="html"):
    """
    Saves text of all court docs for specified jurisdiction into files in
    local environment.  Each opinion is saved as an individual text or html
    file in an appropriate jurisdicion-court subfolder in the corpus directory.

    mode=="pure": removes footnote numbers and anchor numbers; removes all html tags
    mode=="html": preserves all html tags; preserves footnotes numbers and anchors    
    """
    
    conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
    cur = conn.cursor()

    if (jurisdiction == "Delaware") or (jurisdiction == "DE"): jxstr = "Delaware_decourtdoc"
    elif (jurisdiction == "Pennsylvania") or (jurisdiction == "PA"): jxstr = "Pennsylvania_pacourtdoc"
    elif (jurisdiction == "Federal") or (jurisdiction == "US"): jxstr = "Federal_uscourtdoc"
    else:
        print("Invalid Jurisdiction.")
        return False

    sql = "SELECT * FROM \"" + jxstr + "\";"
    cur.execute(sql)

    for result in cur:
        
        savedir = getDataPath(court = result[3], jurisdiction = result[2], mode=mode)
        if not os.path.exists(savedir): os.makedirs(savedir)
        maintext = result[12]
        footnotes = result[13]

        if mode == "pure":
            maintext = re.sub("\<a\shref\=\'\#.*?\/a\>", "", maintext)
            footnotes = re.sub("\<a\shref\=\'\#.*?\/a\>", "", footnotes)
            soup1 = BeautifulSoup(maintext)
            soup2 = BeautifulSoup(footnotes)
            maintext = soup1.get_text()        
            footnotes = soup2.get_text()
            final_string = "<<MAINTEXT>> " + maintext + " <<FOOTNOTES>> " + footnotes
            save_path = savedir + str(result[0]) + ".txt"

        elif mode == "html":
            final_string = maintext + " | " + footnotes
            save_path = savedir + str(result[0]) + ".html"
    
        else:
            print("Invalid save mode.")
            return False
    
        with open(save_path, 'w') as file:
            file.write(final_string)
    
    return True






def getDocCites(text, patternset=citePatterns_all):    
    
    # Get all cites using the full patternset
    citeList = []
    for pattern in patternset:    
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            citeList.append(match)
    
    # Remove unwanted patterns
    tempList = []
    for match in citeList:
        if match.span()[1] + 6 >= len(text): continue
        startPos = match.span()[1] - 2
        evalText = text[startPos:startPos+8]
        if re.search(r"\.\d{1,3}d\s*at\s*\d+", evalText, flags=re.IGNORECASE): continue # Addresses cases like "991 A.2d at 556"
        tempList.append(match)
    citeList = tempList
    
    return citeList





def get_text(idnum, mode="html"):
    
    conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
    cur = conn.cursor()
    cur.execute("SELECT * FROM \"Delaware_decourtdoc\" WHERE ID=" + str(idnum) + ";")
    result = cur.fetchone()

    maintext = result[12]    
    footnotes = result[13]    

    # Remove all footnote numbers and HTML tags
    if (mode == "pure"):
        maintext = re.sub("\<a\shref\=\'\#.*?\/a\>", "", maintext)
        soup = BeautifulSoup(maintext)
        maintext = soup.get_text()
        footnotes = re.sub("\<a\shref\=\'\#.*?\/a\>", "", footnotes)
        soup = BeautifulSoup(footnotes)
        footnotes = soup.get_text()

    conn.close()

    return maintext, footnotes







def getDataPath(court='Court of Chancery', jurisdiction='Delaware', mode='html'):
    
    if (jurisdiction=='Delaware') or (jurisdiction=='DE'): 
        jxPath = 'Delaware'
        if court == 'Court of Chancery': courtPath = 'Chancery'
        elif court == 'Supreme Court': courtPath = 'Supreme'
        elif court == 'Superior Court': courtPath = 'Superior'
        elif court == 'Court of Common Pleas': courtPath = 'CommonPleas'
        elif court == 'Family Court': courtPath = 'Family'
        elif court == 'Court on the Judiciary': courtPath = 'Judicial'
        else: 
            print('Invalid court:', court)
            return ''

    elif (jurisdiction == 'Pennsylvania') or (jurisdiction=='PA'):
        jxPath = 'Pennsylvania'
        if court == 'Commonwealth Court': courtPath = 'Commonwealth'
        elif court == 'Supreme Court': courtPath = 'Supreme'
        elif court == 'Superior Court': courtPath = 'Superior'
        elif court == 'Court of Judicial Discipline': courtPath = 'Judicial'
        else:
            print('Invalid court:', court)
            return ''

    elif (jurisdiction=='United States') or (jurisdiction == 'Federal') or (jurisdiction=='US'):
        jxPath = 'Federal'
        if (court == 'Supreme Court') or (court == 'SCOTUS'): courtPath = 'scotus'
        elif court == 'Second Circuit': courtPath = 'ca2'
        elif court == 'Third Circuit': courtPath = 'ca3'
        elif court == 'District of Delaware': courtPath = 'ded'
        elif court == 'District of New Jersey': courtPath = 'njd'
        elif court == 'Eastern District of Pennsylvania': courtPath = 'paed'
        elif court == 'Middle District of Pennsylvania': courtPath = 'pamd'
        elif court == 'Western District of Pennsylvania': courtPath = 'pawd'
        else:
            print('Invalid court:', court)
            return ''

    else:
        print("Invalid jurisdiction:", jurisdiction)
        return ''

    if mode == 'html': modestring = 'html'
    elif mode == 'pure': modestring = 'puretext'
    else:
        print("Invalid mode:", mode)
        return ''

    path = corporaDir + modestring + '/' + jxPath + '/' + courtPath + '/'
    return path





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




def isDate(string):    
    try:
        parseDate(string, fuzzy=True).date().isoformat()
        return True
    except:
        return False
