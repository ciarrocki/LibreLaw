### Scripts to download and parse legal opinions

- OPparser_text*: Functions to clean text, find relevant sections, split footnotes, and extract parties, court, 
jurisdiction, and date. These functions operate on raw text.  Splitting footnotes is especially prone to error if the 
text is irregular.

- OPparser_data.py: downloads data from (a) Courtlistener; and (b) Delaware government website

- OPlawbox: scripts specially designed to parse the "lawbox" opinions on CourtListener, which are well-formatted and need less processing.
