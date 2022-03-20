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
DIGITS = 5
N = len(os.listdir("nltk_data/corpora/reuters/training")) # Size of the collection
### return max 10 documents
K = 10
    
### populate hashtable for easy retrieval
def retrieve_dict(filepath):
    dictionary = {}
    with open(filepath, "r") as f:
        ### read till eof
        while (line := f.readline()):
            ### term, docFreq, Offset in postingslist
            word, freq, offset = line.split(" ")
            dictionary[word] = (int(freq), int(offset))
    return dictionary

def search_documents(token, dictionary, postings_file):
    documents = [] # Format = [(docID,tf.idf) , ...]

    if token not in dictionary: ### if key does not exist
        return []
    
    with open(postings_file, "r") as f:
        f.seek(dictionary[token][1])
        line = f.readline()
        line = line.strip("\n")
        line = line.split(" ")  # For the moment we consider spaces in the posting lists
        documents = [ ( int(elt[:DIGITS]),float(elt[DIGITS:]) ) for elt in line ]
        
    return documents

### document_vectors = {docId: [q1_score, q2_score, ...], ...}
### documents = [(docId1, score1), ...]
### i represent the i'th element in the array
def update_documentvector(document_vectors, documents, i):
    for el in documents:
        document_vectors[el[0]][i] = el[1]

### document_vectors = {docId: [q1_score, q2_score, ...], ...}
### query_score = [q1_score, q2_score, ...]
def compute_cosscore(document_vectors, query_score):
    cosscore = []
    for docid, doc_score in document_vectors.items():
        score = 0
        for i in range(len(query_score)):
            score += query_score[i] * doc_score[i]

        if score != 0:
            cosscore.append[(docid, score)]
    return cosscore

### cosscore = [(docId, cosscore), ...]
def get_documents(cosscores):
    cosscores.sort(key=lambda i:i[1], reverse=True) ### sort using the cosscore

    ### Get only the best K number of results
    if len(cosscores) > K:
        cosscores = cosscores[:K]

    ### return only the docId
    return [docId[0] for docId in cosscores]

### deprecated (check process_query)
def queryToVector(query,dictionary,N):
    vect = []
    # Compute weights
    for term in query :
        tf_idf = (1 + log(1)) * log(N/dictionary[term][0],10)
        vect.append( tf_idf )

    return [normalize(elt,vect) for elt in vect]

def process_query(query, dictionary):
    tokens = {}
    queries = [] 
    for word in query:
        ### pre-process tokens similar to index
        token = (STEMMER.stem(word)) 
        token = token.strip(punctuation).split(" ")
        ### maintain tf for the token
        if token in tokens:
            tokens[token] += 1
        else:
            tokens[token] = 1
            queries.append(token)  ### get all distinct tokens

    ### compute the tf-idf
    token_wtidf = []
    for i in range(len(queries)):
        token = queries[i]
        ### tf using lg 2 since queries normally are smaller in size
        tf_idf = (1 + log(tokens[token]), 2) * log(N/dictionary[token][0], 10) ### TODO: Check the data structure for dictionary and change accordingly
        token_wtidf.append(tf_idf)

    ### get normalized score for token
    token_score = [normalize(tf, token_wtidf) for tf in token_wtidf] ### TODO: does normalizing use the score itself or tf?
    return queries, token_score
        

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    documents_vects = {} # { docID: document_vector ..}
    dictionary = retrieve_dict(dict_file) # Get the dictionary

    # Get the query 
    with open(queries_file, "r") as file :              
        with open(results_file, "w") as result_file: # for every query we need to write
            while query := file.readline():
                ### compute scores for the query and keep track of the ordering for the queries          
                queries, token_score = process_query(query,dictionary)

                ### brute forcing, ensure all the dictionary is populate
                for key in dictionary.keys():
                    documents_vects[key] = [0 * len(queries)]

                for i in range(len(queries)):
                    documents = search_documents(queries[i],dictionary,postings_file)
                    update_documentvector(documents_vects, documents, i)
                    # TODO: build documents vectors

                cosscores = compute_cosscore(documents_vects,token_score)
                result = get_documents(cosscores)

                result_file.write(' '.join(result))
                result_file.write("\n")

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
