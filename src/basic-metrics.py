# Collects basic metrics on the Faulkner corpus

import nltk
import os
import string

from nltk.tokenize import word_tokenize

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

def lexical_diversity(text):
    return 1.0 * len(set(text)) / len(text)

def unique_words(text):
    return len(set(text))

def main():
    print("Basic Metrics:\n")
    for filename in os.listdir(novels_dir):
        if filename.endswith(".txt"):
            print(filename)
            with open(novels_dir + "/" + filename, "r") as textfile:
                # Creates a list of words in the novel, stores in text
                text = clean_text(textfile)
                print("Word count: " + str(len(text)))
                print("Unique words: " + str(unique_words(text)))
                print("Lexical diversity: " + str(lexical_diversity(text)))
            print("")
        textfile.close()

if __name__ == "__main__":
    main()
