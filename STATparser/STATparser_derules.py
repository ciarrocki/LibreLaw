#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:06:48 2019

@author: dan
"""



r1 = (1000, '/home/dan/Data/DelawareGov/Rules/Processed/DRE.txt', "Delaware Rules of Evidence", "DRE")
r2 = (2000, '/home/dan/Data/DelawareGov/Rules/Processed/supremeRules.txt', "Supreme Court Rules", "Sup. Ct. R.")
r3 = (3000, '/home/dan/Data/DelawareGov/Rules/Processed/chanceryRules.txt', "Court of Chancery Rules", "Ct. Ch. R.")
r4 = (4000, '/home/dan/Data/DelawareGov/Rules/Processed/superiorCivilRules.txt', "Superior Court Civil Rules", "Sup. Ct. Civ. R.")
r5 = (5000, '/home/dan/Data/DelawareGov/Rules/Processed/superiorCrimRules.txt', "Superior Court Criminal Rules", "Sup. Ct. Crim. R.")
r6 = (6000, '/home/dan/Data/DelawareGov/Rules/Processed/familyCivilRules.txt', "Family Court Civil Rules", "Fam. Ct. Civ. R.")
r7 = (7000, '/home/dan/Data/DelawareGov/Rules/Processed/familyCrimRules.txt', "Family Court Criminal Rules", "Fam. Ct. Crim. R.")
r8 = (8000, '/home/dan/Data/DelawareGov/Rules/Processed/commonCivil.txt', "Court of Common Pleas Civil Rules", "Ct. Comm. Pl. Civ. R.")
r9 = (9000, '/home/dan/Data/DelawareGov/Rules/Processed/commonCrim.txt', "Court of Common Pleas Criminal Rules", "Ct. Comm. Pl. Crim. R.")
r10 = (10000, '/home/dan/Data/DelawareGov/Rules/Processed/JPcivil.txt', "Justice of the Peace Court Civil Rules", "J.P. Ct. Civ. R.")
r11 = (11000, '/home/dan/Data/DelawareGov/Rules/Processed/JPcrim.txt', "Justice of the Peace Court Criminal Rules", "J.P. Ct. Crim. R.")
allRules = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11]
testRules = [r1, r2, r3, r4, r5]


### Imports
import re

from STATparser_toDjango import saveDEruleTree, saveDErule
from STATparser_utils import loadLines_text_rules
from STATparser_format import formatSecText




def parseAndSave_DErules_all():

    for rule in allRules:
        ruleset, ruletree = parseDErule(rule[1], rule[0], rule[3])

        saveDEruleTree(fullName=rule[2], treeType="Rules", number=rule[0],
                       nameText=rule[2], description=rule[2], bigHTML=ruletree, 
                       smallHTML="", source="DE Government Website", 
                       filepath=rule[1])

        for r in ruleset:
            saveDErule(title=ruleset[r]['title'], number=ruleset[r]['number'], 
                       text=ruleset[r]['text'], treeNumber=rule[0], 
                       filepath=rule[1], citation0=ruleset[r]['citation0'],
                       previous=ruleset[r]['previous'], next0=ruleset[r]['next'],
                       rulesname=rule[2])





def parseDErule(filepath, rulebase, ruleform):

    linelist = loadLines_text_rules(filepath)
    rules, treelist = splitRules_derules(linelist)
    rules = splitTitleText_derules(rules)
    rules = getNumberCite_derules(rules, ruleform)
    rules = format_rules_derules(rules)
    rules = add_prev_next_derules(rules, rulebase)
    treeHTML = get_tree_html(treelist, rulebase, rules)
    
    return rules, treeHTML





def add_prev_next_derules(rules, rulebase):

    newrules = {}
    keys = list(rules.keys())

    for i, k in enumerate(keys):
        newrule = rules[k]
        if i == 0: prev = ""
        else: prev = "<a href='/Delaware/statutes/" + str(rulebase) + "/" + rules[keys[i-1]]['number'] + "'>" + rules[keys[i-1]]['title'] + "</a>"
        if i >= len(keys) - 1: next0 = ""
        else: next0 = "<a href='/Delaware/statutes/" + str(rulebase) + "/" + rules[keys[i+1]]['number'] + "'>" + rules[keys[i+1]]['title'] + "</a>"
        newrule['previous'] = prev
        newrule['next'] = next0
        newrules[k] = newrule

    return newrules





def format_rules_derules(rules):
    
    newrules = {}
    for r in rules:
        linelist = rules[r]['text']
        newtext = formatSecText(linelist)
        newrule = {'title':rules[r]['title'], 'text':newtext,
                   'number':rules[r]['number'], 'citation0':rules[r]['citation0']}
        newrules[r] = newrule

    return newrules




def get_tree_html(treelist, rulebase, rules):

    html = ""
    detailsOn = False
    
    for line in treelist:
        if re.search(r"^((Article)|(ARTICLE))\s[A-X]{1,5}\.", line) or\
        re.search(r"^[A-X]{1,5}\.\s", line):
            detailsOn = True
            newtext = line.replace('\n', '').replace('\x0c', '')
            html = html + "</details><details><summary>" + newtext + "</summary>" 
        else:
            linktext = rules[line]['title'].replace('\n', '').replace('\x0c', '')
            html = html + "<a href='/Delaware/statutes/" + str(rulebase) + "/" + line + "'>" + linktext + "</a>"

    if detailsOn: html += "</details>"
    if html.startswith("</details>"): html = html[10:]

    return html






def getNumberCite_derules(rules, ruleform):
    
    newrules = {}
    for r in rules:
        ttext = rules[r]['title'].lower()

        # DE Chancery, DRE, <ADD MORE>
        if re.search(r"^rule\s*(\d{1,5}[a-z]?)\.?\s+", ttext): 
            num = re.search(r"^rule\s*(\d{1,5}[a-z]?)\.?\s+", ttext)[1]
        
        # Standard #2: DE Rules: Rule 5.1; PA Rules: Rule 204.1
        elif re.search(r"^rule\s*(\d{1,5})[a-z]?\.\d{1,3}\.\s+[a-z]", ttext):
            num = re.search(r"^rule\s*(\d{1,5}[a-z]?\.\d{1,3})\.\s+[a-z]", ttext)[1]

        # Superior Crim Rules
        elif re.search(r"^\s\s\srule\s*(\d{1,5}[a-z]?)\.?\s+", ttext):
            num = re.search(r"^\s\s\srule\s*(\d{1,5}[a-z]?)\.?\s+", ttext)[1]
        # Else/Default
        else:
            num = "-1"

        citation0 = ruleform.strip() + " " + num

        newrule = {'title':rules[r]['title'], 'text':rules[r]['text'], 
                   'number':num, 'citation0':citation0}
        
        newrules[r] = newrule

    return newrules





def splitTitleText_derules(rules):
    
    newrules = {}
    for rule in rules:
        newrule = {"title":rules[rule][0], "text":rules[rule][1:]}
        newrules[rule] = newrule

    return newrules





def splitRules_derules(linelist):
    rules = {}
    ruleNum = 0
    newrule = []
    ruleNumText = ""
    treelist = []
    prevHeaderFlag = False

    for i, line in enumerate(linelist):        

        if isNewRule(line):
            newRuleNum, newRuleNumText = getRuleNumText(line)
            if newRuleNum >= ruleNum:
                rules[ruleNumText] = newrule
                treelist.append(ruleNumText)
                newrule = []
                ruleNum = newRuleNum
                ruleNumText = newRuleNumText

        if isHeader(i, linelist):
            treelist.append(line)
            prevHeaderFlag = True            
            continue
        
        if prevHeaderFlag:
            if isHeader2(i, linelist):
                treelist[-1] = treelist[-1] + " " + line
                continue
            prevHeaderFlag = False


        newrule.append(line)
        if (i == len(line) - 1): 
            rules[ruleNumText] = newrule
            treelist.append(ruleNumText)


    treelist = [e for e in treelist if e] # Remove blank entries ('')

    return rules, treelist




def isNewRule(line):
    proLine = line.lower().replace("\x0c", "")
    
    # STANDARD #1: DE Chancery, DRE, PA Rules normal, 
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.?\s+", proLine): return True

    # STANDARD #2: PA Rules: Rule 204.1
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.\d{1,3}\.", proLine): return True

    # Superior Crim Rules
    if re.search(r"^\s\s\srule\s*(\d{1,5})[a-z]?\.?\s+", proLine): return True

    return False



def getRuleNumText(line):
    proLine = line.lower().replace("\x0c", "")
    
    # Standard #1: Chancery, DRE, PA Rules normal, 
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.?\s+([a-z]|\[)", proLine):
        newRuleNum = int(re.search(r"^rule\s*(\d{1,5})[a-z]?\.?\s+([a-z]|\[)", proLine)[1])
        newRuleNumText = re.search(r"^rule\s*(\d{1,5}[a-z]?)\.?\s+([a-z]|\[)", proLine)[1]
        return newRuleNum, newRuleNumText

    # Standard #2: DE Rules: Rule 5.1; PA Rules: Rule 204.1
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.\d{1,3}\.\s+[a-z]", proLine):
        newRuleNum = int(re.search(r"^rule\s*(\d{1,5})[a-z]?\.\d{1,3}\.\s+[a-z]", proLine)[1])
        newRuleNumText = re.search(r"^rule\s*(\d{1,5}[a-z]?\.\d{1,3})\.\s+[a-z]", proLine)[1]
        return newRuleNum, newRuleNumText

    # Superior Crim Rules
    if re.search(r"^\s\s\srule\s*(\d{1,5})[a-z]?\.?\s+", proLine): 
        newRuleNum = int(re.search(r"^\s\s\srule\s*(\d{1,5})[a-z]?\.?\s+", proLine)[1])
        newRuleNumText = re.search(r"^\s\s\srule\s*(\d{1,5}[a-z]?)\.?\s+", proLine)[1]
        return newRuleNum, newRuleNumText

    return 0, 0




def isHeader(i, linelist):
    line = linelist[i]
    if i > 0: prev1 = linelist[i-1]
    else: prev1 = "<START>"
    if i < len(linelist) - 1: next1 = linelist[i+1]
    else: next1 = "<END>"

    # Chancery Rules Format: ["\n", "II. COMMENCEMENT OF ACTION; SERVICE OF PROCESS, PLEADINGS,", "MOTIONS, AND ORDERS; DEPOSIT AND SECURITY FOR COSTS."]
    if (prev1.strip() == ""):
        if line.isupper():
            if re.search(r"^[A-X]{1,5}\.\s", line):
                return True

    # DRE Rules Format:
    if re.search(r"^((Article)|(ARTICLE))\s[A-X]{1,5}\.", line):
        return True

    return False


        
def isHeader2(i, linelist):
    line = linelist[i]
    if line.isupper(): return True
    return False

        

        