# Measures the rough percentage of a text concerned with female characters/actors/objects

import nltk
import os
import io
import string

novels_dir = "./corpus/novels"
char_names_dir = "./resources/character_names"

female_character_names_file = "female_character_names.txt"
male_character_names_file = "male_character_names.txt"

fem_markers = ["she", "her", "hers", "herself", "mrs", "ms", "miss", "mme", "madame", "woman", "girl", "lady", "queen", "princess", "female", "feminine", "mother", "daughter", "wife", "aunt", "auntie", "belle", "granny", "mom"]
masc_markers = ["he", "him", "his", "himself", "mr", "man", "reverend", "boy", "gentleman", "king", "prince", "male", "masculine", "captain", "colonel", "father", "son", "husband", "uncle", "dad"]

def char_names_from_path(path):
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

def title_from_filename(filename):
  # All files are prefixed by "YEAR_0X_"
  prefixlen = 8
  # All files have filetype ".txt"
  suffixlen = 4
  title = filename[prefixlen : -suffixlen]
  # Special checks for "Soldiers' Pay" and  "Go Down, Moses"
  if("Soldiers" in title):
    title = "Soldiers' Pay"
  if("Go_Down" in title):
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
	femme_percent = 1.0 * fem_words / total_words * 100
	masc_percent = 1.0 * masc_words / total_words * 100
	return (femme_percent, masc_percent)

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
	femme_percent = 1.0 * fem_words / total_words * 100
	masc_percent = 1.0 * masc_words / total_words * 100
	return (femme_percent, masc_percent)

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

# Returns meaningful statistics (to be decided upon) related to gender in the text
# TODO: implement
def calculate_gender_ratios():
	return 0

def main():
	print("Percentage text bounded by female identifiers:")
	print("")
	for filename in os.listdir(novels_dir):
		if filename.endswith(".txt"):
			curr_title = title_from_filename(filename)
			print_title_and_underline(curr_title)
			with open(novels_dir + "/" + filename, "r") as textfile:
				text = clean_text(textfile)
				(femme_percent, masc_percent) = generate_gender_percentages(text, curr_title)
				print("Fem%: {0:.2f}".format(femme_percent))
				print("Masc%: {0:.2f}".format(masc_percent))
				print("")
				(femme_percent, masc_percent) = generate_gender_percentages_strict(text, curr_title)
				print("Fem% (strict): {0:.2f}".format(femme_percent))
				print("Masc% (strict): {0:.2f}".format(masc_percent))
				print("")
				(fem_marker_ct, masc_marker_ct, fem_names_ct, male_names_ct) = generate_gender_statistics(text)
				print("Female marker words: {}".format(fem_marker_ct))
				print("Male marker words: {}".format(masc_marker_ct))
				print("Female names: {}".format(fem_names_ct))
				print("Male names: {}".format(male_names_ct))
			textfile.close()
			print("")

if __name__ == "__main__":
  main()