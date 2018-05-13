# Collects basic metrics on the Faulkner corpus

import nltk
import os
import string

from nltk.tokenize import word_tokenize         # word_tokenize(text)
from nltk.tokenize import sent_tokenize         # sent_tokenize(text)
from nltk.stem.porter import PorterStemmer      # PorterStemmer
from nltk.probability import FreqDist           # FreqDist

novels_dir = "./corpus/novels"

def clean_text(textfile):
    # Split into words separated by whitespace
    text = [word for line in textfile for word in line.split()]
    # Remove punctuation
    trans_table = string.maketrans(string.punctuation, " " * len(string.punctuation))
    text = [word.translate(trans_table).strip() for word in text]
    # Normalize to lower-case
    text = [word.lower() for word in text]
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

def lexical_diversity(text):
    return 1.0 * len(set(text)) / len(text)

def unique_words(text):
    return len(set(text))

def most_frequent_words(text):
    return []

def print_basic_metrics(text):
    print("Word count: " + str(len(text)))
    print("Unique words: " + str(unique_words(text)))
    print("Lexical diversity: " + str(lexical_diversity(text)))

def main():
    print("Basic Metrics:\n")

    # Stores the text for each novel using title as key
    text_by_title = dict()
    # Stores stemmed text for each novel using title as key
    stemmed_text_by_title = dict()
    # Stores stemmed text with common words removed, for each novel, using title as key
    stemmed_filtered_text_by_title = dict()
    # Stores frequency distributions for each text using title as key
    freq_dist_by_title = dict()
    # FreqDists for stemmed text
    stemmed_freq_dist_by_title = dict()
    # FreqDists for stemmed, filtered text
    stemmed_filtered_freq_dist_by_title = dict()

    # List of frequently used stop words in English
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

    # Process text files
    for filename in os.listdir(novels_dir):
        if filename.endswith(".txt"):
            curr_title = title_from_filename(filename)
            print(curr_title + ":")
            with open(novels_dir + "/" + filename, "r") as textfile:
                # Creates a clean list of words in the novel, stores in text dictionary
                text = clean_text(textfile)
                text_by_title[curr_title] = text
                # Creates a frequency distribution for the current title, stores in dictionary
                freq_dist_by_title[curr_title] = FreqDist(text)
                # Creates a list of stemmed words in the novel, stores in dictionary
                porter = PorterStemmer()
                stemmed_text_by_title[curr_title] = [porter.stem(w.decode("utf-8")) for w in text]
                stemmed_filtered_text_by_title[curr_title] = [w for w in text if not w in stop_words]

                # Prints some of the basic metrics for the current text
                print_basic_metrics(text)
            print("")

        textfile.close()

if __name__ == "__main__":
    main()
