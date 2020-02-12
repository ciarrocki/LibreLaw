# NLP Scripts

These scripts support NLP functionality on the website.  

The most important modules are:

- CiteVista_graphviz.py: Algorithms used to draw graphs of citation relationships among cases.  Uses the graphviz library to create and render the graphs.  Relies on cite_matrix dictionaries created by CiteVista_matrix.

- CiteVista_matrix.py: Creates the cite_matrix dictionary, which stores the documents each opinion in a database cites and each opinion in the database that cites that opinion.  In essence, the cite_matrix dictionary is an adjancency-matrix based on citation relationships.  The key for each entry is the docID of the opinion in question.  Each entry provides two fields: (1) a list of the opinions that cite this opinion; and (2) a list of the opinions that this opinion cites

- CiteVista_people.py: Scripts to load spaCy NLP model, identify named entities, and then filter results.  Also contains scripts to clean text before processing with spaCy.  To come: training with custom data.

- CiteVista_wl.py: Find Westlaw citations in public database materials.  The Westlaw citations are found by first creating a list of all Westlaw-style citations in case text, e.g., United States v. Bennett, 2005 WL 2709572 (W.D.N.Y. Oct. 21, 2005).  Cases in the database that do not have a reporter citation are then evaluated against this list to find matches.



