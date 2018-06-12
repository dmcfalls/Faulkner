# -*- coding: utf-8 -*-

# This program conducts TF-IDF Analysis on a text given some input information
# tf is defined as the frequency of a term in a particular text/document
# idf is defined as the number of texts/documents divided by the number of texts/documents in which the term appears

import nltk
import os
import io
import string
import math

from collections import defaultdict

novels_dir = "./corpus/novels"

# filename = "1929-02_The_Sound_and_the_Fury.txt"
filename = "1930-01_As_I_Lay_Dying.txt"

# section_delimiters = ["April Seventh, 1928.", "June Second, 1910.", "April Sixth, 1928.", "April Eighth, 1928."]
section_delimiters = ["DARL", "CORA", "JEWEL", "DEWEY DELL", "TULL", "ANSE", "PEABODY", "VARDAMAN", "CASH", "SAMSON", "ADDIE", "WHITFIELD", "ARMSTID", "MOSELEY", "MACGOWAN"]

# The Sound and The Fury: ["April Seventh, 1928.", "June Second, 1910.", "April Sixth, 1928.", "April Eighth, 1928."]
# As I Lay Dying:  ["DARL", "CORA", "JEWEL", "DEWEY DELL", "TULL", "ANSE", "PEABODY", "VARDAMAN", "CASH", "SAMSON", "ADDIE", "WHITFIELD", "ARMSTID", "MOSELEY", "MACGOWAN"]

# NOTES

# As I Lay Dying - Use the ALL-CAPS chapter names as indicators that words belong to a character's narration
# The Sound and the Fury - Use the four dated SECTION names as indicators that words belong to character's section

# For the above, reference Steven Ramsay's article on The Waves as inspiration

# Light in August - TODO: look for sturctual indicators (numbered chapters? character names?)

# In general: pass a list of section tokens to a function that divies up the text based on those tokens

def clean_text(textfile):
  # Split into words separated by whitespace
  text = [word for line in textfile for word in line.split()]
  # Remove non-punctuation and non-alphanumeric characters
  text = [filter(str.isalnum, word) for word in text]
  # Normalize to lower-case
  text = [word.lower() for word in text]
  # Remove blanks and blank spaces, remove whitespace from words
  text = [word.strip() for word in text if word != "" and word != " "]
  return text

section_to_marker_converter = {"April Seventh, 1928.":"Benjy", "June Second, 1910.":"Quentin", "April Sixth, 1928.":"Jason", "April Eighth, 1928.":"Dilsey"}
def section_to_marker(section):
	if section in section_to_marker_converter.keys():
		return section_to_marker_converter[section]
	return section

def populateFreqDicts(textfile, documentFreqDicts, corpusFreqs):
	all_words = set()
	currSection = ""
	# Populate documentFreqDicts going by sections of a document
	for line in textfile:
		bareline = line.rstrip().lstrip()
		if bareline in section_delimiters:
			currSection = bareline
			# print(currSection)
			continue
		for word in line.split():
			word = filter(str.isalnum, word).lower().strip()
			if word == "":
				continue
			documentFreqDicts[currSection][word] += 1
			# print("update freq of " + word + " in " + currSection + " to " + str(documentFreqDicts[currSection][word]))
			all_words.add(word)
	# Populate corpusFreqs by checking word counts across all sections
	for word in all_words:
		for section in section_delimiters:
			if documentFreqDicts[section][word] > 0:
				corpusFreqs[word] += 1

def tf(term, documentFreqs):
	if documentFreqs[term] == 0:
		return 0.0
	return 1.0 + math.log(documentFreqs[term])

def idf(term, corpusFreqs):
	if corpusFreqs[term] == 0:
		return 0.0
	return math.log(1 + 1.0 * len(section_delimiters) / corpusFreqs[term])

def tfidf(term, documentFreqs, corpusFreqs):
	return 1.0 * tf(term, documentFreqs) * idf(term, corpusFreqs)

def print_highest_weight_terms(section, documentFreqDicts, corpusFreqs, all_words):
	N = 30
	topline = "Highest weighted terms in " + section_to_marker(section) + " section(s):\n"
	print(topline)
	print("Words:          Weights:")
	tfidf_weights = dict()
	for word in all_words:
		tfidf_weights[word] = tfidf(word, documentFreqDicts[section], corpusFreqs)
	terms_by_weight = reversed(sorted(tfidf_weights.iteritems(), key = lambda (k,v): (v, k)))
	count = 0
	for key, value in terms_by_weight:
		print("{:<15} {:<15}".format(key, value))
		count += 1
		if(count == N):
			break
	print("-" * len(topline) + "\n")

def main():
	print("TF-IDF Analysis Module:\n")
	# Creates a dictionary of word:("number of texts word appears in")
	corpusFreqs = defaultdict(lambda: 0)
	# Creates a dictionary of word:("freq in document") for each document with a section delimiter
	# e.g. documentFreqDicts[delimiter][word] returns the frequency of the 'word' in the section delimited by 'delimiter'
	documentFreqDicts = defaultdict(lambda: defaultdict(lambda: 0))
	all_words = set()
	with open(novels_dir + "/" + filename, "r") as textfile:
		populateFreqDicts(textfile, documentFreqDicts, corpusFreqs)
		textfile.seek(0)
		all_words = set(clean_text(textfile))
	# Print the highest weight terms for the desired section
	for section in section_delimiters:
		print_highest_weight_terms(section, documentFreqDicts, corpusFreqs, all_words)

if __name__ == "__main__":
  main()