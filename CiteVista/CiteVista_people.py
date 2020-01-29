#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 18:37:43 2019

@author: dan
"""



import en_core_web_sm, en_core_web_lg  # Part of spacy - MIT license






def get_people_orgs(text):
    
    nlp = en_core_web_lg.load()
    doc = nlp(text)
    orgs = [x.text for x in doc.ents if x.label_ == 'ORG']
    people = [x.text for x in doc.ents if x.label_ == 'PERSON']
    #pprint([(x.text, x.label_) for x in doc.ents])

    orgdict = dict()
    for item in orgs:
        if item in orgdict.keys(): orgdict[item] += 1
        else: orgdict[item] = 1
    orgs = list(orgdict.items())
    orgs.sort(key = lambda x: x[1], reverse=True)
        
    peopledict = dict()
    for item in people:
        if item in peopledict.keys(): peopledict[item] += 1
        else: peopledict[item] = 1
    people = list(peopledict.items())
    people.sort(key = lambda x: x[1], reverse=True)    

    people = filter_people_orgs(people)

    return people, orgs
    




def filter_people_orgs(plist):
    newlist = []
    for p in plist:
        fail = False
        pro = p[0].lower()
        for word in dqList_PeopleOrgs:
            if word in pro:
                fail = True
                break
        if not fail: newlist.append(p)
    return newlist


dqList_PeopleOrgs = ['plaintiff', 'defendant', 'complaint',
                     'merger']


