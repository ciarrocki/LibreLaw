#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:31:44 2019

@author: dan


        Cite Matrix - dictionary that stores citation relationships: 
        Keys: (int) documentID 
        Values: (dictionary) a dictionary with following values:

            "id": documentID (int)

            "next": a list of doc IDs (ints) of the documents that 
                    cite this one

            "previous": a list of tuples: first element is the citation (str),
                        second element is the document ID (int) if the document 
                        is in the cite dictionary; if not, the second element
                        is -1

        Cite Dictionary:
            Keys: int : docID
            Values: list of ints : All documents by docID this doc cites
    
"""


import psycopg2
import pickle

from CiteVista_utils import getDocCites
from CiteVista_utils import CiteMatrixDir





def load_cite_matrix(path=CiteMatrixDir+"matrix_de0.p"):
    return pickle.load(open(path, "rb"))





def gen_cite_matrix(jurisdictions=['DE'], save=True, 
                    savepath=CiteMatrixDir+"citeMatrix0.p"):
    """
    Creates a new cite matrix across entire court doc databases.
    The cite matrix is a dictionary.  Keys = doc ids of every court doc in
    the specified databases.  Each value in the cite matrix is itself a 
    dictionary, each of which has 2 key-values: the previous list and the
    next list.

    The Previous List: All opinions that the subject opinion cites.  Opinions
    on the previous list come before the subject opinion in time.

    The Next List: All opinions that cite the subject opinion.  Opinions in
    the next list come after the subject opinion in time.

    """

    print("Making cite dictionary.")
    cite_dict = gen_cite_dict(jurisdictions)
    print("Items in cite dictionary:", len(cite_dict))
    cite_matrix0 = {}
    prevCount = 0
    nextCount = 0

    # Make "previous" list:
    # Go through every document in each database and search it for citations
    # Add all of those citations to a dictionary with keys of doc id
    print("Making previous list . . . . .")
    for jx in jurisdictions:

        if (jx == "Delaware") or (jx == "DE"): jxstr = "Delaware_decourtdoc"
        elif (jx == "Pennsylvania") or (jx == "PA"): jxstr = "Pennsylvania_pacourtdoc"
        elif (jx == "Federal") or (jx == "US"): jxstr = "Federal_uscourtdoc"
        else:
            print("Invalid Jurisdiction:", jx)
            return False

        print("Starting jurisdiction:", jx)
        conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
        cur = conn.cursor()
        sql = "SELECT * FROM \"" + jxstr + "\";"
        cur.execute(sql)

        print("Making previous list. Completed: . . . ", end='')
        for c, result in enumerate(cur):
            if c % 1000 == 0: print(c, " . . . ", end='')
            citeList = getDocCites(result[12] + " " + result[13])
            if result[0] == 134422: print(citeList)
            newlist = list()
            for cite in citeList:
                if cite[0] in cite_dict.keys(): newlist.append((cite[0], cite_dict[cite[0]]))
                else: newlist.append((cite[0], -1))
                prevCount += 1
            #Dedupe previous list
            alreadycited = []
            finallist = []
            for item in newlist:
                if item[0] in alreadycited: continue
                alreadycited.append(item[0])
                finallist.append(item)
            cite_matrix0[int(result[0])] = finallist
        print("Done.")

    # Make "next" list: 
    # Go through every document again and look for that document in the lists
    # of doc ids - add all of those doc IDs to a list
    print("Making next list for", len(cite_matrix0), "records. Completed: . . . ", end='')
    final_matrix = {}
    for c, i in enumerate(cite_matrix0.keys()):
        if c % 1000 == 0: print(c, " . . . ", end='')
        newlist = []
        for j in cite_matrix0.keys():
            for k in cite_matrix0[j]:
                if k[1] == i: 
                    nextCount += 1
                    newlist.append(j)
        # Remove duplicates from next list
        newset = set(newlist)
        newlist = list(newset)
        final_matrix[i] = {"id":i, "previous":cite_matrix0[i], "next":newlist}     
    print("Done.")

    # Pickle and save matrix
    pickle.dump(final_matrix, open(savepath, "wb"))

    # Final Report
    print("Matrix finsihed.")
    print("Previous Count:", prevCount)
    print("Next Count:", nextCount)

    return final_matrix





def gen_cite_dict(jurisdictions=['DE']):
    """
    Generates (and saves as a text file) a citation dictionary for opinions
    in the database.  Citations (a string) are mapped to the citation's
    ID number (an integer) in the database.
    """

    cite_dict = dict()    

    dupeCount = 0
    for jx in jurisdictions:
    
        # Check the jurisdiction 
        if (jx == "Delaware") or (jx == "DE"): jxstr = "Delaware_decourtdoc"
        elif (jx == "Pennsylvania") or (jx == "PA"): jxstr = "Pennsylvania_pacourtdoc"
        elif (jx == "Federal") or (jx == "US"): jxstr = "Federal_uscourtdoc"
        else:
            print("Invalid Jurisdiction:", jx)
            return False
    
        # Connect to the database for the jurisdiction
        conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
        cur = conn.cursor()
        sql = "SELECT * FROM \"" + jxstr + "\";"
        cur.execute(sql)
        
        # LOOPS THROUGH EVERY ITEM IN THE DATABASE
        for result in cur:
            for c in range(14, 19): # Loops through each of the citation fields, Citation1, Citation2, etc.
                if result[c]: # If the citation field is populated,
                    if result[c] != "NONE": # and the ciation is not a blank WL cite, add it to the cite dict
                        if result[c] in cite_dict.keys(): dupeCount += 1
                        cite_dict[result[c]] = int(result[0])

    print("Dupe count:", dupeCount)
    return cite_dict

