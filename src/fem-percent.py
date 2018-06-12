# -*- coding: utf-8 -*-

# Measures the rough percentage of a text concerned with female characters/actors/objects

import nltk
import os
import io
import string
import csv

# novels_dir = "./corpus/novels"
# novels_dir = "./corpus/higher_brow"
novels_dir = "./corpus/lower_brow"

char_names_dir = "./resources/character_names"

female_character_names_file = "female_character_names.txt"
male_character_names_file = "male_character_names.txt"

fem_markers = ["she", "her", "hers", "herself", "mrs", "ms", "miss", "mme", "madame", "woman", "girl", "lady", "queen", "princess", "female", "feminine", "mother", "daughter", "wife", "aunt", "auntie", "belle", "granny", "mom"]
masc_markers = ["he", "him", "his", "himself", "mr", "man", "reverend", "boy", "gentleman", "king", "prince", "male", "masculine", "captain", "colonel", "father", "son", "husband", "uncle", "dad"]

USE_CHARACTER_NAMES = False

VERBOSE = False
OUTPUT_CSVFILE = True
output_filename = "./out.csv"

def char_names_from_path(path):
	if(not USE_CHARACTER_NAMES):
		return set([])
	with open(path, "r") as textfile:
		names = [line for line in textfile]
		names = [word.lower().strip() for word in names]
	return set(names)

fem_characters = char_names_from_path(char_names_dir + "/" + female_character_names_file)
male_characters = char_names_from_path(char_names_dir + "/" + male_character_names_file)

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

def separate_author_and_filename(filename):
    if filename[:4] == "dime":
        underscore_index = 10
        return ("Dime Novel", "#" + filename[(underscore_index + 1):])
    elif not (filename[:4]).isdigit():
        underscore_index = filename.index("_")
        author = filename[:underscore_index]
        year_and_title = filename[(underscore_index + 1):]
        return (author, year_and_title)
    else:
        return ("Faulkner", filename)

def title_from_filename(filename):
    (author, year_and_title) = separate_author_and_filename(filename)
    # All files are prefixed by "YEAR_0X_"
    prefixlen = 8
    # All files have filetype ".txt"
    suffixlen = 4
    # Special check for dime novel corpus
    if(author == "Dime Novel"):
        return year_and_title[:-suffixlen]
    title = year_and_title[prefixlen : -suffixlen]
    # Special checks for "Soldiers' Pay" and  "Go Down, Moses"
    if("Soldiers_Pay" in title):
        title = "Soldiers' Pay"
    if("Go_Down_Moses" in title):
        title = "Go Down, Moses"
    return title.replace("_", " ")

def print_title_and_underline(title):
  print(title + ":")
  underline = "-" * len(title) + "-"
  print(underline)

def is_fem_token(word):
	if word in fem_markers or word in fem_characters:
		return True

def is_masc_token(word):
	if word in masc_markers or word in male_characters:
		return True

# Returns a pair (femme_percent, masc_percent) given a text
def generate_gender_percentages(text, title):
	fem_words = 0
	masc_words = 0
	total_words = 0
	# curr_gender can be either "masc" or "fem", refers to last marker/character seen
	curr_gender = "masc"
	for word in text:
		if is_fem_token(word):
			curr_gender = "fem"
		elif is_masc_token(word):
			curr_gender = "masc"
		if curr_gender == "fem":
			fem_words += 1
		elif curr_gender == "masc":
			masc_words += 1
		total_words += 1
	fem_percent = 1.0 * fem_words / total_words * 100
	masc_percent = 1.0 * masc_words / total_words * 100
	return (fem_percent, masc_percent)

# Returns a pair (femme_percent, masc_percent) given a text
# Stricter than the naive algorithm above: requires words fall between two markers of the same kind
def generate_gender_percentages_strict(text, title):
	fem_words = 0
	masc_words = 0
	total_words = 0
	# last_gender can be "neut", "masc", or "fem", refers to last marker/character
	prev_gender = "neut"
	curr_gender = "neut"
	words_since_last_change = 0
	for word in text:
		# Assign gender to current word
		if is_fem_token(word):
			curr_gender = "fem"
		elif is_masc_token(word):
			curr_gender = "masc"
		else:
			curr_gender = "neut"
		# Gendered word assignment if last segment of text bounded by same-kind markers
		if curr_gender == "fem" and prev_gender == "fem":
			fem_words += words_since_last_change
		elif curr_gender == "masc" and prev_gender == "masc":
			masc_words += words_since_last_change
		# Housekeeping
		if curr_gender == "fem" or curr_gender == "masc":
			prev_gender = curr_gender
			words_since_last_change = 0
		words_since_last_change += 1
		total_words += 1
	fem_percent = 1.0 * fem_words / total_words * 100
	masc_percent = 1.0 * masc_words / total_words * 100
	return (fem_percent, masc_percent)

# Returns the raw counts of feminine/masculine marker words and female/male names
def generate_gender_statistics(text):
	fem_marker_ct = 0
	masc_marker_ct = 0
	fem_names_ct = 0
	male_names_ct = 0
	for word in text:
		if word in fem_markers:
			fem_marker_ct += 1
		elif word in masc_markers:
			masc_marker_ct += 1
		elif word in fem_characters:
			fem_names_ct += 1
		elif word in male_characters:
			male_names_ct += 1
	return (fem_marker_ct, masc_marker_ct, fem_names_ct, male_names_ct)

def fem_to_masc_marker_ratio(fem_marker_ct, masc_marker_ct):
	return 1.0 * fem_marker_ct / masc_marker_ct

def fem_to_male_name_ratio(fem_name_ct, male_name_ct):
	if(not USE_CHARACTER_NAMES):
		return 0
	return 1.0 * fem_name_ct / male_name_ct

