# This program conducts TF-IDF Analysis on a text given some input information
# tf is defined as the frequency of a term in a particular text/document
# idf is defined as the number of texts/documents divided by the number of texts/documents in which the term appears

import nltk
import os
import io
import string

from collections import defaultdict

novels_dir = "./corpus/novels"

filename = "1930-01_As_I_Lay_Dying.txt"

section_delimiters = ["DARL", "CORA", "JEWEL", "DEWEY DELL", "TULL", "ANSE", "PEABODY"]

# The Sound and The Fury: []
# As I Lay Dying:  []

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
  # Remove blanks and blank spaces
  text = [word for word in text if word != "" and word != " "]
  return text

def populateFreqDicts(textfile, documentFreqDicts, corpusFreqs):
	allwords = set()
	currSection = ""
	# Populate documentFreqDicts going by sections of a document
	for line in textfile:
		if line.strip() in section_delimiters:
			currSection = line.strip()
			continue
		for word in line:
			word = filter(str.isalnum, word).lower().strip()
			if word == "":
				continue
			documentFreqDicts[currSection][word] += 1
			allwords.add(word)
	# Populate corpusFreqs by checking word counts across all sections
	for word in allwords:
		for section in section_delimiters:
			if documentFreqDicts[section][word] > 0:
				corpusFreqs[word] += 1

def tf(term, documentFreqs):
	return 1 + log(documentFreqs[term])

def idf(term, corpusFreqs):
	return log(1 + len(section_delimiters) / corpusFreqs[term])

def tfidf(term, documentFreqs, corpusFreqs):
	return tf(term, documentFreqs) * idf(term, corpusFreqs)

def main():
	print("TF-IDF Module:")
	# Creates a dictionary of word:("number of texts word appears in")
	corpusFreqs = defaultdict(lambda: 0)
	# Creates a dictionary of word:("freq in document") for each document with a section delimiter
	# e.g. documentFreqDicts[delimiter][word] returns the frequency of the 'word' in the section delimited by 'delimiter'
	documentFreqDicts = defaultdict(lambda: defaultdict(lambda: 0))
	with open(novels_dir + "/" + filename, "r") as textfile:
		populateFreqDicts(textfile, documentFreqDicts, corpusFreqs)




if __name__ == "__main__":
  main()