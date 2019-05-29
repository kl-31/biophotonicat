# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 05:28:51 2019

@author: KCLIANG
Helper functions for biophotobot.
"""
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.externals import joblib
import pandas as pd
import numpy as np
from unidecode import unidecode
import string
import json
from os.path import isfile,splitext,isdir
from os import environ,remove,makedirs
import tweepy
from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import datetime
from bs4 import BeautifulSoup
import urllib
from subprocess import call
from shutil import rmtree
import patoolib
import glob
from random import choice, randint
from PyPDF2 import PdfFileReader

#import bitly_api
#import sys

scopes = ['https://spreadsheets.google.com/feeds',
	  'https://www.googleapis.com/auth/drive']
keyfile_dict = {
    'auth_provider_x509_cert_url': environ['GSPREAD_AUTH_PROVIDER'],
    'auth_uri': environ['GSPREAD_AUTH_URI'],
    'client_email': environ['GSPREAD_CLIENT_EMAIL'],
    'client_id': environ['GSPREAD_CLIENT_ID'],
    'client_x509_cert_url': environ['GSPREAD_CLIENT_X509'],
    'private_key': environ['GSPREAD_PRIVATE_KEY'].replace('\\n', '\n'),
    'private_key_id': environ['GSPREAD_PRIVATE_KEY_ID'],
    'project_id': environ['GSPREAD_PROJECT_ID'],
    'token_uri': environ['GSPREAD_TOKEN_URI'],
    'type': environ['GSPREAD_TYPE']
}


def get_titles_db():
	#print(keyfile_dict)
	creds = ServiceAccountCredentials.from_json_keyfile_dict(
    keyfile_dict=keyfile_dict, scopes=scopes)
	#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	client = gspread.authorize(creds)
	sh = client.open_by_key('1PoD8M5_fg33gdAktthKXrsyPwHMqSMASDRIX1i_zYtk')
	worksheet = sh.sheet1
	titles_list = worksheet.col_values(1)	
	return titles_list

def write_to_db(row):
	creds = ServiceAccountCredentials.from_json_keyfile_dict(
    keyfile_dict=keyfile_dict, scopes=scopes)
	#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	client = gspread.authorize(creds)
	sh = client.open_by_key('1PoD8M5_fg33gdAktthKXrsyPwHMqSMASDRIX1i_zYtk')
	worksheet = sh.sheet1
	worksheet.insert_row(row+[str(datetime.date.today())],1)
	sleep(1) # google api 60 write requests per 60 sec
	return


def normalize_text(s):
	s=''.join([i for i in s if not i.isdigit()]) # remove numbers
	s = s.replace('-',' ')
	s = s.replace('/',' ')
	s = s.replace('μ','u')
	s = unidecode(str(s))
	s=s.translate(s.maketrans('', '', string.punctuation)) # remove punctuation
	s = s.lower() # make lowercase
	s = s.replace('  ',' ') # remove double spaces
	return s

def strip_html(s):
		if s[:3]=='<p>' and not s[-4:]=='</p>': # differentiate between Nature and Science abstract formats
			soup = BeautifulSoup(s,'lxml')
			soup.p.decompose()
			s = soup.get_text() 
		return s
	
def scrape_image(raw, journal):
	if raw == '':
		return False
	
	if isdir('./data/'):
		rmtree('./data/')
		
	if journal == "Journal of Biophotonics":
		#print(raw)
		makedirs('./data/',exist_ok=True)
		soup = BeautifulSoup(raw,'lxml')
		if len(soup.find_all('img', src=True))==0:
			return False
		link = soup.find_all('img', src=True)[0]['src']
		extension = splitext(urllib.parse.urlparse(link).path)[-1]
		urllib.request.urlretrieve(link,'./data/tweet_pic'+extension)
		call(['convert','-density','300','-define', 'trim:percent-background=2%','-trim','+repage','-background', 'white', '-alpha', 'remove', '-alpha', 'off','./data/tweet_pic'+extension,'./data/tweet_pic.png'])

	elif journal == "Biorxiv Biophys/Bioeng":
		makedirs('./data/',exist_ok=True)
		paper_id = urllib.parse.urlparse(raw).path.split('/')[-1]
		paper_path = 'https://www.biorxiv.org/content/10.1101/' + paper_id + '.full'
		soup = BeautifulSoup(urllib.request.urlopen(paper_path).read(),'lxml')
		links_raw = soup.find_all('a',{'class':'highwire-figure-link highwire-figure-link-download'})
		if len(links_raw) == 0:
			pdf_raw = soup.find_all('meta',{'name':'citation_pdf_url'})
			pdf_raw = pdf_raw[0]['content']
			urllib.request.urlretrieve(pdf_raw,'./data/paper'+'.pdf')
			pdf = PdfFileReader(open('./data/paper.pdf','rb'))
			n_pages = pdf.getNumPages()
			page_num = randint(0,n_pages)
			call(['convert','-density','300','-define', 'trim:percent-background=2%','-trim','+repage','-background', 'white', '-alpha', 'remove', '-alpha', 'off','./data/paper.pdf['+ str(page_num)+']','./data/tweet_pic.png'])
		else:
			links = []
			for link in links_raw:
				links.append(link['href'])
			pic_raw = choice(links)
			urllib.request.urlretrieve(pic_raw,'./data/pic_raw'+'.jpg')
			call(['convert','-density','300','-define', 'trim:percent-background=2%','-trim','+repage','-background', 'white', '-alpha', 'remove', '-alpha', 'off','./data/pic_raw.jpg','./data/tweet_pic.png'])

		
		
	elif journal == "Arxiv Optics":
		makedirs('./data/',exist_ok=True)
		urllib.request.urlretrieve(raw.replace('abs','e-print'),'source')
		if isdir('./data/'):
			rmtree('./data/')
		makedirs('./data/',exist_ok=True)
		try:	
			patoolib.extract_archive("source", outdir="./data/")
		except:
			return False	
	#	if glob.glob('./data/' + '**/*.tex', recursive=True) !=[]:
		files = glob.glob('./data/' + '**/*.png', recursive=True)
		if files != []:
			picraw = choice(files)
			call(['convert','-density','300','-define', 'trim:percent-background=2%','-trim','+repage','-background', 'white', '-alpha', 'remove', '-alpha', 'off', picraw+'[0]','./data/tweet_pic.png'])
			return True
		else:
			otherfiles = glob.glob('./data/' + '**/*.pdf', recursive=True) + glob.glob('./data/' + '**/*.eps', recursive=True) + glob.glob('./data/' + '**/*.ps', recursive=True)
			if otherfiles != []:
				picraw = choice(otherfiles)
				call(['convert','-density','300','-define', 'trim:percent-background=2%','-trim','+repage','-background', 'white', '-alpha', 'remove', '-alpha', 'off', picraw+'[0]','./data/tweet_pic.png'])
				return True
			else:
				return False		
	
	if isfile('./data/tweet_pic.png'):
		return True
	else:
		return False

def compute_proba(titles):
	vectorizer = HashingVectorizer(ngram_range=(1, 3))
	
	titles = pd.DataFrame(titles,columns=['title','link','journal_name','abstract'])
	titles['abstract'] = [re.sub(r'^(.*?)<br\/>','',str(s)) for s in titles['abstract']] # remove all text up to and including <br\>
	titles['abstract'] = [re.sub(r'\[[^\[\]]*\]','',str(s)) for s in titles['abstract']] # remove all text within [] brackets
	titles['abstract'] = [strip_html(s) for s in titles['abstract']]
	titles['text'] = [normalize_text(re.sub(r'\([^()]*\)', '', str(s))) for s in titles['title']+titles['abstract']] # already has a space after title
	X_test = vectorizer.fit_transform(titles['text'])
	clf = joblib.load('new_trained_model.pkl')
	
	pred = clf.predict_proba(X_test)
	#arr = np.empty((np.size(titles,0),4),dtype=object)
	arr = [None] * 5
	arr[0] = titles['title'][0]
	arr[1] = titles['link'][0]
	arr[2] = titles['journal_name'][0]
	arr[3] = titles['abstract'][0]
	arr[4] = float(pred[:,1])
	return arr
	

def tweet_post(line,image_flag):
	auth = tweepy.OAuthHandler(environ['TWITTER_CONSUMER_KEY'], environ['TWITTER_CONSUMER_SECRET'])
	auth.set_access_token(environ['TWITTER_ACCESS_TOKEN'], environ['TWITTER_ACCESS_SECRET'])
	api = tweepy.API(auth)	
	try:
		if image_flag == False:
			api.update_status(line)
			sleep(60*60) 
			return True
		else:
			api.update_with_media('./data/tweet_pic.png',line)
			sleep(60*60) 
			return True
	except tweepy.TweepError as e:
		print(e.args[0][0]['message'])
		return False

#def shorten_link(link):
#	b = bitly_api.Connection(API_USER, API_KEY)
#	response = b.shorten(link)
#	return response['url']