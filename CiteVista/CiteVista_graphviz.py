#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 14:10:49 2019

@author: dan

Scripts that create graphs of citation relationships.  These scripts are used
on the website to create custom graphs.  See www.librelaw.com

The "standard_inverse" script draws a graph using a maximum "degree" and a 
maximum "depth".  The degree is the maximum number of nodes shown in each layer.  
The depth is the number of steps (i.e., layers) from the starting node.
The degree is decreased by a factor of 2 and the process is repeated 
recursively until the maximum depth has been reached.


"""


import os
import sys
import pickle
from graphviz import Digraph


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEcourtDoc
from Pennsylvania.models import PAcourtDoc

CiteMatrixDir = "/home/dan/Data/CiteVista/CiteMatrix/"



def load_cite_matrix(path=CiteMatrixDir+"matrix_de0.p"):
    return pickle.load(open(path, "rb"))





def standard_inverse(LID, cite_matrix, database='DE', prev_degree=8, prev_depth=2, next_degree=10, next_depth=1):
    """
    Standard graph method.  See description above.

    LID: Identification number of the starting node
    cite_matrix: a Citematrix object - see CiteVista_matrix
    prev_degree: The maximum degree for previous cases, i.e., cases the document cites
    prev_depth: The maximum depth for previous cases
    next_degree: The maximum degree for next cases, i.e., cases that cite the document
    next_degree: The maximum depth for next cases
    """
    if database=='DE': db = DEcourtDoc.objects
    elif database=='PA': db = PAcourtDoc.objects
    else:
        print("Invalid Database.")
        return False

    dot = Digraph(comment="CiteVista", format='svg')

    prev_recursive(str(LID), "0", db, cite_matrix, dot, prev_degree, prev_depth, [], [])
    next_recursive(str(LID), "0", db, cite_matrix, dot, next_degree, next_depth, [], [])

    #dot.render('Delaware/static/Delaware/graphs/cust.svg')
    dot.view()








def prev_recursive(docID, nextID, db, cite_matrix, dot, max_degree, depth, Vlist, Elist):
    """
    Standard recursive method for "previous" cases - those that the document
    in question cites and come previous in time.
    
    Each time the recursive method is called, the degree is decreased by
    a factor of two.

    POSSIBLE CHANGE: Generalize by creating ability to set the factor by which
    the degree is changed in each step.    
    """    
    
    doc = db.get(pk=int(docID))
    text = insertSpacing(doc.Slug0, 17)
    dot.node(str(docID), text)
    if nextID == "0": dot.node(str(docID), text, color="#f6ff52", style="filled")
    else: dot.node(str(docID), text, fontsize=str(12 - depth))
    Vlist.append(str(docID))

    if depth <= 0: return

    weighted_list = []
    for cite, prevID in cite_matrix[int(docID)]["previous"]:
        if prevID == -1: weight = -1
        else: weight = len(cite_matrix[prevID]["next"])
        weighted_list.append((weight, cite, prevID))
    weighted_list.sort(reverse=True)

    for n, cite, prevID in weighted_list[:max_degree]:

        if prevID == -1:
            if cite in Vlist:
                if (str(docID), cite) in Elist: continue
                dot.edge(str(docID), cite)
                Elist.append((docID, cite))
            else:
                dot.node(cite, cite, fontsize=str(12 - depth))
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
                prev_recursive(str(prevID), str(docID), db, cite_matrix, dot, int(max_degree / 2), depth - 1, Vlist, Elist)






def next_recursive(docID, nextID, db, cite_matrix, dot, max_degree, depth, Vlist, Elist):
    """
    Standard recursive method for "next" cases - those that cite the document
    in question and come next in time.

    Each time the recursive method is called, the degree is decreased by
    a factor of two.

    POSSIBLE CHANGE: Same as above: generalize by creating ability to set 
    the factor by which the degree is changed in each step.    
    """

    doc = db.get(pk=int(docID))
    text = insertSpacing(doc.Slug0, 17)
    dot.node(str(docID), text)
    if nextID == "0": dot.node(str(docID), text, color="#f6ff52", style="filled")
    else: dot.node(str(docID), text, fontsize=str(12 - depth))
    Vlist.append(str(docID))

    if depth <= 0: return

    weighted_list = []
    for nextID in cite_matrix[int(docID)]["next"]:
        if nextID == -1: weight = -1
        else: weight = len(cite_matrix[nextID]["next"])
        weighted_list.append((weight, nextID))
    weighted_list.sort(reverse=True)

    for n, nextID in weighted_list[:max_degree]:

        if nextID in Vlist:
            if (str(nextID), str(docID)) in Elist: continue
            dot.edge(str(nextID), str(docID))
            Elist.append((str(nextID), str(docID)))
        else:
            if (str(nextID), str(docID)) in Elist: continue
            dot.edge(str(nextID), str(docID))
            Elist.append((str(nextID), str(docID)))
            next_recursive(str(nextID), str(docID), db, cite_matrix, dot, int(max_degree / 2), depth - 1, Vlist, Elist)




def insertSpacing(text, n):
    """
    Formats text for display in graphviz node bubbles.  When dot.node
    is called, text prepared by this function should be supplied.

    Inserts newline characters every n characters so that the text wraps
    in the graphiz node bubble.

    text: String of text for which we will add newline characters
    n: The maximum number of characters per line in the graphviz bubble.
    """
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
