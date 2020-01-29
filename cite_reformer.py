#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 13:03:12 2020

@author: dan
"""

import re



def reform_de_cite(text):
    
    newtext = ""
    
    for i, c in enumerate(text):
        
        if c.isnumeric():
            if len(text) > i + 1:
                if not text[i + 1].isnumeric(): newtext = newtext + c + " "
                else: newtext = newtext + c
            else: newtext = newtext + c
    
        elif c.isalpha():
            if len(text) > i + 1:
                if not text[i + 1].isalpha(): newtext = newtext + c + " "
                else: newtext = newtext + c
            else: newtext = newtext + c
        
        else: newtext = newtext + c
    

    newtext = newtext.lower()
    
    # Atlantic Reporter
    newtext = re.sub(r"a\s{0,2}\.?\s{0,2}2\s{0,2}d", "a.2d", newtext)
    newtext = re.sub(r"a\s{0,2}\.?\s{0,2}3\s{0,2}d", "a.3d", newtext)
    newtext = re.sub(r"a\s{0,2}\.?\s{0,2}4\s{0,2}d", "a.4d", newtext)
    
    # North Eastern Reporter
    newtext = re.sub(r"n.*\..*e.*\..*2.*d", "n.e. 2d", newtext)
    newtext = re.sub(r"n.*\..*e.*\..*2.*d", "n.e. 2d", newtext)
    newtext = re.sub(r"n.*\..*e.*\..*2.*d", "n.e. 4d", newtext)

    # Federal Reporter
    newtext = re.sub(r"f\s{0,2}\.?\s{0,2}2\s{0,2}d", "f.2d", newtext)
    newtext = re.sub(r"f\s{0,2}\.?\s{0,2}3\s{0,2}d", "f.3d", newtext)
    newtext = re.sub(r"f\s{0,2}\.?\s{0,2}4\s{0,2}d", "f.4d", newtext)

    # Supreme Court
    newtext = re.sub(r"u.*\..*s.*\.", "u.s.", newtext)


    # FINAL FORMATTING
    newtext = newtext.replace("  ", " ")
    newtext = newtext.replace("  ", " ")

    return newtext




