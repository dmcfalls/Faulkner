# -*- coding: utf-8 -*-

# Collects basic metrics on the Faulkner corpus

import os                                       # Filesystem interfacing
import io                                       # Input/Output
import string                                   # String methods
import csv                                      # For reading/writing .csv files

import nltk                                     # Our primary NLP suite -- simple but effective
from nltk.tokenize import word_tokenize         # word_tokenize(text)
from nltk.tokenize import sent_tokenize         # sent_tokenize(text)
from nltk.stem.porter import PorterStemmer      # PorterStemmer()
from nltk.probability import FreqDist           # FreqDist()
from nltk.tree import Tree                      # Tree()

import spacy                                    # Another NLP suite that offers sentence parsing
import en_core_web_sm                           # English interface for spacy

from stanfordcorenlp import StanfordCoreNLP     # Yet another NLP suite used for dependency parsing

OUTPUT_CSVFILE = False
VERBOSE = True

novels_dir = "./corpus/novels"                  # Faulkner's novels corpus
# novels_dir = "./corpus/higher_brow"           # Faulkner's modernist contemporaries
# novels_dir = "./corpus/lower_brow"            # Dime novels from the early 1900's
# novels_dir = "./corpus/miscellaneous"         # Other interesting novels, unrelated to project

output_filename = "./output.csv"

en_nlp = en_core_web_sm.load()

stanfordCoreNLP_directory = "./resources/stanford-corenlp-full-2018-02-27"

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

def word_count(text):
    return len(text)

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

def longest_sentence_length(sentences):
    # Shorter version; only recovers the length and not the actual sentence
    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    return max(sentence_lengths)
    # Longer version; retains and prints the longest sentence
    longest = ""
    longest_length = 0   
    for sentence in sentences:
        length = len(sentence.split())
        if(length > longest_length):
            longest_length = length
            longest = sentence
    print(longest)
    return longest_length

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
# Modified from this stackoverflow post: https://stackoverflow.com/questions/36610179/how-to-get-the-dependency-tree-with-spacy
def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return Tree(node.orth_, [])

# Reports the depth of the deepest node in the given NLTK Tree object
def tree_depth(tree):
    return max(len(pos) for pos in tree.treepositions())

# Parse the sentences into parsed trees and report the average depth of the tree as a measure of sentences complexity
def average_tree_depth(sentences):
    total_depths = 0
    n_sentences = 0
    for sentence in sentences:
        doc = en_nlp(sentence)
        for sent in doc.sents:
            total_depths += tree_depth(to_nltk_tree(sent.root))
            n_sentences += 1
    return 1.0 * total_depths / n_sentences

# Average dependency distance as defined in Oya's 2008 paper
# Applied only to sentences with >10 or <=20 words. Measures "difficulty" of reading sentences.
def average_dependency_distance(sentences):
    stanfordNLP = StanfordCoreNLP(stanfordCoreNLP_directory, memory = "8g")
    n_sentences = 0
    dd_sum = 0
    for sentence in sentences:
        sentence = sentence.encode("utf-8")
        tokens = sentence.split()
        if (len(tokens) > 20) or (len(tokens) < 10):
            continue
        curr_sum = 0
        dep_tuples = stanfordNLP.dependency_parse(sentence)
        for dep_tuple in dep_tuples:
            dist = abs(dep_tuple[2] - dep_tuple[1])
            curr_sum += dist
        curr_add = 1.0 * curr_sum / len(dep_tuples)
        n_sentences += 1
        dd_sum += curr_add
        if VERBOSE and (n_sentences % 100) == 0:
            print("  Parsed a sentence (#{0}): avg. dep. dist. = {1:.4f}".format(n_sentences, curr_add))
    stanfordNLP.close()
    return 1.0 * dd_sum / n_sentences

def sentence_complexity_metrics(text, sentences):
    atd = average_tree_depth(sentences)
    # add = average_dependency_distance(sentences)
    return (atd)

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
    (atd) = sentence_complexity_metrics(text, sentences)
    print("  Average sentence tree depth: {0:.3f}".format(atd))
    # print("  Average dependency distance: {0:.3f}".format(add))

def basic_metrics_from_text(text, sentences, stemmed_text, stemmed_filtered_text, title):
    c = word_count(text)
    sc = len(sentences)
    uw = unique_words(text)
    uws = unique_words(stemmed_text)
    awl = average_word_length(text)
    asl = average_sentence_length(text, sentences)
    ld = lexical_diversity(stemmed_text)
    (n, v, adj, adv, prn) = part_of_speech_metrics(text)
    (atd) = sentence_complexity_metrics(text, sentences)
    return [title, c, sc, uw, uws, awl, asl, ld, n, v, adj, adv, prn, atd]

headers = ["Title", "Word count", "Sentence count", "Unique words", "Unique words (stemmed)", "Average word length", "Average sentence length", "Lexical diversity", "Noun%", "Verb%", "Adjective%", "Adverb%", "Pronoun%", "Average sentence tree depth", "Average dependency distance"]
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

# Alternate main module used to get ADD per novel independently (since coreNLP couldn't handle more than one at a time)
def main_avg_dep_dist():
    novel_filename = "1962-01_The_Reivers.txt"
    novel_path = novels_dir + "/" + novel_filename
    title = title_from_filename(novel_filename)
    with open(novel_path) as textfile:
        sentences = sent_tokenize(textfile.read().decode("utf-8"))
        print("Title: {}".format(title))
        novel_ADD = average_dependency_distance(sentences)
        print("Average depepdency distance: {}".format(novel_ADD))
        with open("corenlp-add-out.csv", "a") as output_file:
            writer = csv.writer(output_file)
            writer.writerow([novel_ADD])
            print("Wrote data to csv file")
        return

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

    # If writing to CSV file, opens and writes headers
    if(OUTPUT_CSVFILE):
        write_headers_to_file(output_filename)

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

                if(OUTPUT_CSVFILE):
                    data = basic_metrics_from_text(text, sentences, stemmed_text, stemmed_filtered_text, curr_title)
                    write_data_to_file(data, output_filename)

                if(VERBOSE):
                    print_basic_metrics(text, sentences, stemmed_text, stemmed_filtered_text)
                    # print("Part of speech percentages:")
                    # print_part_of_speech_data(text)
                    print("Sentence complexity metrics:")
                    print_sentence_complexity_data(text, sentences)
                    # print("Most frequent words:")
                    # print_most_frequent_words(freq_dist_by_title[curr_title])
                    # print("Most frequent words (stemmed & filtered):")
                    # print_most_frequent_words(stemmed_filtered_freq_dist_by_title[curr_title])
            print("")
            textfile.close()

if __name__ == "__main__":
    main()
