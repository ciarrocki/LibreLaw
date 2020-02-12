# LibreLaw - A Free Database of Legal Materials
## Visit the website at: www.librelaw.com

Welcome to LibreLaw.  The goal of this project is to support research and analysis of legal materials using open-source natural language processing tools.  The website is the front-end for a database containing over 200,000 legal documents.  These documents are fully searchable, and search results can be filtered by various categories.  The website also includes NLP tools for analyzing the materials, like: 
 - Create custom graphs of citation relationships among opinions
 - Identify people and organizations in texts

This repository contains some of the source-code that supports the www.librelaw.com website.  Specifically, you can find the scripts that:

 - Download raw opinions, statutes, and court rules 
 - Process and parse the raw text or PDFs so they can be stored as tabular data with defined dates, courts, jurisdictions, and other fields.
 - Analyze the corpus for connections between documents and build data structures that support the graphical citeview featured on the website.
 - Extract the names of people and organizations from any opinion in the corpus.

All comments and ideas are welcome.


### Guide to the Repository

 - <strong>CiteVista</strong>: NLP tools.  These scripts create datastructures to hold citation relationships among opinions, generate graphs that model relationships among opinions, identify people and organizations in text, and clean text in support of these functions.

 - <strong>OPparser</strong>: Scripts that download legal opinions from public sources, parse and format their content, and add them to the database.

 - <strong>STATparser</strong>: Scripts that download and parse statues and court rules from public sources, parse and format their content, and add them to the database.

 - <strong>Gensim</strong>: Experimental use of the Gensim library with the corpus of legal opinions.
