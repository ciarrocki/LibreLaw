#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 16:23:43 2019

@author: dan
"""



WLdateRE = r"[A-Za-z]{1,10}\.?\s*\d{1,2}((\,)|(\,\s+)|(\s+))(19|20)\d\d"


citePatterns_stateReporters = [
            r"\d{1,3}\s*((a\.?\s?(2|3)d)|(a\.))\s*\d{1,4}", # Atlantic Reporter ("345 A.2d 678"); A.;A.2d;A.3d
            r"\d{1,3}\s*((p\.?\s?(2|3)d)|(p\.))\s*\d{1,4}", # Pacific Reporter ("345 P.2d 678"); P.;P.2d;P.3d
            r"\d{1,3}\s*s\.?o\.?(\s?(2|3)d\.?)?\s*\d{1,4}", # Southern Reporter ("345 So. 2d 456"); So.;So. 2d;So. 3d.
            r"\d{1,3}\s*n\.?e\.?(\s?(2|3)d\.?)?\s*\d{1,4}", # North Eastern Reporter ("345 N.E.2d 654"); N.E.;N.E.2d;N.E.3d
            r"\d{1,3}\s*n\.?w\.?(\s?2d\.?)?\s*\d{1,4}", # North Western Reporter ("345 N.W.2d 654"); N.W.;N.W.2d
            r"\d{1,3}\s*s\.?e\.?(\s?2d\.?)?\s*\d{1,4}", # South Eastern Reporter ("345 S.E.2d 654"); S.E.;S.E.2d
            r"\d{1,3}\s*s\.?w\.?(\s?(2|3)d\.?)?\s*\d{1,4}", # South Western Reporter ("345 S.W.2d 654"); S.W.;S.W.2d;S.W.3d
            r"\d{1,3}\s*n\.?y\.?s\.?(\s?(2|3)d\.?)?\s*\d{1,4}", # New York Supplement ("345 N.Y.S. 2d 678"); N.Y.S.;N.Y.S. 2d;N.Y.S. 3d
            # CALIFORNIA REPORTER!!!
            # California Reporter: Cal. Rptr.;Cal. Rptr. 2d;Cal. Rptr. 3d
]

citePatterns_federalReporters = [
        r"\d{1,3}\s*f\.?(\s?(2|3)d\.?)?\s*\d{1,4}", # Federal Reporter ("345 F.2d 678"); F.;F.2d;F.3d
        r"\d{1,3}\s*f\.?\s*supp\.?(\s*(2|3)d\.?)?\s*\d{1,4}", # Federal Supplement ("345 F. Supp.2d 678"); F. Supp.;F. Supp.2d;F. Supp.3d
        r"\d{1,3}\s*f\.?r\.?d\.?\s*\d{1,4}", # Federal Rules Decisions ("345 F.R.D. 678"); F.R.D.
        r"\d{1,3}\s*b\.?r\.?\s*\d{1,4}", # Bankruptcy Court Reporter ("345 B.R. 678"); B.R.
        r"\d{1,3}\s*t\.?c\.?\s*\d{1,4}", # Tax Court Reporter ("345 T.C. 678"); T.C.
        r"\d{1,3}\s*u\.?s\.?\s*\d{1,4}", # Official SCOTUS ("345 U.S. 678"); U.S.
        r"\d{1,3}\s*s\.?ct\.?\s*\d{1,4}", # West SCOTUS ("345 S.Ct. 678"); S.Ct.
        r"\d{1,3}\s*fed\.?cl\.?\s*\d{1,4}", # Federal Claims Reporter ("345 Fed. Cl. 678"); Fed. Cl.
        r"\d{1,3}\s*vet\.?\s*app\.?\s*\d{1,4}", # Veteran Appeals Reporter ("345 Vet. App. 678"); Vet. App.
        r"\d{1,3}\s*m\.?j\.?\s*\d{1,4}", # Military Justice Reporter ("345 M.J. 678"); M.J.
        r"\d{1,3}\s*f\.?\s*app(\'|\’)?x\s*\d{1,4}", # Federal Appendix ("345 F. App'x 678"); F. App'x
]

citePatterns_westlaw = [
        r"(19|20)\d\d\s*wl\s*\d{3,12}", # Westlaw Format ("2016 WL 435398"); WL
] 

citePatterns_lexis = [
]


citePatterns_all = citePatterns_stateReporters + citePatterns_federalReporters +\
                    citePatterns_westlaw + citePatterns_lexis



WLsearchPatterns = [
        r"(19|20)\d\d\s*wl\s*\d{3,12}", # Westlaw Format ("2016 WL 435398"); WL
]



findCites_keywords = ['state', 'of', 'the', 'a', 'v.', 'in', 're', 're:',
    'stockholders', 'stockholder', 'litigation', "s'holders", 'litig.', 'derivative', 'deriv.',
    'individual', 'indiv.', 'behalf',
    'llc', 'l.l.c.', 'llc.', 'corp.', 'co.', 'group', 'inc.', 'inc', 'co', 'corp',
    'lp', 'l.p.', 'lp.', 'c/o', 'trust', 'imo', 'partners', 'association', 'n.a.',
    'company', 'associates', 'corporation', 'matter', 'estate', 'holdings',
    'assoc.', "ass'n", 'enterprises', 'enters.', 'homeowners', 'limited',
    'capital', 'acquisition', 'delaware', 'county', 'cnty.', 'city',
    'pension', 'estate', 'a/k/a/', 'deceased',
    'writ', 'petition', 'rel.', 'pennsylvania', 'commonwealth']