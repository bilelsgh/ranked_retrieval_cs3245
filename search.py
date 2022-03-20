#!/usr/bin/python3
import re
import os
import nltk
import sys
import getopt
from math import sqrt, log
from nltk import stem
from string import punctuation

from functions import normalize

STEMMER = stem.PorterStemmer()
OPR = ["AND", "OR", "(", ")", "NOT"]
num_docs = 0 ## not sure of the value
all_docs = []
DIGITS = 5
N = len(os.listdir("nltk_data/corpora/reuters/training")) # Size of the collection

def populate_global():
    global num_docs
    global all_docs
    with open("all_docid.txt", "r") as f:
        all_docs = f.readline().strip(" ").split(" ")
        all_docs = list(map(int, all_docs))   
        all_docs.sort()
    num_docs = len(all_docs)
    all_docs = [all_docs, False]
    
### populate hashtable for easy retrieval
def retrieve_dict(filepath):
    dictionary = {}
    with open(filepath, "r") as f:
        ### read till eof
        while (line := f.readline()):
            word, freq, offset = line.split(" ")
            dictionary[word] = (int(freq), int(offset))
    return dictionary

def search_documentsV2(token, dictionary, postings_file):
    documents = [] # Format = [(docID,tf.idf) , ...]

    if isinstance(token, list):
        return token, []
    ### if it is not the stated object do a search through posting
    if token not in dictionary: ### if key does not exist return empty list
        return [], []
    with open(postings_file, "r") as f:
        f.seek(dictionary[token][1])
        line = f.readline()
        line = line.strip("\n")
        line = line.split(" ")  # For the moment we consider spaces in the posting lists
        documents = [ ( int(elt[:DIGITS]),float(elt[DIGITS:]) ) for elt in line ]
        
    return documents, []

def queryToVector(query,dictionary,N):
    vect = []
    # Compute weights
    for term in query :
        tf_idf = (1 + log(1)) * log(N/dictionary[term][0],10)
        vect.append( tf_idf )

    return [normalize(elt,vect) for elt in vect]

def process_query(query):
    
    tokens = {}
    token_vector = [] 
    for word in query:
        ### pre-process tokens similar to index
        token = (STEMMER.stem(word)) 
        token = token.strip(punctuation).split(" ")
        ### maintain tf for the token
        if token in tokens:
            tokens[token] += 1
        else:
            tokens[token] = 1
            token_vector.append(token)  ### get all distinct tokens

    ### compute the tf-idf
    for i in range(len(token_vector)):
        pass


    


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    documents_vects = {} # { docID: document_vector ..}
    dictionary = retrieve_dict(dict_file) # Get the dictionary

    # Get the query 
    with open(queries_file, "r") as file :              
        with open(results_file, "w") as result_file: # for every query we need to write
            while query := file.readline():          
                query_vect = queryToVector(query,dictionary,N)

                for query_term in query :
                    documents = search_documentsV2(query_term,dictionary,postings_file)
                    # TODO: build documents vectors

                for document_vect in documents_vects: 
                    pass
                    # TODO: Compute score cosscore(document_vect,query_vect)

                result_file.write()
                result_file.write("\n")
    
    # TODO: return the K documents corresponding to the K higher scores




dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
