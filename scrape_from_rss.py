import feedparser
#import csv
#import string
from unidecode import unidecode
import json
from os.path import isfile
import helpers


if isfile('feed_info.txt'):
	feed_info = json.load(open("feed_info.txt"))
else:
	feed_info = {
			'optica': 
				{'name':'Optica', 
				 'path': 'http://metadata.osa.org/rss/infobase/optica_feed.xml',
				 'etag':''},
			 'lsa':
				 {'name': 'Light: Science and Applications',
				'path': 'http://feeds.nature.com/lsa/rss/current?fmt=xml',
				  'etag': ''},
			  'nat_photon':
				  {'name':'Nature Photonics',
				   'path': 'http://www.nature.com/nphoton/journal/vaop/ncurrent/rss.rdf',
				   'etag': ''},
			'oe':
				{'name': 'Optics Express',
					 'path': 'http://metadata.osa.org/rss/infobase/opex_feed.xml',
					 'etag': ''},
				'boe':
					{'name': 'Biomedical Optics Express',
					  'path': 'http://metadata.osa.org/rss/infobase/boe_feed.xml',
					  'etag': ''},
				'ol':
					{'name': 'Optics Letters',
					  'path': 'http://metadata.osa.org/rss/infobase/ol_feed.xml',
					  'etag': ''},
				'nat_meth':
					{'name': 'Nature Methods',
						'path': 'http://www.nature.com/nmeth/journal/vaop/ncurrent/rss.rdf',
						'etag': ''},
				'nat_bme':
					{'name': 'Nature BME',
						  'path': 'http://feeds.nature.com/natbiomedeng/rss/current?fmt=xml',
						  'etag': ''},
					'science':
					{'name': 'Science',
						  'path': 'http://science.sciencemag.org/rss/express.xml',
						  'etag': ''},
					'nat_comms':
					{'name': 'Nature Communications',
						  'path': 'http://feeds.nature.com/ncomms/rss/current?fmt=xml',
						  'etag': ''},
					  'science_advances':
					{'name': 'Science Advances',
						  'path': 'https://advances.sciencemag.org/rss/current.xml',
						  'etag': ''}
					}

written = 0
posted = 0
titles_list = helpers.get_titles_db()
for feed in feed_info.keys():	
	print(feed)
	feed_name = feed_info[feed]['name']
	feed_path = feed_info[feed]['path']
	feed_rss = feedparser.parse(feed_path)
	for i in range(len(feed_rss.entries)):
		entry = feed_rss.entries[i]
		if feed_name == 'Journal of Biophotonics': # for each journal, there is a raw source/link from which image can be pulled.
			image_raw = entry.content[0].value
			authors_raw = entry.authors
		elif feed_name == 'Arxiv Optics':
			image_raw = entry.link
			authors_raw = entry.authors
		elif feed_name == "Biorxiv Biophys/Bioeng": 
			image_raw = entry.link
			authors_raw = entry.link # scrape authors from html
		elif feed_name == 'Science':
			image_raw = ''
			authors_raw = entry.link # scrape authors from html
		elif feed_name == 'Science Advances':
			image_raw = entry.link
			authors_raw = entry.link # scrape authors from html
		else:
			image_raw = ''
			authors_raw = entry.authors
		abstract = unidecode(entry.summary.replace('\n',' '))
		row = [[unidecode(entry.title), entry.link, feed_name, abstract ]] 
		if row[0][0].strip().lower() not in titles_list:
			proba_out = helpers.compute_proba(row)
			#print(proba_out)
			helpers.write_to_db(proba_out)
			written = written + 1
			if proba_out[-1] >=0.6:
				handles = helpers.get_author_handles(authors_raw,feed_name)
				if helpers.tweet_post('%s (relevance: %.0f%%) %s #biophotonics #biomedicaloptics %s' % (entry.title, proba_out[-1]* 100,entry.link,handles),helpers.scrape_image(image_raw,feed_name)):
						posted = posted + 1
			elif proba_out[-1] < 0.6 and (feed_name == 'Biomedical Optics Express' or feed_name == 'Journal of Biophotonics'):
				handles = helpers.get_author_handles(authors_raw,feed_name)
				if helpers.tweet_post('%s (relevance: %.0f%% but cat probably meowssed up) %s #biophotonics #biomedicaloptics %s' % (entry.title, proba_out[-1]* 100, entry.link,handles),helpers.scrape_image(image_raw,feed_name)):
						posted = posted + 1
				
		if posted >=22: # 22 hours elapsed  
		   break
	if posted >=22: # 22 hours elapsed  
		break
			#print('%d: %s' % (i,row[0]))
print('%d rows written.' % written)
print('%d tweets posted.' % posted)