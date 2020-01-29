#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 09:32:17 2019

@author: dan
"""




### Imports

import json
import os
import subprocess
import time
import random
import requests
import tarfile
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from OPparser_utils import getFileList, getCtDirFromCLlink
from OPparser_utils import rawDataDir_DEGOV, proDataDir_DEGOV, rawDataDir_CL, proDataDir_CL, compressedDataDir_CL
from OPparser_utils import chromeDriver, seed_DEGOV, seed_DECL, seed_PACL, seed_USCL
from OPparser_lists import prohibitedList_DEGOV




### Main Functions


def getData_CL(jurisdiction):

    """
    print("Downloading data  . . . . .")
    downloadData_CL(jurisdiction)
    """

    print("Extracting data . . . . .")
    extractData_CL(jurisdiction)

    print("Processing data . . . . .")
    if jurisdiction == "Delaware": sourcepath = rawDataDir_CL + "Delaware/"
    elif jurisdiction == "Pennsylvania": sourcepath = rawDataDir_CL + "Pennsylvania/"
    elif jurisdiction == "Federal": sourcepath = rawDataDir_CL + "Federal/"
    else:
        print("Invalid jurisdiction.  (getData_CL())")
        return False
    
    flist = getFileList(sourcepath, ext="", recursive=True)
    for f in flist:
        courtFolder = f.split('/')[-3] + "/" + f.split('/')[-2] + "/"
        savepath = proDataDir_CL + courtFolder
        processJSON_CL(f, savepath, recursive=False)

    print("Done.")
    return True





def updateRawData_DEGOV(year):

    finalDirectory = rawDataDir_DEGOV + str(year) + "/"
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_DEGOV)
    selectYear(browser, year)

    print("**Delaware Opinions/Orders Update Tool**")
    print("Checking year:", year)
    print("Checking directory:", finalDirectory)

    print("Getting links to opinions and orders . . .")
    allLinks = getOpinionLinks(browser)

    print("Comparing available files to downloaded files . . .")
    newLinks = []

    for link in allLinks:
        fileName = finalDirectory + link.partition("=")[2] + ".pdf"
        if os.path.isfile(fileName): continue
        else: newLinks.append(link)
        
    print("There are", len(newLinks), "new files to download.")

    if len(newLinks) > 0:
        print("Downloading new files . . .")
        downloadFiles(newLinks, finalDirectory)
    
    browser.quit()

    print("Done.")





def updateProData_DEGOV():

    pdfList = getFileList(rawDataDir_DEGOV, ext=".pdf", recursive=True)
    txtList = getFileList(proDataDir_DEGOV, ext=".detx", recursive=True)
    numList = [f.split('/')[-1][:-5] for f in txtList]

    newList = [f for f in pdfList if f.split('/')[-1][:-4] not in numList]
    print("Extracting text from", len(newList), "new PDFs.")

    for f in newList:
        savePDFtext_DEGOV(f)
    print("Done.")

    return True





def downloadData_DEGOV(year):

    finalDirectory = rawDataDir_DEGOV + str(year) + "/"    
    browser = webdriver.Chrome(executable_path = chromeDriver)
    browser.get(seed_DEGOV)
    selectYear(browser, year)
    
    print("Downloading year:", year)
    print("Saving files to:", finalDirectory)
    
    print("Getting links to opinions and orders . . .")
    links = getOpinionLinks(browser)

    print("Downloading opinions and orders . . .")
    downloadFiles(links, finalDirectory)

    browser.quit()

    print("Done.")





def downloadData_CL(jurisdiction):
    
    if jurisdiction == "Delaware": seed = seed_DECL
    elif jurisdiction == "Pennsylvania": seed = seed_PACL
    elif jurisdiction == "Federal": seed = seed_USCL
    else:
        print("Invalid jurisdiction.")
        return False

    saveDir = compressedDataDir_CL

    for i, item in enumerate(seed.items()):
        print("Downloading file " + str(i + 1) + " of " + str(len(seed)) + ": " + item[1] + " . . .  ", end='')
        resp = requests.get(item[1])
        savePath = saveDir + item[1].split('/')[-1]
        #print(savePath)
        with open(savePath, 'wb') as file: #Need to open as binary file
            file.write(resp.content)
        print("Done.")
    print("Download complete.")





def extractData_CL(jurisdiction):
    
    if jurisdiction == "Delaware": flist = [compressedDataDir_CL + key + ".tar.gz" for key in seed_DECL.keys()]
    elif jurisdiction == "Pennsylvania": flist = [compressedDataDir_CL + key + ".tar.gz" for key in seed_PACL.keys()]
    elif jurisdiction == "Federal": flist = [compressedDataDir_CL + key + ".tar.gz" for key in seed_USCL.keys()]
    else:
        print("Invalid jurisdiction.")
        return False

    for f in flist:
        savepath = rawDataDir_CL + getCtDirFromCLlink(f)
        with tarfile.open(f, "r:gz") as tar_ref:
            tar_ref.extractall(savepath)






def analyzeJSON_CL(path, recursive=False):

    fileList = getFileList(path, ext='.json', recursive=recursive)
    
    OCRcounter = 0
    lawboxCounter = 0
    notLawboxCounter = 0
    withCitesCounter = 0
    htmlCounter = 0
    plainTextCounter = 0
    for file in fileList:    
        data = loadData(file)
        if data['extracted_by_ocr'] != None:
            if data['extracted_by_ocr'] == 'true': OCRcounter += 1
        if data['html_lawbox'] != None:
            if len(data['html_lawbox']) > 10: lawboxCounter += 1
        if data['html_lawbox'] != None:
            if len(data['html_lawbox']) <= 10: notLawboxCounter += 1
        if data['html_lawbox'] == None:
            notLawboxCounter += 1
        if data['html_with_citations'] != None:
            if len(data['html_with_citations']) > 10: withCitesCounter += 1
        if data['html'] != None:
            if len(data['html']) > 10: htmlCounter += 1
        if data['plain_text'] != None:
            if len(data['plain_text']) > 10: plainTextCounter += 1

    #Testing
    fileCounter = len(fileList)
    print('\n', "Total Number of JSON Files:", fileCounter)
    print("Number OCR Used:", OCRcounter, "({0:.2f}%)".format(OCRcounter / fileCounter * 100))
    print("lawbox:", lawboxCounter, "({0:.2f}%)".format(lawboxCounter / fileCounter * 100))
    print("notLawbox:", notLawboxCounter, "({0:.2f}%)".format(notLawboxCounter / fileCounter * 100))
    print("html_with_cites:", withCitesCounter, "({0:.2f}%)".format(withCitesCounter / fileCounter * 100))
    print("html:", htmlCounter, "({0:.2f}%)".format(htmlCounter / fileCounter * 100))
    print("plain_text:", plainTextCounter, "({0:.2f}%)".format(plainTextCounter / fileCounter * 100))
    print('\n', data.keys(), '\n')

    return fileCounter, OCRcounter, lawboxCounter, withCitesCounter



### Sub Functions

def loadData(path):
    data = 0
    with open(path) as dataFile:
        data = json.load(dataFile)
    return data




def selectYear(browser, year):
    
    customYearOption = browser.find_element_by_css_selector("option[value='year']")
    customYearOption.click()

    yearOptionText = r"option[value='" + str(year) + r"']"
    yearOption = browser.find_element_by_css_selector(yearOptionText)
    yearOption.click()



def getOpinionLinks(browser):

    opLinks = []

    try:
        while True:
            newRows = browser.find_elements_by_css_selector(".table-responsive")[0].find_elements_by_tag_name('tr')            
            for row in newRows:
                newLink = row.find_element_by_tag_name('a').get_attribute('href')
                if newLink != None: opLinks.append(newLink)            
            nextButton = browser.find_element_by_css_selector("a[aria-label='Next']")
            nextButton.click()
    
    except NoSuchElementException:
        pass
    
    return opLinks



def downloadFiles(links, folder):

    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for link in links:

        fileID = link.partition("=")[2]
        if isProhibited(fileID): continue
        fileName = folder + fileID + ".pdf"
        
        resp = requests.get(link)
        
        with open(fileName, 'wb') as file: #Need to open as binary file
            file.write(resp.content)




def saveAllPDFtext_DEGOV(path=rawDataDir_DEGOV):
    flist = getFileList(path, ext=".pdf", recursive=True)
    for f in flist:
        savePDFtext_DEGOV(f)
    return True





def savePDFtext_DEGOV(filePath):
    """
    Uses the PDFminer pdf2txt.py command-line utility to save the text of
    DelawareGov PDFs to text files.

    Example command that is executed:
        pdf2txt.py -t text -o "/home/dan/Data/DelawareGov/Processed/2019/273500.txt" "/home/dan/Data/DelawareGov/Raw/2019/273500.pdf"    
    """
    year = filePath.split('/')[-2]
    fileName = filePath.split('/')[-1]
    if fileName.endswith(".pdf"): fileName = fileName[:-4]
    savePath = proDataDir_DEGOV + year + '/' + fileName + ".detx"
    command = "pdf2txt.py -t text -o " + savePath + " " + filePath
    #print("\n***COMMAND:", command)
    subprocess.call(command, shell=True) # shell=True is necessary for command as single-string with arguments; might be a better way to do this???

    return True





def processJSON_CL(sourcePath, outputPath, recursive=False):

    data = loadData(sourcePath)
    fileName = sourcePath.split('/')[-1]

    if data['html_lawbox']:
        if len(data['html_lawbox']) > 10: 
            outDir = outputPath + "/lawbox/"
            newFilePath = outDir + fileName[:-4] + "cllb"
            if not os.path.exists(outDir): os.makedirs(outDir)
            with open(newFilePath, 'wb') as file: #Need to open as binary file
                file.write(data['html_lawbox'].encode('utf8'))

    elif data['html_with_citations']:
        if len(data['html_with_citations']) > 10: 
            outDir = outputPath + "/withCitations/"
            newFilePath = outDir + fileName[:-4] + "clwc"
            if not os.path.exists(outDir): os.makedirs(outDir)
            with open(newFilePath, 'wb') as file: #Need to open as binary file
                file.write(data['html_with_citations'].encode('utf8'))

    elif data['plain_text']:
        if len(data['plain_text']) > 10: 
            outDir = outputPath + "/plainText/"
            newFilePath = outDir + fileName[:-4] + 'cltx'
            if not os.path.exists(outDir): os.makedirs(outDir)
            with open(newFilePath, 'wb') as file: #Need to open as binary file
                file.write(data['plain_text'].encode('utf8'))

    else:
        print("Failed to load file: ", sourcePath)






def processJSONfolder_CL(sourcePath, outputPath, recursive=False):

    fileList = getFileList(sourcePath, ext='.json', recursive=recursive)
    failCounter = 0
    lawboxCounter = 0
    htmlWCcounter = 0
    plainTextCounter = 0

    for file in fileList:
        
        data = loadData(file)
        fileName = file.split('/')[-1]

        if data['html_lawbox']:
            if len(data['html_lawbox']) > 10: 
                outDir = outputPath + '/' + file.split('/')[-3] + '/' + file.split('/')[-2] + "/lawbox/"
                newFilePath = outDir + fileName[:-4] + "cllb"
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(newFilePath, 'wb') as file: #Need to open as binary file
                    file.write(data['html_lawbox'].encode('utf8'))
                lawboxCounter += 1
                continue

        elif data['html_with_citations']:
            if len(data['html_with_citations']) > 10: 
                outDir = outputPath + '/' + file.split('/')[-3] + '/' + file.split('/')[-2] + "/withCitations/"
                newFilePath = outDir + fileName[:-4] + "clwc"
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(newFilePath, 'wb') as file: #Need to open as binary file
                    file.write(data['html_with_citations'].encode('utf8'))
                htmlWCcounter += 1
                continue

        elif data['plain_text']:
            if len(data['plain_text']) > 10: 
                outDir = outputPath + '/' + file.split('/')[-3] + '/' + file.split('/')[-2] + "/plainText/"
                newFilePath = outDir + fileName[:-4] + 'cltx'
                if not os.path.exists(outDir):
                    os.makedirs(outDir)
                with open(newFilePath, 'wb') as file: #Need to open as binary file
                    file.write(data['plain_text'].encode('utf8'))
                plainTextCounter += 1
                continue

        else:
            print("Failed to load file: ", sourcePath + file)
            failCounter += 1

    print("\nTotal lawbox:", lawboxCounter)
    print("Total HTMLwithCitations:", htmlWCcounter)
    print("Total plainText:", plainTextCounter)
    print("failed to load:", failCounter)





def isProhibited(fileID):
    
    if fileID in prohibitedList_DEGOV:
        print("PROHIBITED ITEM!")
        return True
        
    return False



def nap(base, scaler=0):
    time.sleep(base + (scaler * random.random()))







"""
def getText_pypdf(filePath):

    fullText = ""
    with open(filePath, "rb") as fileObj:
        pdfReader = PyPDF2.PdfFileReader(fileObj)
        numPages = pdfReader.numPages
        for pageNum in range(0, numPages):
            pageObj = pdfReader.getPage(pageNum)
            pageText = pageObj.extractText()
            fullText = fullText + pageText + '\x0c\n'

    return fullText
"""

