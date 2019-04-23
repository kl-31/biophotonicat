
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
from xml.etree.ElementTree import iterparse
import csv
import time
import datetime

def search(query,retmax):
	Entrez.email = 'your.email@example.com'
	handle = Entrez.esearch(db='pubmed', 
							sort='relevant', 
							retmax=str(retmax),
							#retstart = '10000',
							retmode='xml', 
							#reldate = '3650',
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

	groups = [['physics', 'biology','engineering'],
			   ['physics optics','engineering optics'],
			   ['biomedical optics', 'biophotonics']]
	start = time.time()
	with open('paper-titles-data.csv', mode='w') as data_file:
		file_writer =  csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for group in groups:
			if groups.index(group)==0:
				retmax=4000
			else:
				retmax = 6000
			for query in group:
				i = 0
				results = search(query,retmax)
				id_list = results['IdList']
				papers = fetch_details(id_list)
				for event, elem in iterparse(papers):
					try:
						if elem.tag == 'ArticleTitle':
							#print(str(i)+elem.text)
							file_writer.writerow([elem.text, str(groups.index(group))])
							i = i+1
							elem.clear()
					except:
						pass
				print('%d titles saved in %s.' % (i,query))
	data_file.close()
	end = time.time()
	print('Time elapsed: %s' % datetime.timedelta(seconds=round(end - start)))
	
#		for i, paper in enumerate(papers['PubmedArticle']):
#			#file_writer.writerow([paper['MedlineCitation']['Article']['ArticleTitle'], '1'])
#			print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))