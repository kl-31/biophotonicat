
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
from xml.dom import minidom
import csv

def search(query):
	Entrez.email = 'your.email@example.com'
	handle = Entrez.esearch(db='pubmed', 
							sort='most+recent', 
							retmax='100000',
							retmode='xml', 
							reldate = '3650',
							term=query)
	results = Entrez.read(handle)
	return results

def fetch_details(id_list):
	ids = ','.join(id_list)
	Entrez.email = 'your.email@example.com'
	handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
	#results = Entrez.read(handle)
	return handle

if __name__ == '__main__':

	with open('paper-titles-data.csv', mode='w') as data_file:
		file_writer =  csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		results = search('biomedical optics')
		id_list = results['IdList']
		papers = fetch_details(id_list)
		data = minidom.parse(papers)
		for title in data.getElementsByTagName("ArticleTitle"):
			for node in title.childNodes:
				if node.nodeType == node.TEXT_NODE:
					print(node.data)
					try:
						file_writer.writerow([node.data, '1'])
					except:
							pass
	data_file.close()
#		for i, paper in enumerate(papers['PubmedArticle']):
#			#file_writer.writerow([paper['MedlineCitation']['Article']['ArticleTitle'], '1'])
#			print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))