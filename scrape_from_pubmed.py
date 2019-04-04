
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 13:50:39 2019

@author: liangkc
"""

# you need to install Biopython:
# pip install biopython

# Full discussion:
# https://marcobonzanini.wordpress.com/2015/01/12/searching-pubmed-with-python/

from Bio import Entrez
from bs4 import BeautifulSoup

def search(query):
	Entrez.email = 'your.email@example.com'
	handle = Entrez.esearch(db='pmc', 
							sort='relevance', 
							retmax='2',
							retmode='xml', 
							reldate = '3650',
							term=query)
	results = Entrez.read(handle)
	return results

def fetch_details(id_list):
	ids = ','.join(id_list)
	Entrez.email = 'your.email@example.com'
	handle = Entrez.efetch(db='pmc',
						   retmode='xml',
						   id=ids)
	results=BeautifulSoup(handle, features="xml")
	return results

if __name__ == '__main__':
	results = search('optical coherence tomography')
	id_list = results['IdList']
	papers = fetch_details(id_list)
	for paper in papers.findAll('mixed-citation'):
		pmcid = dict(paper.attrs)
		try:
			print(paper.find('article-title').contents)
		except:
			print('no article title')
		#print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
	# Pretty print the first paper in full
	#import json
#print(json.dumps(papers[0], indent=2, separators=(',', ':')))