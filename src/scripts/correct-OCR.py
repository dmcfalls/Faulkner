# This script attempts to correct basic transcription errors in texts
# generated with OCR

# NOTE: as of now this script doesn't work; putting this on hold.

import nltk
import os
import re

pathname = "./corpus/novels/1926-01_Soldiers_Pay.txt"
output = "./out.txt"

lexicon_path = "./resources/dictionaries/english-dictionary-umich.txt"

def get_dictionary():
	with open(lexicon_path, "r") as file:
		dictionary = [word.lower() for line in file for word in line.split()]
	file.close()
	print("Imported dictionary with {} words".format(len(dictionary)))
	return set(dictionary)

# Returns the number of additions, replacements, and deletions needed
# to transform word into target
def correction_cost(word, target):
	if abs(len(word) - len(target)) > 2:
		return 100
	if len(word) == 0 or len(target) == 0:
		return max(len(word), len(target))
	cost = 0
	if word[-1] != target[-1]:
		cost = 1
	return min(correction_cost(word[:-1], target), correction_cost(word, target[:-1]), correction_cost(word[:-1], target[:-1]) + cost)

# Returns the word from the dictionary that results from the minimum
# number of transformations of the given word
def min_cost_correction(word, dictionary):
	print("Finding min cost correction for {}".format(word))
	min_cost = 100
	min_cost_target = word
	for target in dictionary:
		cost = correction_cost(word, target)
		if cost < min_cost:
			min_cost = cost
			min_cost_target = target
	return (min_cost, min_cost_target)

def main():
	dictionary = get_dictionary()
	with open(pathname, "r") as textfile:
		with open(output, "w") as outputfile:
			# Iterate across words in the file
			for line in textfile:
				for word in re.split(r'(\s+)', line):
					# Replace word with word from dictionary if min-cost replacement has cost < 3
					word_clean = word.strip().lower()
					if '\n' in word or '\r\n' in word or word in dictionary or word_clean in dictionary:
						outputfile.write(word)
					else:
						(cost, correction) = min_cost_correction(word_clean, dictionary)
						if cost < 3:
							outputfile.write(correction)
							outputfile.write(" ")
						else:
							outputfile.write(word)
	textfile.close()
	outputfile.close()

if __name__ == "__main__":
	main()
