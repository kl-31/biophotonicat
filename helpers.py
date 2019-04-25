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
from os.path import isfile
from credentials import *
import tweepy
from time import sleep
#import bitly_api
import sys

def post_in_db(row):
	path = 'database.txt'
	if isfile(path):
		database = json.load(open(path))
	else: 
		return False

	title = row[0][0]
	if title in database:
			return True
	return False

def write_to_db(row):
	path = 'database.txt'
	if isfile(path):
		database = json.load(open(path))
	else: database = {}
	database[row[0][0]] = {}
	database[row[0][0]]['link']= row[0][1]
	database[row[0][0]]['journal_name']= row[0][2]
	database[row[0][0]]['prob']= row[0][3]
	json.dump(database, open(path,'w'))
	return


def normalize_text(s):
	s=''.join([i for i in s if not i.isdigit()]) # remove numbers
	s = s.replace('-',' ')
	s = s.replace('/',' ')
	s = s.replace('μ','u')
	s = unidecode(str(s))
	s=s.translate(s.maketrans('', '', string.punctuation)) # remove punctuation
	s = s.lower() # make lowercase
	return s

def compute_proba(titles):
	vectorizer = HashingVectorizer()
	
	titles = pd.DataFrame(titles,columns=['title','link','journal_name'])
	titles['text'] = [normalize_text(str(s)) for s in titles['title']]
	X_test = vectorizer.fit_transform(titles['text'])
	clf = joblib.load('trained_model.pkl')
	
	pred = clf.predict_proba(X_test)
	arr = np.empty((np.size(titles,0),4),dtype=object)
	arr[:,0] = np.array(titles['title'])
	arr[:,1] = np.array(titles['link'])
	arr[:,2] = np.array(titles['journal_name'])
	arr[:,3] = pred[:,2]
	
	# dont determine relevance in this function
#	relevant = np.where([i[2]>=0.5 for i in pred])[0]
#	irrelevant = np.where([i[2]<0.5 for i in pred])[0]
#	#print(pred)
#	relevant_arr = np.empty((len(relevant),4),dtype=object)
#	relevant_arr[:,0] = np.array(titles.loc[relevant,'title'])
#	relevant_arr[:,1] = np.array(titles.loc[relevant,'link'])
#	relevant_arr[:,2] = np.array(titles.loc[relevant,'journal_name'])
#	relevant_arr[:,3] = pred[relevant,2]
#	print(relevant_arr)
#	print('%d relevant papers found.' % len(relevant))
#	print(np.array(titles.loc[irrelevant,'title']))
#	print('%d irrelevant papers found.' % len(irrelevant))
	
	return arr
	

def tweet_post(line):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)	
	api.update_status(line)
	sleep(300)
	return

#def shorten_link(link):
#	b = bitly_api.Connection(API_USER, API_KEY)
#	response = b.shorten(link)
#	return response['url']