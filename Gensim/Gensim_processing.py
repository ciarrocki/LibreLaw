#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 09:48:07 2020

@author: dan
"""



import re
import psycopg2
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup






def save_text_as_paragraphs(jurisdiction_list, savepath):
    """ MAINTEXT ONLY - Does not include footnotes!"""

    with open(savepath, "w") as save_file:
        
        for jurisdiction in jurisdiction_list:
            
            if (jurisdiction == "Federal") or (jurisdiction == "US"): jxstr = "Federal_uscourtdoc"
            elif (jurisdiction == "Delaware") or (jurisdiction == "DE"): jxstr = "Delaware_decourtdoc"
            elif (jurisdiction == "Pennsylvania") or (jurisdiction == "PA"): jxstr = "Pennsylvania_pacourtdoc"
            else:
                print("Invalid Jurisdiction.")
                return False

            conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
            cur = conn.cursor()

            sql = "SELECT COUNT(*) FROM \"" + jxstr + "\";"
            cur.execute(sql)
            num_records = cur.fetchone()[0]

            sql = "SELECT * FROM \"" + jxstr + "\";"
            cur.execute(sql)

            print("Starting Jurisdiction:", jurisdiction, "(" + str(num_records) + " records)")
            print("Progress: ", end='')

            i = 0   # Do not want to call enumerate on the results
            for result in cur:
                i += 1
                if i % 1000 == 0: print("*", end='')
                maintext = result[12]
                plist = maintext.split("<p id='p")
                newplist = [re.sub(r"\<.*?\>", "", p) for p in plist]                
                for j, para in enumerate(newplist):
                    # Make sure para is well formed with an ID field
                    paraNumMatch = re.search(r"^(\d+)\'\>", para)
                    if not paraNumMatch: continue
                    # Extract para num
                    paraNum = int(paraNumMatch[1])
                    # Final processing
                    pro_para = re.sub(r"^\d+\'\>", "", para)
                    pro_para = pro_para.strip().replace('\n', ' ')
                    # Check the final string: if it looks like garbage, kick it out
                    if numnums_para(pro_para): continue
                    # Check using the same one we use for sentences too!        
                    if numnums(pro_para): continue
                    # Add database, docID, and paraID to the string
                    docID = str(result[0])
                    pro_para = docID + " " + jxstr + " " + str(paraNum) + " " +  pro_para
                    save_file.write(pro_para)
                    save_file.write('\n')
            print()

            conn.close()
    return True







def save_text_as_sentences(jurisdiction_list, savepath):

    with open(savepath, "w") as save_file:

        for jurisdiction in jurisdiction_list:

            if (jurisdiction == "Delaware") or (jurisdiction == "DE"): jxstr = "Delaware_decourtdoc"
            elif (jurisdiction == "Pennsylvania") or (jurisdiction == "PA"): jxstr = "Pennsylvania_pacourtdoc"
            elif (jurisdiction == "Federal") or (jurisdiction == "US"): jxstr = "Federal_uscourtdoc"
            else:
                print("Invalid Jurisdiction.")
                return False

            conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
            cur = conn.cursor()

            sql = "SELECT COUNT(*) FROM \"" + jxstr + "\";"
            cur.execute(sql)
            num_records = cur.fetchone()[0]

            sql = "SELECT * FROM \"" + jxstr + "\";"
            cur.execute(sql)

            print("Starting Jurisdiction:", jurisdiction, "(" + str(num_records) + " records)")
            print("Progress: ", end='')

            i = 0   # Do not want to call enumerate on the results
            for result in cur:
                i += 1
                if i % 1000 == 0: print("*", end='')
                maintext = result[12]
                footnotes = result[13]
                maintext = re.sub("\<a\shref\=\'\#.*?\/a\>", "", maintext)
                footnotes = re.sub("\<a\shref\=\'\#.*?\/a\>", "", footnotes)
                soup1 = BeautifulSoup(maintext)
                soup2 = BeautifulSoup(footnotes)
                maintext = soup1.get_text()
                footnotes = soup2.get_text()
                final_string = maintext + footnotes
                sentences = sent_tokenize(final_string)

                for sent in sentences:
                    # Numnums is the sentence-eater: if the sentence is 
                    # mostly numbers/spaces, or otherwise looks like garbage
                    # (re semantics) then we skip the line.
                    pro_sent = ' '.join(sent.split())
                    if numnums(pro_sent): continue
                    save_file.write(pro_sent)
                    save_file.write('\n')
            print()

            conn.close()        
    return True






def numnums_para(string):
    
    if len(string) < 30: return True
    if string.strip() == "": return True
    
    return False






def numnums(sent):

    numbers = sum(c.isdigit() for c in sent)
    letters = sum(c.isalpha() for c in sent)
    spaces = sum(c.isspace() for c in sent)
    
    if (numbers + spaces > letters) and (numbers > 2): return True
    if (numbers > letters): return True

    if letters < 15: return True

    return False