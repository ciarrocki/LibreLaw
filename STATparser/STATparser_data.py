#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 09:45:24 2019

@author: dan
"""

### Imports

import zipfile
import subprocess
import requests
import re
import os
import random
import time
from selenium import webdriver
from bs4 import BeautifulSoup

from STATparser_utils import chromeDriver, getFileList, getDate

from STATparser_utils import seed_DESTAT, rawDataDir_DESTAT, proDataDir_DESTAT
from STATparser_utils import seed_USC, compressedDataDir_USC, rawDataDir_USC
from STATparser_utils import seed_PAlegis, dataDir_PAlegis, seed_PAlegis_unconsolidated
from STATparser_utils import seed_DErules, rawDataDir_DERULES, proDataDir_DERULES, rawDataDir_PARULES, proDataDir_PARULES
from STATparser_utils import seed_PArules_RCPgeneral, seed_PArules_RCrimGeneral, seed_PArules_PARE, seed_PArules_appellate1, seed_PArules_appellate2, seed_PArules_appellate3
from STATparser_utils import seed_PArules_JUVR1, seed_PArules_JUVR2, seed_PArules_MCCR, seed_PArules_RPROF, seed_PArules_RADM, seed_PArules_SENTG


from STATparser_toDjango import savePAunconsolidated





### Main Functions

# Downloads All USC Data - OVERWRITES
def getData_USC():
    downloadCompressedData_USC()
    extractData_USC()
    return True


# Downloads All DE Stat Data - OVERWRITES
def getData_DEstat():
    downloadRawData_DEstat()
    processRawData_DEstat()
    return True


def getData_PAlegis():
    downloadData_PAlegis()
    return True

# Downloads All DE rules Data - OVERWRITES
def getData_DErules():
    downloadRawData_DErules()
    processRawData_DErules()
    return True



### Sub Functions


def downloadData_PAlegis():
    
    # Get links to all of the PA titles in HTML
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_PAlegis)
    HTMLlinks = [element.get_attribute("href") for element in browser.find_elements_by_xpath("//a[contains(., 'HTML')]")]
    
    # Save the content from each of the links (have to do it this way; iframe nonsense)
    for l in HTMLlinks:
        browser.get(l)
        link = browser.find_element_by_tag_name("iframe").get_attribute("src")
        resp = requests.get(link)
        titleNum = re.search(r"ttl\=(\d{1,2})", l)[1]
        savepath = dataDir_PAlegis + "title" + str(titleNum) + ".html"
        with open(savepath, 'wb') as file: #Need to open as binary file
            file.write(resp.content)

    browser.quit()
    return True





def downloadRawData_DEstat():

    # Get links to all of the DE statute PDFs
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_DESTAT)
    elements = browser.find_elements_by_tag_name('a')
    links = [element.get_attribute('href') for element in elements]
    links = [link for link in links if link.endswith(".pdf")]
    browser.quit()

    # Download the PDFs
    for link in links:
        filename = link.split('/')[-1]
        filepath = rawDataDir_DESTAT + filename
        resp = requests.get(link)
        with open(filepath, 'wb') as file: #Need to open as binary file
            file.write(resp.content)

    return True




def processRawData_DEstat():
    proList = getFileList(rawDataDir_DESTAT, ext=".pdf", recursive=True)
    for f in proList:
        savePDFtext_stat(f)
    return True




def savePDFtext_stat(filePath):
    """
    Uses the PDFminer pdf2txt.py command-line utility to save the text of
    DelawareGov statutes to text files.

    Example of a command that this method executes:
    pdf2txt.py -t text -o "/home/dan/Data/DelawareGov/Statutes/Processed/title8.sttx" "/home/dan/Data/DelawareGov/Statutes/Raw/title8.pdf"
    """

    fileName = filePath.split('/')[-1]
    if fileName.endswith(".pdf"): fileName = fileName[:-4]
    savePath = proDataDir_DESTAT + '/' + fileName + ".txt"
    command = "pdf2txt.py -t text -o " + savePath + " " + filePath
    #print("\n***COMMAND:", command)
    subprocess.call(command, shell=True) # shell=True is necessary for command as single-string with arguments; might be a better way to do this???

    return True





def savePDFtext_DErules(filePath):
    """
    Uses the PDFminer pdf2txt.py command-line utility to save the text of
    DelawareGov statutes to text files.

    Example of a command that this method executes:
    pdf2txt.py -t text -o "/home/dan/Data/DelawareGov/Statutes/Processed/title8.sttx" "/home/dan/Data/DelawareGov/Statutes/Raw/title8.pdf"
    """
    fileName = filePath.split('/')[-1]
    if fileName.endswith(".pdf"): fileName = fileName[:-4]
    savePath = proDataDir_DERULES + '/' + fileName + ".txt"
    command = "pdf2txt.py -t text -o " + savePath + " " + filePath
    #print("\n***COMMAND:", command)
    subprocess.call(command, shell=True) # shell=True is necessary for command as single-string with arguments; might be a better way to do this???

    return True



def savePDFtext_PArules(filePath):
    """
    Uses the PDFminer pdf2txt.py command-line utility to save the text of
    DelawareGov statutes to text files.

    Example of a command that this method executes:
    pdf2txt.py -t text -o "/home/dan/Data/DelawareGov/Statutes/Processed/title8.sttx" "/home/dan/Data/DelawareGov/Statutes/Raw/title8.pdf"
    """
    fileName = filePath.split('/')[-1]
    if fileName.endswith(".pdf"): fileName = fileName[:-4]
    savedir = proDataDir_PARULES + '/' + filePath.split('/')[-2] + '/'
    if not os.path.exists(savedir): os.makedirs(savedir)
    savePath = savedir + fileName + '.txt'
    command = "pdf2txt.py -t text -o " + savePath + " " + filePath
    #print("\n***COMMAND:", command)
    subprocess.call(command, shell=True) # shell=True is necessary for command as single-string with arguments; might be a better way to do this???

    return True





def downloadCompressedData_USC():
    # Get link to xml zip archive of all USC titles
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_USC)
    alltitles = browser.find_element_by_css_selector("[title='All USC Titles in XML']")
    link = alltitles.get_attribute("href")
    browser.quit()
    
    # Download the zip file to the compressedDataDir_USC path
    filepath = compressedDataDir_USC + "alltitles.zip"
    resp = requests.get(link)
    with open(filepath, 'wb') as file:     # Need to open as binary file
        file.write(resp.content)
    
    return True




def extractData_USC():    
    with zipfile.ZipFile(compressedDataDir_USC + "alltitles.zip", 'r') as zip_ref:
        zip_ref.extractall(rawDataDir_USC)    
    return True





def DLandSave_PAlegis_unconsolidated(yearlist=[2019]):
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_PAlegis_unconsolidated)
    allYearLinkElements = browser.find_elements_by_css_selector(".DataTable a")

    # Restrict list of years to those specified in input (where they are available)
    finalYearLinks = [yearEl.get_attribute('href') for yearEl in allYearLinkElements
                     if int(re.sub(r"[^0-9]", "", yearEl.text)) in yearlist]

    for yearlink in finalYearLinks:

        browser.get(yearlink)
        acts = browser.find_elements_by_partial_link_text("Acts on General Legislation Approved")
        if len(acts) > 0: acts[0].click()
     
        table = browser.find_element_by_class_name('DataTable') 
        headers, rows = getTableData(table)
        
        # Convert last selenium element to raw link
        rows = [[row[0], row[1], row[2], row[3], row[4], row[5].get_attribute('href')] for row in rows]

        for row in rows:
            
            # Load data from big table for whole year (list of acts)
            year = row[0]
            act = row[1]
            PL = row[2]
            titlenum = row[3]
            title = row[4]
        
            # Go to the specific act we are interestedin
            browser.get(row[5])

            # If available, click on the link to HTML version of act
            htmlLinks = browser.find_elements_by_partial_link_text("HTML")
            if len(htmlLinks) > 0: htmlLinks[0].click()
            else: 
                print("No HTML Link - skipping act")
                continue

            # Load the data from the iframe (ugh)
            link = browser.find_element_by_tag_name("iframe").get_attribute("src")
            resp = requests.get(link)
            actContent = resp.content.decode()

            # parse out the content with BeautifulSoup
            soup = BeautifulSoup(actContent)
            paragraphs = soup.find_all("p")
            toptable = soup.find("table")

            # Generate frontmatter, i.e., tabletext, and the maintext (from paragraphs)
            tabletext = ""
            if toptable: tabletext = toptable.text
            date = getDate(tabletext)
            maintext = genMainText_unconsolidated(paragraphs)

            # Save all data for act to a dictionary
            data = {'title':title, 'year':year, 'act':act, 'PL':PL, 
                    'date':date, 'titlenum':titlenum, 'tabletext':tabletext, 
                    'maintext':maintext}

            # Save data to the PAstat database
            savePAunconsolidated(data)

    browser.quit()
    return True
    




def genMainText_unconsolidated(plist):
    maintext = ""
    for p in plist:
        # "Translates" the Legis formatting into something better (mine)
        marginleft = 0
        indent = 0
        if re.search(r"margin\-left\:(\-?\d\.\d{1,5})in", str(p)): 
            marginleft = float(re.search(r"margin\-left\:(\-?\d\.\d{1,5})in", str(p))[1])
        if re.search(r"text-indent:(\-?\d\.\d{1,5})in", str(p)): 
            indent = float(re.search(r"text-indent:(\-?\d\.\d{1,5})in", str(p))[1])
        margin = str((marginleft + indent) * 100) + "px"
        part1 = "<p style='margin-left:" + margin + "'>"
        part2 = p.text
        part3 = "</p>"
        maintext = maintext + part1 + part2 + part3
    return maintext





def getTableData(table):
    head = table.find_element_by_tag_name('thead')
    head_line = head.find_element_by_tag_name('tr')
    headers = [header.text for header in head_line.find_elements_by_tag_name('th')]
    
    body = table.find_element_by_tag_name('tbody')
    bodyrows = body.find_elements_by_tag_name('tr')
    rows = []
    for bodyrow in bodyrows:
        newrow = [el.text for el in bodyrow.find_elements_by_tag_name('td')]
        lastel = bodyrow.find_elements_by_tag_name('td')[-1]
        linkToAct = lastel.find_element_by_tag_name('a')
        newrow.append(linkToAct)
        rows.append(newrow)

    return headers, rows
    




def downloadRawData_DErules():
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_DErules)

    rules = {}
    rules['supremeRules'] = browser.find_element_by_partial_link_text("Supreme Court Rules").get_attribute('href')
    rules['chanceryRules'] = browser.find_element_by_partial_link_text("Court of Chancery Rules").get_attribute('href')
    rules['superiorCivilRules'] = browser.find_element_by_partial_link_text("Rules of Civil Procedure, Superior Court").get_attribute('href')
    rules['superiorCrimRules'] = browser.find_element_by_partial_link_text("Rules of Criminal Procedure, Superior Court").get_attribute('href')
    rules['superiorSpecialRules'] = browser.find_element_by_partial_link_text("Rules of Special Procedure, Superior Court").get_attribute('href')
    rules['superiorPTR'] = browser.find_element_by_partial_link_text("Interim Special Rule of Criminal Procedure for Pretrial Release").get_attribute('href')
    rules['familyCivilRules'] = browser.find_element_by_partial_link_text("Family Court Civil Rules").get_attribute('href')
    rules['familyCrimRules'] = browser.find_element_by_partial_link_text("Family Court Criminal Rules").get_attribute('href')
    rules['commonCivil'] = browser.find_element_by_partial_link_text("Court of Common Pleas Civil Rules").get_attribute('href')
    rules['commonCrim'] = browser.find_element_by_partial_link_text("Court of Common Pleas Criminal Rules").get_attribute('href')
    rules['commonBail'] = browser.find_element_by_partial_link_text("Court of Common Pleas Bail Rules of Conduct").get_attribute('href')
    rules['JPcivil'] = browser.find_element_by_partial_link_text("Justice of the Peace Court Civil Rules").get_attribute('href')
    rules['JPcivilViolations'] = browser.find_element_by_partial_link_text("Justice of the Peace Court Civil Violations Rules").get_attribute('href')
    rules['JPcrim'] = browser.find_element_by_partial_link_text("Justice of the Peace Court Criminal Rules").get_attribute('href')
    rules['DRE'] = browser.find_element_by_partial_link_text("Delaware Uniform Rules of Evidence").get_attribute('href')

    for key in rules.keys():
        filename = key + ".pdf"                
        filepath = rawDataDir_DERULES + filename
        resp = requests.get(rules[key])
        with open(filepath, 'wb') as file: #Need to open as binary file
            file.write(resp.content)

    browser.quit()

    return True





def processRawData_DErules():
    flist = getFileList(rawDataDir_DERULES)
    for f in flist:
        savePDFtext_DErules(f)
    return True




def processRawData_PArules():
    flist = getFileList(rawDataDir_PARULES, ext='.pdf', recursive=True)
    for f in flist:
        savePDFtext_PArules(f)
    return True



#------------------------------------------------------------------------------------#
# seeds: seed_PArules_RCPgeneral, seed_PArules_RCrimGeneral, seed_PArules_PARE,      #
#        seed_PArules_appellate1, seed_PArules_appellate2, seed_PArules_appellate3,  #
#        seed_PArules_JUVR1, seed_PArules_JUVR2, seed_PArules_MCCR,                  #
#        seed_PArules_RPROF, seed_PArules_RADM, seed_PArules_SENTG                   #
#                                                                                    #
# savedirs: rawDataDir_PARULES + "RCIVP/", rawDataDir_PARULES + 'RCRIMP/',           #
#           rawDataDir_PARULES + 'PARE/', rawDataDir_PARULES + 'RAP/',               #
#           rawDataDir_PARULES + 'JUVR/', rawDataDir_PARULES + 'MCCR/',              #
#           rawDataDir_PARULES + 'RPROF/', rawDataDir_PARULES + 'RADM/',             #
#           rawDataDir_PARULES + 'SENTG/'
#------------------------------------------------------------------------------------#


def downloadRawData_PArules(seed, savedir):
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed)
        
    allLinks = browser.find_elements_by_tag_name('a')
    pdfLinks = []
    for link in allLinks:
        if link.get_attribute('href'):
            if link.get_attribute('href').endswith(".pdf"): 
                pdfLinks.append(link.get_attribute('href'))
    
    pdfLinks = [l for l in pdfLinks if 'data' in l] # restricts to URLs in the data section; excludes style manual, code schedule, and code bulletin
    
    browser.quit()

    if not os.path.exists(savedir): os.makedirs(savedir)

    for link in pdfLinks:
        savepath = savedir + link.split('/')[-1]
        resp = requests.get(link)
        with open(savepath, 'wb') as file: #Need to open as binary file
            file.write(resp.content)

    return True




def nap(base, scaler=0):
    time.sleep(base + (scaler * random.random()))
