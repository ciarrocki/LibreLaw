#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 07:39:49 2019

@author: dan
"""


### Imports

import re





### Main Functions

def formatFootnotes_text(footnotes):

    finalFNs = ""

    for fnNum, fn in enumerate(footnotes):
        if fnNum == 0: continue
        newFN = r"<div class='fn'><a href='#FNanchor" + str(fnNum) + "' class='FNnumber' name='FNnumber" + str(fnNum) + "'>" + str(fnNum) + "</a> "
        flatText = flattenFN(fn[0])
        flatText = removeFNnum(flatText, fnNum)
        flatText = flatText.replace('\n', '')
        newFN = newFN + flatText + "</div>"
        finalFNs = finalFNs + newFN

    return finalFNs





### Sub Functions

def flattenFN(textList):
    flatText = ""
    for line in textList:
        flatText += line
    return flatText





def removeFNnum(text, fnNum):
    newtext = re.sub(r'^' + str(fnNum), '', text.strip()) 
    return newtext


