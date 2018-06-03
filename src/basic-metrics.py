# Collects basic metrics on the Faulkner corpus

import nltk
import os
import io
import string

import spacy
import en_core_web_sm

from nltk.tokenize import word_tokenize         # word_tokenize(text)
from nltk.tokenize import sent_tokenize         # sent_tokenize(text)
from nltk.stem.porter import PorterStemmer      # PorterStemmer()
from nltk.probability import FreqDist           # FreqDist()
from nltk.tree import Tree                      # Tree()

novels_dir = "./corpus/novels"

en_nlp = en_core_web_sm.load()

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

def average_word_length(text):
    totalChars = 0
    for word in text:
        totalChars += len(word)
    return 1.0 * totalChars / len(text)

def average_sentence_length(text, sentences):
    return 1.0 * len(text) / len(sentences)

def pos_percent(count, text):
    return 1.0 * count / len(text)

def part_of_speech_metrics(text):
    tagged_text = nltk.pos_tag(text, tagset = 'universal')
    tagged_fd = nltk.FreqDist(tag for (word, tag) in tagged_text)
    noun_pct = pos_percent(tagged_fd["NOUN"], text)
    verb_pct = pos_percent(tagged_fd["VERB"], text)
    adj_pct = pos_percent(tagged_fd["ADJ"], text)
    adv_pct = pos_percent(tagged_fd["ADV"], text)
    pron_pct = pos_percent(tagged_fd["PRON"], text)
    return (noun_pct, verb_pct, adj_pct, adv_pct, pron_pct)

# Given a tree from spacy's en_nlp(), convert into an NLTK Tree object
# From this stackoverflow post: https://stackoverflow.com/questions/36610179/how-to-get-the-dependency-tree-with-spacy
def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return Tree(node.orth_, [])

# Reports the depth of the deepest node in the given NLTK Tree object
def tree_depth(tree):
    return max(len(pos) for pos in tree.treepositions())

# parse the sentences into CFG trees and report the average depth of the tree as a measure of sentences complexity
# TODO: implement
def average_tree_depth(sentences):
    total_depths = 0
    n_sentences = 0
    for sentence in sentences:
        doc = en_nlp(sentence)
        for sent in doc.sents:
            total_depths += tree_depth(to_nltk_tree(sent.root))
            n_sentences += 1
    return 1.0 * total_depths / n_sentences

# reports the average size of a chunk of text; can give insight into how much ideas are modified
# TODO: implement
def average_chunk_size(sentences):
    return 1.0

def sentence_complexity_metrics(text, sentences):
    atd = average_tree_depth(sentences)
    acs = average_chunk_size(sentences)
    return (atd, acs)

def print_title_and_underline(title):
    print(title + ":")
    underline = "-" * len(title) + "-"
    print(underline)

def print_basic_metrics(text, sentences, stemmed_text, stemmed_filtered_text):
    print("Word count: " + str(len(text)))
    print("Sentence count: " + str(len(sentences)))
    print("Unique words: " + str(unique_words(text)))
    print("Unique words (stemmed): " + str(unique_words(stemmed_text)))
    print("Average word length: {0:.3f}".format(average_word_length(text)))
    print("Average sentence length: {0:.2f}".format(average_sentence_length(text, sentences)))
    print("Lexical diversity: {0:.6f}".format(lexical_diversity(stemmed_text)))

def print_most_frequent_words(freq_dist):
    for (word, freq) in most_frequent_words(freq_dist):
        print("  " + word + " (" + str(freq) + ")")

def print_part_of_speech_data(text):
    (n, v, adj, adv, prn) = part_of_speech_metrics(text)
    print("  Noun%: {0:.3f}".format(n))
    print("  Verb%: {0:.3f}".format(v))
    print("  Adjective%: {0:.3f}".format(adj))
    print("  Adverb%: {0:.3f}".format(adv))
    print("  Pronoun%: {0:.3f}".format(prn))

def print_sentence_complexity_data(text, sentences):
    (atd, acs) = sentence_complexity_metrics(text, sentences)
    print("Average sentence tree depth: {0:.3f}".format(atd))
    print("Average sentence component chunk size (unfinished): {0:.3f}".format(acs))

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
                #print("Part of speech percentages:")
                #print_part_of_speech_data(text)
                print("Sentence complexity metrics:")
                print_sentence_complexity_data(text, sentences)
                print("Most frequent words (stemmed & filtered):")
                print_most_frequent_words(stemmed_filtered_freq_dist_by_title[curr_title])
            print("")
            textfile.close()

if __name__ == "__main__":
    main()
