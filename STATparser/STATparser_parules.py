#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 16:06:03 2019

@author: dan
"""



import re



from STATparser_utils import loadLines_text_rules, getFileList
from STATparser_format import formatSecText
from STATparser_toDjango import savePAruleTree, savePArule



PARULES = {"PARE": (1000, '/home/dan/Data/PACodeBulletin/Processed/PARE/', 'Pennsylvania Rules of Evidence', 'Pa. R. Evid.'), 
           "RCIVP": (2000, '/home/dan/Data/PACodeBulletin/Processed/RCIVP/', 'Pennsylvania Rules of Civil Procedure', 'Pa. R. Civ. P.'),
           "RCRIMP": (3000, '/home/dan/Data/PACodeBulletin/Processed/RCRIMP/', 'Pennsylvania Rules of Criminal Procedure', 'Pa. R. Crim. P.'),
           "RAP": (4000, '/home/dan/Data/PACodeBulletin/Processed/RAP/', 'Pennsylvania Rules of Appellate Procedure', 'Pa. R. App. P.'),
           "MCCR": (5000, '/home/dan/Data/PACodeBulletin/Processed/MCCR/', 'Pennsylvania Minor Court Civil Rules', 'Pa. Minor Ct. Civ. R.'),
           "JUVR": (6000, '/home/dan/Data/PACodeBulletin/Processed/JUVR/', 'Pennsylvania Juvenile Rules', 'Pa. Juv. R.')}
#           "RPROF": (7000, '/home/dan/Data/PACodeBulletin/Processed/RPROF/', 'Rules of Professional Conduct', 'Pa. R. Prof. Cond.'),
#           "RADM": (8000, '/home/dan/Data/PACodeBulletin/Processed/RADM/', 'Bar Admissions Rules', 'Pa. Bar Adm. R.'),
#           "SENTG": (9000, '/home/dan/Data/PACodeBulletin/Processed/SENTG/', 'Sentencing Guidelines', 'Pa. Sent. Guideline R.')}







def parseAndSave_parules_all():
    
    for k in PARULES.keys():
    
        treeHTML, rules = parse_ruleset_parules(ruleset=k)
        
        savePAruleTree(fullName=PARULES[k][2], treeType="Rules", number=PARULES[k][0], 
                       nameText=PARULES[k][2], description=PARULES[k][2], 
                       bigHTML=treeHTML, smallHTML="", source="PA Code & Bulletin (pacodeandbulletin.gov)", 
                       filepath=PARULES[k][1])
        
        for r in rules:
            savePArule(title=rules[r]['title'], number=rules[r]['number'], 
                       text=rules[r]['text'], treeNumber=PARULES[k][0], 
                       filepath=PARULES[k][1], citation0=rules[r]['citation0'], 
                       previous=rules[r]['previous'], next0=rules[r]['next'], 
                       rulesname=PARULES[k][2])
    
    return True





def parse_ruleset_parules(ruleset='RCIVP'):

    treeHTML = ""
    rules = {}

    flist = sorted(getFileList(PARULES[ruleset][1], recursive=False))

    for f in flist:
        smallTree, smallRules = parse_chapter_parules(f, PARULES[ruleset][3], PARULES[ruleset][0])
        treeHTML = treeHTML + smallTree
        rules.update(smallRules)

    rules = format_rules_parules(rules)
    rules = add_prev_next_parules(rules, PARULES[ruleset][0])

    return treeHTML, rules





def parse_chapter_parules(filepath, ruleform, rulebase):

    linelist = loadLines_text_rules(filepath)
    frontmatter, maintext = cleanRules_parules(linelist)

    rules = splitRules_parules(maintext)
    rules = splitTitleText_parules(rules)
    rules = getNumberCite_parules(rules, ruleform)

    chap_name = get_chap_name(frontmatter)

    treeHTML = "<details><summary>" + chap_name + "</summary>"
    for k in rules.keys():
        treeHTML = treeHTML + "<a href='/Pennsylvania/statutes/" + str(rulebase) + "/" + rules[k]['number'] + "'>" + rules[k]['title'] + "</a>"
    treeHTML = treeHTML + "</details>"

    return treeHTML, rules





def format_rules_parules(rules):

    newrules = {}    
    for k in rules.keys():
        tempR = rules[k]
        linelist = tempR['text']
        newtext = formatSecText(linelist)
        tempR['text'] = newtext
        newrules[k] = tempR

    return newrules





def add_prev_next_parules(rules, rulebase):

    newrules = {}
    keys = list(rules.keys())

    for i, k in enumerate(keys):
        newrule = rules[k]
        if i == 0: prev = ""
        else: prev = "<a href='/Pennsylvania/statutes/" + str(rulebase) + "/" + rules[keys[i-1]]['number'] + "'>" + rules[keys[i-1]]['title'] + "</a>"
        if i >= len(keys) - 1: next0 = ""
        else: next0 = "<a href='/Pennsylvania/statutes/" + str(rulebase) + "/" + rules[keys[i+1]]['number'] + "'>" + rules[keys[i+1]]['title'] + "</a>"
        newrule['previous'] = prev
        newrule['next'] = next0
        newrules[k] = newrule

    return newrules





def getNumberCite_parules(rules, ruleform):
    
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





def get_chap_name(text):

    # Check all lines for text like: 'CHAPTER 200. BUSINESS OF COURTS\n'
    # Works for most PA rules
    for i, line in enumerate(text):
        if re.search(r"^CHAPTER\s\d{1,5}\.", line):
            newtext = getChapterNameText(text, i)
            return newtext.replace('\n', '')

    # Check all lines for text like: 'ARTICLE III. PRESUMPTIONS\n'
    # Works for PA rules of evidence
    for i, line in enumerate(text):
        if re.search(r"^ARTICLE\s[IVXLC]{1,5}\.\s[A-Z]", line):
            newtext = getChapterNameText(text, i)
            return newtext.replace('\n', '')

    return ""



def getChapterNameText(text, i):
    newtext = text[i]
    j = i
    while True:
        if len(text) > j + 1:
            if text[j + 1].isupper(): 
                newtext = newtext + " " + text[j + 1]
                j = j + 1
            else: break
        else: break
    return newtext




def splitRules_parules(linelist):

    rules = {}
    newrule = []        
    ruleNum = 0
    ruleNumText = ""

    for i, line in enumerate(linelist):        
        
        if isNewRule_parules(line):
            newRuleNum, newRuleNumText = getRuleNumText_parules(line)
            if newRuleNum >= ruleNum:
                rules[ruleNumText] = newrule
                newrule = []
                ruleNum = newRuleNum
                ruleNumText = newRuleNumText

        processed_line = line.replace('\n', '')
        newrule.append(processed_line)

    rules[ruleNumText] = newrule # Add final rule upon exit from loop

    if "" in rules.keys(): del rules[""]

    return rules





def isNewRule_parules(line):
    
    if newRuleDQ(line): return False
    if newRuleAuto(line): return True
    
    proLine = line.lower().replace("\x0c", "")
    
    # STANDARD #1: DE Chancery, DRE, PA Rules normal, 
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.?\s+", proLine): return True

    # STANDARD #2: PA Rules: Rule 204.1
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\.\d{1,3}\.", proLine): return True

    # Superior Crim Rules
    if re.search(r"^\s\s\srule\s*(\d{1,5})[a-z]?\.?\s+", proLine): return True

    return False



def newRuleDQ(line):

    # PA criminal rules, chapter 1: A line starts with "Rule 547. With regard"
    if line.startswith("Rule 547. With regard to other information"): return True
    # PA criminal rules, chapter 7: A line (not a new rule) starts with this text
    if line.startswith("Rule 1410. Present Rule"): return True

    return False


def newRuleAuto(line):

    # PA criminal rules; anomaly with Rule 536
    if line.startswith("Rule 536 . Procedures"): return True
    
    return False
    



def getRuleNumText_parules(line):
    proLine = line.lower().replace("\x0c", "")
    
    # Standard #1: Chancery, DRE, PA Rules normal, 
    if re.search(r"^rule\s*(\d{1,5})[a-z]?\s?\.\s+([a-z]|\[|\()", proLine):
        newRuleNum = int(re.search(r"^rule\s*(\d{1,5})[a-z]?\s?\.\s+([a-z]|\[|\()", proLine)[1])
        newRuleNumText = re.search(r"^rule\s*(\d{1,5}[a-z]?)\s?\.\s+([a-z]|\[|\()", proLine)[1]
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





def splitTitleText_parules(rules):
    
    newrules = {}
    for rule in rules:
        #if len(rules[rule]) < 2: print(rules[rule])
        newrule = {"title":rules[rule][0], "text":rules[rule][1:]}
        newrules[rule] = newrule

    return newrules

    



def cleanRules_parules(linelist):
    """
    NEED TO COMMENT THIS UP!
    """

    frontmatter = []
    maintext = []
    i = 0
    startMain = False

    while i < len(linelist):
        
        # Start with SPECIAL CASE: flipped top SEE Rule 206 of PA RULES OF CIV P 
        if linelist[i].startswith('\x0c'):
            if len(linelist) >= i + 4:
                if linelist[i + 2].startswith("Rule"): 
                    i = i + 2
                    continue
        
        # Skip Condition #1: page feed character - skip first four lines of every page!
        if linelist[i].startswith('\x0c'): 
            
            i = i + 4
            continue

        # Skip Condition #2: text like: "(313121) No. 372 Nov. 05" starts a FOUR LINE SKIP at the bottom of each page
        if re.search("^\(\d{6}\)\sNo", linelist[i]):
            i = i + 4
            continue            

        # Skip Condition #3: page numbers in the form 100-42
        if re.search("^\d{3,5}\-\d{1,3}\n", linelist[i]):
            i = i + 1
            continue

        # If the startMain flag is not set, determine whether or not to set it
        if not startMain:
            # Special case for rules of criminal procedure, which include a bunch of stuff at the front we want to avoid
            if (linelist[0] == 'TITLE 234\n') and (linelist[2] == 'RULES OF CRIMINAL PROCEDURE\n'):
                if re.search("^Rule\s100\.", linelist[i]): startMain = True
            # Normal case: any "Rule" line will trigger it and start the maintext
            else:
                if re.search("^Rule\s\d{1,5}\.\s", linelist[i]): startMain = True
                if re.search("^Rule\s\d{1,5}\.\d{1,5}\s", linelist[i]): startMain = True

        # Write the line either to maintext or frontmatter, depending on
        # whether the startMain flag has been set        
        if startMain:
            maintext.append(linelist[i])
        else:
            frontmatter.append(linelist[i])
        i = i + 1


    

    return frontmatter, maintext




