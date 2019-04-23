#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 13:23:05 2019

@author: liangkc
partly from https://www.kaggle.com/kinguistics/classifying-news-headlines-with-scikit-learn
and
mostly from https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html#sphx-glr-auto-examples-text-plot-document-classification-20newsgroups-py
"""

# get some libraries that will be useful
import string
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, ComplementNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier, GradientBoostingClassifier
from sklearn.utils.extmath import density
from sklearn import metrics
from time import time
import matplotlib.pyplot as plt

# grab the data
titles = pd.read_csv("paper-titles-data.csv", names=['title','category'])
unseen_pd = pd.read_csv("paper-titles-unseen.csv",header=None,sep='\t')

def normalize_text(s):
	s=''.join([i for i in s if not i.isdigit()]) # remove numbers
	s=s.translate(s.maketrans('', '', string.punctuation)) # remove punctuation
	s = s.lower() # make lowercase
	return s

titles['text'] = [normalize_text(str(s)) for s in titles['title']]

# split into train and test sets
data_train, data_test, y_train, y_test = train_test_split(titles['text'], titles['category'], test_size=0.2)

target_names = ['0','1','2']

# pull the data into vectors
vectorizer = HashingVectorizer(non_negative=True)
X_train = vectorizer.fit_transform(data_train)
X_test = vectorizer.fit_transform(data_test)

# test unseen data
#unseen_raw = [
#			'Moments reconstruction and local dynamic range compression of high order superresolution optical fluctuation imaging',
#			  'Interferometric scattering microscopy reveals microsecond nanoscopic protein motion on a live cell membrane',
#			  'Targeting LIF-mediated paracrine interaction for pancreatic cancer therapy and monitoring'
#			  ]
#unseen_pd = pd.DataFrame(unseen_raw,header=None)
unseen_pd['text'] = [normalize_text(str(s)) for s in unseen_pd[0]]
unseen = vectorizer.fit_transform(unseen_pd['text'])

def benchmark(clf):
	print('_' * 80)
	print("Training: ")
	print(clf)
	t0 = time()
	clf.fit(X_train, y_train)
	train_time = time() - t0
	print("train time: %0.3fs" % train_time)

	t0 = time()
	pred = clf.predict(X_test)
	test_time = time() - t0
	print("test time:  %0.3fs" % test_time)

	score = metrics.accuracy_score(y_test, pred)
	print("accuracy:   %0.3f" % score)
	

	
	print("classification report:")
	print(metrics.classification_report(y_test, pred,
											target_names=target_names))
	print("confusion matrix:")
	print(metrics.confusion_matrix(y_test, pred))
	print()
	clf_descr = str(clf).split('(')[0]
	return clf_descr, score, train_time, test_time

results = []
for clf, name in (
		(LogisticRegression(),"Logistic Regression"),
		#(RidgeClassifier(tol=1e-2, solver="sag"), "Ridge Classifier"),
		#(Perceptron(max_iter=50, tol=1e-3), "Perceptron"),
		#(PassiveAggressiveClassifier(max_iter=50, tol=1e-3),
		# "Passive-Aggressive")):
		#(KNeighborsClassifier(n_neighbors=10), "kNN")):
		):
	print('=' * 80)
	print(name)
	results.append(benchmark(clf))

for penalty in ["l2", "l1"]:
	print('=' * 80)
	print("SGD %s penalty" % penalty.upper())
	# Train Liblinear model
#	results.append(benchmark(LinearSVC(penalty=penalty, dual=False,
	#								   tol=1e-3)))

	# Train SGD model
	results.append(benchmark(SGDClassifier(alpha=.0001, max_iter=50,loss='modified_huber',
										   penalty=penalty)))

# Train SGD with Elastic Net penalty
print('=' * 80)
print("SGD Elastic-Net penalty")
results.append(benchmark(SGDClassifier(alpha=.0001, max_iter=50,loss='modified_huber',
									   penalty="elasticnet")))

# Train NearestCentroid without threshold
#print('=' * 80)
#print("NearestCentroid (aka Rocchio classifier)")
#results.append(benchmark(NearestCentroid()))

# Train sparse Naive Bayes classifiers
print('=' * 80)
print("Naive Bayes")
results.append(benchmark(MultinomialNB(alpha=.01)))
results.append(benchmark(BernoulliNB(alpha=.01)))
results.append(benchmark(ComplementNB(alpha=.1)))

print('=' * 80)
print("Ensemble")
results.append(benchmark(RandomForestClassifier(n_estimators=20,max_depth=25)))
results.append(benchmark(AdaBoostClassifier(n_estimators=20)))
results.append(benchmark(GradientBoostingClassifier(n_estimators=20)))


accuracies = [i[1] for i in results]
best_acc = accuracies.index(max(accuracies))
best_clf = results[best_acc][0]
print('Best clf: %s' % best_clf)

clf = SGDClassifier(alpha=.0001, max_iter=50,loss='modified_huber',
										   penalty='l2')
clf.fit(X_train,y_train)
unseen_pred = clf.predict_proba(unseen)
answer = [i[2]>0.4 for i in unseen_pred]
print(unseen_pred)
print(answer)
#print('=' * 80)
#print("LinearSVC with L1-based feature selection")
## The smaller C, the stronger the regularization.
## The more regularization, the more sparsity.
#results.append(benchmark(Pipeline([
#  ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False,
#												  tol=1e-3))),
#  ('classification', LinearSVC(penalty="l2"))])))

## make some plots
#
#indices = np.arange(len(results))
#
#results = [[x[i] for x in results] for i in range(4)]
#
#clf_names, score, training_time, test_time = results
#training_time = np.array(training_time) / np.max(training_time)
#test_time = np.array(test_time) / np.max(test_time)
#
#plt.figure(figsize=(12, 8))
#plt.title("Score")
#plt.barh(indices, score, .2, label="score", color='navy')
#plt.barh(indices + .3, training_time, .2, label="training time",
#		 color='c')
#plt.barh(indices + .6, test_time, .2, label="test time", color='darkorange')
#plt.yticks(())
#plt.legend(loc='best')
#plt.subplots_adjust(left=.25)
#plt.subplots_adjust(top=.95)
#plt.subplots_adjust(bottom=.05)
#
#for i, c in zip(indices, clf_names):
#	plt.text(-.3, i, c)
#
#plt.show()


