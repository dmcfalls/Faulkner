# Collects basic metrics on the Faulkner corpus

import nltk
import os
import io
import string

from nltk.tokenize import word_tokenize         # word_tokenize(text)
from nltk.tokenize import sent_tokenize         # sent_tokenize(text)
from nltk.stem.porter import PorterStemmer      # PorterStemmer
from nltk.probability import FreqDist           # FreqDist

novels_dir = "./corpus/novels"

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

def lexical_diversity(text):
    return 1.0 * len(set(text)) / len(text)

def unique_words(text):
    return len(set(text))

def most_frequent_words(freq_dist):
    N = 20
    return freq_dist.most_common(N)

def average_sentence_length(text, sentences):
    return 1.0 * len(text) / len(sentences)

def print_title_and_underline(title):
    print(title + ":")
    underline = "-" * len(title) + "-"
    print(underline)

def print_basic_metrics(text, sentences, stemmed_text, stemmed_filtered_text):
    print("Word count: " + str(len(text)))
    print("Sentence count: " + str(len(sentences)))
    print("Unique words: " + str(unique_words(text)))
    print("Unique words (stemmed): " + str(unique_words(stemmed_text)))
    print("Average sentence length: {0:.2f}".format(average_sentence_length(text, sentences)))
    print("Lexical diversity: {0:.6f}".format(lexical_diversity(stemmed_text)))

def print_most_frequent_words(freq_dist):
    for (word, freq) in most_frequent_words(freq_dist):
        print("  " + word + " (" + str(freq) + ")")

def main():
    print_title_and_underline("Basic Metrics")
    print("")

    # Stores the text (as a list of words) for each novel using title as key
    text_by_title = dict()
    # Stores the text (as a list of sentences) for each novel using title as key
    sentences_by_title = dict()
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
            print_title_and_underline(curr_title)
            with open(novels_dir + "/" + filename, "r") as textfile:
                # Creates a clean list of words in the novel, stores in text dictionary
                text = clean_text(textfile)
                text_by_title[curr_title] = text
                # Creates a list of sentences in the novel, stores in dictionary
                textfile.seek(0)    # Reset filestream
                sentences = sent_tokenize(textfile.read().decode("utf-8"))
                sentences_by_title[curr_title] = sentences
                
                # Creates a frequency distribution for the current title, stores in dictionary
                freq_dist_by_title[curr_title] = FreqDist(text)
                # Creates a list of stemmed words in the novel, stores in dictionary
                porter = PorterStemmer()
                stemmed_text_by_title[curr_title] = [porter.stem(w.decode("utf-8")) for w in text]
                stemmed_filtered_text_by_title[curr_title] = [w for w in text if not w in stop_words]

                # Prints some of the basic metrics for the current text
                stemmed_text = stemmed_text_by_title[curr_title]
                stemmed_filtered_text = stemmed_filtered_text_by_title[curr_title]
                
                # Specialized frequency distributions 
                stemmed_freq_dist_by_title[curr_title] = FreqDist(stemmed_text)
                stemmed_filtered_freq_dist_by_title[curr_title] = FreqDist(stemmed_filtered_text)

                print_basic_metrics(text, sentences, stemmed_text, stemmed_filtered_text)
                # print("Most frequent words:")
                # print_most_frequent_words(freq_dist_by_title[curr_title])
                print("Most frequent words (stemmed & filtered):")
                print_most_frequent_words(stemmed_filtered_freq_dist_by_title[curr_title])
            print("")
            textfile.close()

if __name__ == "__main__":
    main()
