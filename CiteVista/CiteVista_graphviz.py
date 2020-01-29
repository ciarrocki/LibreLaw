#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 14:10:49 2019

@author: dan
"""


import os
import sys

from graphviz import Digraph


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc



o0 = 138849  # Airgas
o1 = 116640 # Zohar





def drawPrevNext(docID, cite_matrix, database='DE', maxNext=10, maxPrev=10):
    
    if database=='DE': doc = DEcourtDoc.objects.get(pk=docID)
    elif database=='PA': doc = PAcourtDoc.objects.get(pk=docID)

    dot = Digraph(comment="CiteVista", format='svg')
    text = insertSpacing(doc.CaseName, 20)
    dot.node('A', text, URL="http://www.espn.com")
    
    for i, (cite, prevID) in enumerate(cite_matrix[docID]["previous"][:maxPrev]):
        if prevID == -1: 
            dot.node('p' + str(i), cite)
            dot.edge('A', 'p' + str(i))
            continue
        else:
            prevDoc = DEcourtDoc.objects.get(pk=prevID)
            text = insertSpacing(prevDoc.CaseName, 15)
            dot.node('p' + str(i), text)
            dot.edge('A', 'p' + str(i))


    for i, nextID in enumerate(cite_matrix[docID]["next"][:maxNext]):
        nextDoc = DEcourtDoc.objects.get(pk=nextID)
        text = insertSpacing(nextDoc.CaseName, 15)
        dot.node('n' + str(i), text)
        dot.edge('n' + str(i), 'A')

    dot.view()
    #dot.render('test-output/test0.svg', view=True)






def cust1_plusnext(docID, cite_matrix, database='DE', max_next=10, maxdegree=10, depth=2):
    if database=='DE': db = DEcourtDoc.objects
    elif database=='PA': db = PAcourtDoc.objects
    else:
        print("Invalid Database.")
        return False

    dot = Digraph(comment="CiteVista")

    cust1_recursive(str(docID), "0", db, cite_matrix, dot, maxdegree, depth, [], [])

    for i, nextID in enumerate(cite_matrix[docID]["next"][:max_next]):
        nextDoc = DEcourtDoc.objects.get(pk=nextID)
        text = insertSpacing(nextDoc.CaseName, 15)
        dot.node('n' + str(i), text)
        dot.edge('n' + str(i), str(docID))

    dot.view()




def cust1(docID, cite_matrix, database='DE', maxdegree=10, depth=2):
    if database=='DE': db = DEcourtDoc.objects
    elif database=='PA': db = PAcourtDoc.objects
    else:
        print("Invalid Database.")
        return False

    dot = Digraph(comment="CiteVista")

    cust1_recursive(str(docID), "0", db, cite_matrix, dot, maxdegree, depth, [], [])

    dot.view()





def cust1_recursive(docID, nextID, db, cite_matrix, dot, maxdegree, depth, Vlist, Elist):

    doc = db.get(pk=int(docID))
    text = insertSpacing(doc.Slug0, 15)
    dot.node(str(docID), text)
    if nextID == "0": dot.node(str(docID), text, color="#f6ff52", style="filled")
    else: dot.node(str(docID), text)
    Vlist.append(str(docID))

    if depth <= 0: return

    weighted_list = []
    for cite, prevID in cite_matrix[int(docID)]["previous"]:
        if prevID == -1: weight = -1
        else: weight = len(cite_matrix[prevID]["next"])
        weighted_list.append((weight, cite, prevID))
    weighted_list.sort(reverse=True)
    #print(weighted_list)    


    for n, cite, prevID in weighted_list[:maxdegree]:

        if prevID == -1:
            if cite in Vlist:
                if (str(docID), cite) in Elist: continue
                dot.edge(str(docID), cite)
                Elist.append((docID, cite))
            else:
                dot.node(cite, cite)
                Vlist.append(cite)
                if (str(docID), cite) in Elist: continue
                dot.edge(str(docID), cite)
                Elist.append((str(docID), cite))

        else:
            if cite in Vlist:
                if (str(docID), str(prevID)) in Elist: continue
                dot.edge(str(docID), str(prevID))
                Elist.append((str(docID), str(prevID)))
            else:
                if (str(docID), str(prevID)) in Elist: continue
                dot.edge(str(docID), str(prevID))
                Elist.append((str(docID), str(prevID)))
                cust1_recursive(str(prevID), str(docID), db, cite_matrix, dot, int(maxdegree / 2), depth - 1, Vlist, Elist)

    



def draw_prev_recursive(docID, cite_matrix, database='DE', maxdegree=10, depth=2):
    if database=='DE': db = DEcourtDoc.objects
    elif database=='PA': db = PAcourtDoc.objects
    else:
        print("Invalid Database.")
        return False

    dot = Digraph(comment="CiteVista")

    recurse_prev_cites(str(docID), "0", db, cite_matrix, dot, maxdegree, depth, [], [])

    dot.view()





def recurse_prev_cites(docID, nextID, db, cite_matrix, dot, maxdegree, depth, Vlist, Elist):

    
    doc = db.get(pk=int(docID))
    text = insertSpacing(doc.Slug0, 15)
    dot.node(str(docID), text)
    Vlist.append(str(docID))

    if depth <= 0: return

    for cite, prevID in cite_matrix[int(docID)]["previous"][:maxdegree]:

        if prevID == -1:
            if cite in Vlist:
                if (str(docID), cite) in Elist: continue
                dot.edge(str(docID), cite)
                Elist.append((docID, cite))
            else:
                dot.node(cite, cite)
                Vlist.append(cite)
                if (str(docID), cite) in Elist: continue
                dot.edge(str(docID), cite)
                Elist.append((str(docID), cite))

        else:
            if cite in Vlist:
                if (str(docID), str(prevID)) in Elist: continue
                dot.edge(str(docID), str(prevID))
                Elist.append((str(docID), str(prevID)))
            else:
                if (str(docID), str(prevID)) in Elist: continue
                dot.edge(str(docID), str(prevID))
                Elist.append((str(docID), str(prevID)))
                recurse_prev_cites(str(prevID), str(docID), db, cite_matrix, dot, maxdegree, depth - 1, Vlist, Elist)





def drawPrev2(docID, cite_matrix, database='DE', maxnum=10):
    if database=='DE': doc = DEcourtDoc.objects.get(pk=docID)
    elif database=='PA': doc = PAcourtDoc.objects.get(pk=docID)
    else:
        print("Invalid Database.")
        return False

    dot = Digraph(comment="CiteVista")
    text = insertSpacing(doc.Slug0, 20)
    dot.node('A', text)
    
    for i, (cite, prevID) in enumerate(cite_matrix[docID]["previous"][:maxnum]):
        if prevID == -1:
            dot.node('p' + str(i), cite)
            dot.edge('A', 'p' + str(i))
            continue
        else:
            prevDoc = DEcourtDoc.objects.get(pk=prevID)
            text = insertSpacing(prevDoc.Slug0, 15)
            dot.node('p' + str(i), text)
            dot.edge('A', 'p' + str(i))
            for j, (cite, prevID2) in enumerate(cite_matrix[prevID]["previous"][:maxnum]):
                if prevID2 == -1:
                    dot.node('p2' + str(j), cite)
                    dot.edge('p' + str(i), 'p2' + str(j))
                    continue
                else:
                    p2doc = DEcourtDoc.objects.get(pk=prevID2)
                    text = insertSpacing(p2doc.Slug0, 15)
                    dot.node('p2' + str(j), text)
                    dot.edge('p' + str(i), 'p2' + str(j))
    
    dot.view()






def insertSpacing(text, n):
    wordlist = text.split()
    string = ""
    charCounter = 0
    for word in wordlist:
        if len(word) + charCounter > n:
            string = string + "\n" + word
            charCounter = len(word)
        else:
            string = string + " " + word
            charCounter = charCounter + len(word) + 1
    return string  
