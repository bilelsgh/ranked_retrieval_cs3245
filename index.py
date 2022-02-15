#!/usr/bin/python3
import re
import nltk
import os
import sys
import getopt
from nltk.tokenize import wordpunct_tokenize
from nltk import stem

MEMORY = 100 #size ?
PUNCTUATION = [",",".",":","!",";","?","/",")","("]
STEMMER = stem.PorterStemmer()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def SPIMIInvert(file):
    dictionary = {}
    
    with open(file, 'r') as f:
        i = -1
        for line in f.readlines():
            stemmed_tokens_without_punct = []
            i +=1
            print(line)

            #Tokenization
            for word in line.replace("\n","").split(" ") : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                
                #Stemm
                stemmed_token = (STEMMER.stem(word)) # are -> be
                
                #Remove punctuations
                if stemmed_token not in PUNCTUATION and stemmed_token != "":
                    stemmed_token = stemmed_token[:-1] if stemmed_token[-1] in PUNCTUATION else stemmed_token 
                    stemmed_tokens_without_punct.append(stemmed_token)
            
            print(stemmed_tokens_without_punct)
            # finally  -> ["be", "u.s", "big"]

            #Dictionary and posting list
            for token in stemmed_tokens_without_punct:
                pass
        return 0    
            # tokens = wordpunct_tokenize(line)
            # tokens_without_ponct = [token for token in tokens if token not in PUNCTUATION]


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    
    for filename in os.listdir("nltk_data/corpora/reuters/training/"):
        SPIMIInvert(os.path.join("nltk_data/corpora/reuters/training/", filename))
        return 0
input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