# Indicates how often female names are used relative to marker words (higher number indicates names used more often)
def fem_name_to_marker_ratio(fem_name_ct, fem_marker_ct):
	if(not USE_CHARACTER_NAMES):
		return 0
	return 1.0 * fem_name_ct / fem_marker_ct

# Indicates how often male names are used relative to marker words (higher number indicates names used more often)
def male_name_to_marker_ratio(male_name_ct, masc_marker_ct):
	if(not USE_CHARACTER_NAMES):
		return 0
	return 1.0 * male_name_ct / masc_marker_ct

def fem_weighted_score(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent):
	total_fem_ct = fem_marker_ct + fem_name_ct
	total_fm_word_ct = fem_marker_ct + fem_name_ct + masc_marker_ct + male_name_ct
	total_text_percent = fem_percent + masc_percent
	return 0.5 * total_fem_ct / total_fm_word_ct + 0.5 * fem_percent / total_text_percent

def male_weighted_score(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent):
	total_masc_ct = masc_marker_ct + male_name_ct
	total_fm_word_ct = fem_marker_ct + fem_name_ct + masc_marker_ct + male_name_ct
	total_text_percent = fem_percent + masc_percent
	return 0.5 * total_masc_ct / total_fm_word_ct + 0.5 * masc_percent / total_text_percent

def fem_to_male_weighted_ratio(fem_score, masc_score):
	return 1.0 * fem_score / masc_score

# Returns meaningful statistics (to be decided upon) related to gender in the text
def calculate_gender_ratios(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent):
	ftmmr = fem_to_masc_marker_ratio(fem_marker_ct, masc_marker_ct)
	ftmnr = fem_to_male_name_ratio(fem_name_ct, male_name_ct)
	fntmr = fem_name_to_marker_ratio(fem_name_ct, fem_marker_ct)
	mntmr = male_name_to_marker_ratio(male_name_ct, masc_marker_ct)
	fws = fem_weighted_score(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent)
	mws = male_weighted_score(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent)
	ftmwr = fem_to_male_weighted_ratio(fws, mws)
	return (ftmmr, ftmnr, fntmr, mntmr, fws, mws, ftmwr)

def gender_metrics_from_text(text, title):
	(fp, mp) = generate_gender_percentages(text, title)
	(fps, mps) = generate_gender_percentages_strict(text, title)
	(fmc, mmc, fnc, mnc) = generate_gender_statistics(text)
	(ftmmr, ftmnr, fntmr, mntmr, fws, mws, ftmwr) = calculate_gender_ratios(fmc, fnc, mmc, mnc, fp, mp)
	return [title, fp, mp, fps, mps, fmc, mmc, fnc, mnc, ftmmr, ftmnr, fntmr, mntmr, fws, mws, ftmwr]

headers = ["Title", "Fem%", "Masc%", "Fem% (strict)", "Masc% (strict)", "Female marker words", "Male marker words", "Female names", "Male names", "FtM marker ratio", "FtM name ratio", "Fem NtM ratio", "Masc NtM ratio", "Fem weighted score", "Masc weighted score", "FtM weighted ratio"]
def write_headers_to_file(filename):
    with open(filename, "a") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers)
        print("Wrote headers to csv file\n")

def write_data_to_file(data, filename):
    with open(filename, "a") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(data)
        print("Wrote data to csv file")

def main():
	print("Percentage text bounded by female identifiers:")
	print("")

	if(OUTPUT_CSVFILE):
		write_headers_to_file(output_filename)

	for filename in os.listdir(novels_dir):
		if filename.endswith(".txt"):
			curr_title = title_from_filename(filename)
			print_title_and_underline(curr_title)
			with open(novels_dir + "/" + filename, "r") as textfile:
				text = clean_text(textfile)
				if(OUTPUT_CSVFILE):
					data = gender_metrics_from_text(text, curr_title)
					write_data_to_file(data, output_filename)
				if(VERBOSE):
					(fem_percent, masc_percent) = generate_gender_percentages(text, curr_title)
					print("Fem%: {0:.2f}".format(fem_percent))
					print("Masc%: {0:.2f}".format(masc_percent))
					print("")
					(fem_percent_strict, masc_percent_strict) = generate_gender_percentages_strict(text, curr_title)
					print("Fem% (strict): {0:.2f}".format(fem_percent_strict))
					print("Masc% (strict): {0:.2f}".format(masc_percent_strict))
					print("")
					(fem_marker_ct, masc_marker_ct, fem_name_ct, male_name_ct) = generate_gender_statistics(text)
					print("Female marker words: {}".format(fem_marker_ct))
					print("Male marker words: {}".format(masc_marker_ct))
					print("Female names: {}".format(fem_name_ct))
					print("Male names: {}".format(male_name_ct))
					print("")
					(ftmmr, ftmnr, fntmr, mntmr, fws, mws, ftmwr) = calculate_gender_ratios(fem_marker_ct, fem_name_ct, masc_marker_ct, male_name_ct, fem_percent, masc_percent)
					print("Fem to masc marker ratio: {0:.3f}".format(ftmmr))
					print("Fem to male name ratio: {0:.3f}".format(ftmnr))
					print("Fem name to marker ratio: {0:.3f}".format(fntmr))
					print("Masc name to marker ratio: {0:.3f}".format(mntmr))
					print("Female weighted score: {0:.3f}".format(fws))
					print("Male weighted score: {0:.3f}".format(mws))
					print("Female-to-male weighted ratio: {0:.3f}".format(ftmwr))
			textfile.close()
			print("")

if __name__ == "__main__":
  main()