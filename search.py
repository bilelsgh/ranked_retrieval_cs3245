#!/usr/bin/python3
import re
import os
import nltk
import sys
import getopt
from math import sqrt, log
from nltk import stem
from nltk.tokenize import word_tokenize
from string import punctuation

from functions import normalize

"""
TODO :
    - if a word is not in the dictionary 
"""

STEMMER = stem.PorterStemmer()
DIGITS = 5
PATH = os.listdir("nltk_data/corpora/reuters/training")
N = len(PATH) # Size of the collection
### return max 10 documents
K = 10
WEIGHT_QUERY_THRESHOLD = 0.35


def normalize_docScore(docID, score):
    # Normalize a document's score with the document's length we compute at the indexing time
    # :param docID: (int) document ID
    # :param score: (float) current document's score
    # :return: (float) document's normalized score, -1 if we didn't find the document length 
    with open("documents_length.txt","r") as f:
        while(l:=f.readline()) : 
            if int(l.split(" ")[0]) == docID :
                return score/sqrt(float(l.split(" ")[1]))
    return -1


def retrieve_dict(filepath):
    # Populate hashtable for easy retrieval
    # :param filepath: path of the dictionary file
    # :return: dictionary object -> format : {term1: (termFrequency, offset)...}

    dictionary = {}
    with open(filepath, "r") as f:
        ### read till eof
        while (line := f.readline()):
            ### term, docFreq, Offset in postingslist
            word, freq, offset = line.split(" ")
            dictionary[word] = (int(freq), int(offset))
    return dictionary


def update_documentvector(document_vectors, documents, i):
    # :param document_vectors: Vector representations of all the documents -> format: {docId: [q1_weight, q2_weight, ...], ...} qX_score representing the weight for the X-th term of the query
    # :param documents: Document's score [(docId1, score1), ...]
    # :param i: Represents the i'th element in the array
    for el in documents:
        document_vectors[el[0]][i] = el[1]

def compute_cosscore(document_vectors, query_score):
    # :param document_vectors: Vector representations of all the documents -> format: {docId: [q1_weight, q2_weight, ...], ...}
    # :param query_score: Vector representation of the query -> format : [q1_weight, q2_weight, ...], qX_weight representing the weight for the X-th term of the query

    cosscore = []
    for docid, doc_score in document_vectors.items():
        score = 0
        for i in range(len(query_score)):
            score += query_score[i] * doc_score[i]

        if score != 0:
            cosscore.append((docid, normalize_docScore(docid,score))) # normalization with document length
    return cosscore

### cosscore = [(docId, cosscore), ...]
def get_documents(cosscores):
    cosscores.sort(key=lambda i:i[1], reverse=True) ### sort using the cosscore

    ### Get only the best K number of results
    if len(cosscores) > K:
        cosscores = cosscores[:K]

    ### return only the docId
    return [str(docId[0]) for docId in cosscores]


def search_documents(token, dictionary, postings_file):
    documents = [] # Format = [(docID,tf.idf) , ...]

    if token not in dictionary: ### if key does not exist
        return []
    
    with open(postings_file, "r") as f:
        f.seek(dictionary[token][1])
        line = f.readline()
        line = line.strip("\n")
        line = line.split(" ")  # For the moment we consider spaces in the posting lists
        #documents = [ ( int(elt[:DIGITS]),float(elt[DIGITS:]) ) for elt in line  ]

        # Only consider the documents with high enough weight *Heur3*
        documents = []
        for elt in line:
            docID_weight = ( int(elt[:DIGITS]),float(elt[DIGITS:]) ) # (docID,tf.idf)
            # if ( docID_weight[1] ) > WEIGHT_QUERY_THRESHOLD :
            documents.append(docID_weight)
            # else:
                # break
        
        
    return documents

def process_query(query, dictionary):
    tokens = {}
    queries = [] 
    for word in word_tokenize(query):
        ### pre-process tokens similar to index
        token = (STEMMER.stem(word)) 
        token = token.strip(punctuation).split(" ")

        ### maintain tf for the token
        if token[0] in tokens:
            tokens[token[0]] += 1
        else:
            tokens[token[0]] = 1
            queries.append(token[0])  ### get all distinct tokens

    ### compute the tf-idf
    token_wtidf = []
    for i in range(len(queries)):
        token = queries[i]

        ### tf using lg 2 since queries normally are smaller in size
        tf_idf = (1 + log(tokens[token], 10)) * log(N/dictionary[token][0], 10) ### TODO: Check the data structure for dictionary and change accordingly -> ok with the data structure
        token_wtidf.append(tf_idf)
    
    #return queries, token_wtidf
    
    ### get normalized score for token AND get rid of the terms with low tf_idf *Heur3*
    queries_and_score = [(queries[i],tf) for i,tf in enumerate(token_wtidf) if tf > WEIGHT_QUERY_THRESHOLD]
    queries_and_score.sort(key=lambda i:i[1], reverse=True) # Sort the query by weight *Heur3*
    
    token_score = [elt[1] for elt in queries_and_score] ### TODO: does normalizing use the score itself or tf?
    queries_sorted = [elt[0] for elt in queries_and_score]
    return queries_sorted, token_score
        

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    dictionary = retrieve_dict(dict_file) # Get the dictionary

    # Get the query 
    with open(queries_file, "r") as file :              
        with open(results_file, "w") as result_file: # for every query we need to write
            while query := file.readline():
                documents_vects = {} # { docID: document_vector ..}
                
                ### compute scores for the query and keep track of the ordering for the queries         
                print("Query : '{}'".format(query)) 
                queries, token_score = process_query(query,dictionary)
                print(queries,token_score)

                

                for i,query in enumerate(queries):
                    print("..search documents")
                    documents = search_documents(query,dictionary,postings_file)
                    # Create a vector for the documents if they don't already exist
                    for elt in documents:
                        try:
                            documents_vects[int(elt[0])]
                        except:
                            documents_vects[int(elt[0])] = [0]*len(queries)
                    print("..update documents weights")
                    update_documentvector(documents_vects, documents, i)

                # Normalize documents vectors
                # for docID, weights in documents_vects.items():
                #     all_weights = [elt for elt in weights]
                #     for idx,weight in enumerate(weights):
                #         documents_vects[docID][idx] = normalize(weight,all_weights)

                print("..compute cosscore")
                cosscores = compute_cosscore(documents_vects,token_score)
                print("..get documents")
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
