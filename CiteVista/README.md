# NLP Scripts

These scripts support NLP functionality on the website.  

The most important modules are:

- CiteVista_graphviz.py: Algorithms used to draw graphs of citation relationships among cases.  Uses the graphviz library to create and render the graphs.  Relies on cite_matrix dictionary objects created by CiteVista_matrix.

- CiteVista_matrix.py: Creates the cite_matrix dictionary, which stores the documents each opinion in a database cites and each opinion in the database that cites that opinion.  The key for each entry is the docID of the opinion in question.  Each entry provides two fields: (1) a list of the opinions that cite this opinion; and (2) a list of the opinions that this opinion cites

- CiteVista_people.py:

- CiteVista_wl.py:



