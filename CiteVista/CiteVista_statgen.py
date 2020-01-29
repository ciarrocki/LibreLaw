#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 20:17:33 2020

@author: dan
"""



import psycopg2
import json
import sys
import os


### Set up Django API Environment
sys.path.append("/home/dan/LibreLaw/LibreLaw")
os.environ['DJANGO_SETTINGS_MODULE'] = 'LibreLaw.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibreLaw.settings")
import django
django.setup()
from Delaware.models import DEstat







def gen_save_stats_all():
    stats_all, as_string = gen_stats_all()
    save_stats(as_string)
    return stats_all






def gen_stats_all():
    
    doc_stats = gen_stats_docs()
    word_stats = gen_stats_words()
        
    stats_all = doc_stats[0]
    stats_all.update(word_stats[0])

    as_string = json.dumps(stats_all)

    return stats_all, as_string






def gen_stats_docs():

    conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM \"Delaware_decourtdoc\";")
    decourtdoc = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM \"Pennsylvania_pacourtdoc\";")
    pacourtdoc = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM \"Federal_uscourtdoc\";")
    uscourtdoc = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM \"Delaware_destat\" WHERE \"TitleNum\" < 1000;")
    destat = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM \"Delaware_destat\" WHERE \"TitleNum\" >= 1000;")
    derules = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM \"Pennsylvania_pastat\" WHERE \"TitleNum\" < 1000;")
    pastat = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM \"Pennsylvania_pastat\" WHERE \"TitleNum\" >= 1000;")
    parules = cur.fetchone()[0]

    conn.close()
    
    total_courtdocs = decourtdoc + pacourtdoc + uscourtdoc
    total_stat = destat + pastat
    total_rules = derules + parules
    total_de = decourtdoc + destat + derules
    total_pa = pacourtdoc + pastat + parules
    total_us = uscourtdoc
    total_total = total_courtdocs + total_stat + total_rules

    results = {'total_docs':total_total, 'total_courtdoc_docs':total_courtdocs,
               'total_stat_docs':total_stat, 'total_rules_docs':total_rules,
               'decourtdoc_docs':decourtdoc, 'pacourtdoc_docs':pacourtdoc, 
               'uscourtdoc_docs':uscourtdoc, 'destat_docs':destat, 'pastat_docs':pastat,
               'derules_docs':derules, 'parules_docs':parules, 'total_de_docs':total_de,
               'total_pa_docs':total_pa, 'total_us_docs':total_us}

    results_as_string = json.dumps(results)

    return results, results_as_string




def gen_stats_words():

    print("Delaware databases:")
    decourtdoc = get_words_courtdocs("Delaware_decourtdoc")
    destat = get_words_stats("Delaware_destat", max_title_num=999)
    derules = get_words_stats("Delaware_destat", min_title_num=1000)

    print("\nPennsylvania databases:")
    pacourtdoc = get_words_courtdocs("Pennsylvania_pacourtdoc")
    pastat = get_words_stats("Pennsylvania_pastat", max_title_num=999)
    parules = get_words_stats("Pennsylvania_pastat", min_title_num=1000)

    print("\nFederal databases:")
    uscourtdoc = get_words_courtdocs("Federal_uscourtdoc")

    total_courtdoc = decourtdoc + pacourtdoc + uscourtdoc
    total_stat = destat + pastat
    total_rules = derules + parules
    total_de = decourtdoc + destat + derules
    total_pa = pacourtdoc + pastat + parules
    total_us = uscourtdoc
    total_total = total_courtdoc + total_stat + total_rules

    results = {'total_words':total_total, 'total_courtdoc_words':total_courtdoc,
               'total_stat_words':total_stat, 'total_rules_words':total_rules,
               'decourtdoc_words':decourtdoc, 'pacourtdoc_words':pacourtdoc, 
               'uscourtdoc_words':uscourtdoc, 'destat_words':destat, 'pastat_words':pastat,
               'derules_words':derules, 'parules_words':parules,
               'total_de_words':total_de, 'total_pa_words':total_pa,
               'total_us_words':total_us}

    results_as_string = json.dumps(results)

    return results, results_as_string
    





def get_words_courtdocs(table_name):

    conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
    cur = conn.cursor()

    cur.execute("SELECT * FROM \"" + table_name + "\";")

    totalwords = 0
    print("Progress: ", end='')
    for i, result in enumerate(cur.fetchall()):
        if i % 1000 == 0: print('*', end='')
        caseName = result[10]
        mainText = result[12]
        footnotes = result[13]
        numwords = len(caseName.split()) + len(mainText.split()) + len(footnotes.split())
        totalwords += numwords
    print(" Done.")

    conn.close()

    return totalwords





def get_words_stats(table_name, max_title_num=-1, min_title_num=-1):

    conn = psycopg2.connect("dbname=librelaw user=libreuser password=" + password)
    cur = conn.cursor()

    if max_title_num != -1: cur.execute("SELECT * FROM \"" + table_name + "\" WHERE \"TitleNum\" <= " + str(max_title_num)+ ";")
    elif min_title_num != -1: cur.execute("SELECT * FROM \"" + table_name + "\" WHERE \"TitleNum\" >= " + str(min_title_num)+ ";")
    else: cur.execute("SELECT * FROM \"" + table_name + "\";")

    totalwords = 0
    print("Progress: ", end='')
    for i, result in enumerate(cur.fetchall()):
        if i % 1000 == 0: print('*', end='')
        title = result[1]
        text = result[5]
        numwords = len(title) + len(text)
        totalwords += numwords
    print(" Done.")

    conn.close()

    return totalwords





def save_stats(stat_string):
        
    newStat = DEstat()
    
    newStat.Title = "Database Statistics"
    newStat.SectionType = "Stats"
    newStat.TitleNum = 7777
    newStat.Number = 7777
    newStat.Text = stat_string
    newStat.Previous = ""
    newStat.Next = ""
    newStat.Source = ""
    newStat.Filepath = ""
    newStat.Tree0 = ""
    newStat.Tree1 = ""
    newStat.Tree2 = ""
    newStat.Tree3 = ""
    newStat.Tree4 = ""
    newStat.Tree5 = ""
    newStat.Tree6 = ""
    newStat.Tree7 = ""
    newStat.Tree8 = ""
    newStat.Tree9 = ""
    newStat.Citation0 = ""
    newStat.Citation1 = ""

    newStat.save()
    
    return True




