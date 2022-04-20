#!/usr/bin/python3
from pydoc import doc
import re
import os
import nltk
import sys
import getopt
from math import sqrt, log, pow
from nltk import stem
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from string import punctuation

STEMMER = stem.PorterStemmer()
DIGITS = 5
N = sum(1 for line in open('documents_length.txt'))
print("Size of the collection : {}".format(N))
# Size of the collection
### return max 10 documents
K = 10
WEIGHT_QUERY_THRESHOLD = 0.35 # Used to select the most important query terms
WEIGHT_DOCUMENT_THRESHOLD = 1 # Used in optimization heuristic 3
HEURISTIC3 = False # By default, we don't use optimization heuristic (cf. README)

POS_SET = {
    "J": wordnet.ADJ,
    "N": wordnet.NOUN,
    "R": wordnet.ADV,
    "V": wordnet.VERB,
}
# == Normalization functions ==

def normalize_docScore(docID, score):
    # Normalize a document's score with the document's length we compute at the indexing time
    # :param docID: (int) document ID
    # :param score: (float) current document's score
    # :return: (float) document's normalized score, -1 if we didn't find the document length 
    with open("documents_length.txt","r") as f:
        while(l:=f.readline()) : 
            if int(l.split(" ")[0]) == docID :
                return score/float(l.split(" ")[1])
    return -1

def normalize(tf, li):
    # :param tf: is the number of a particular term
    # :param li: is the list of terms that contributes to the distance (considering only query terms here)
    if tf == 0:
        return 0
    
    deno = 0
    for i in li:
        deno += pow(i, 2)

    deno = sqrt(deno)
    return tf / deno

# =============

def retrieve_dict(filepath):
    # Populate hashtable for easy retrieval
    # :param filepath: (str) path of the dictionary file
    # :return: dictionary object -> format : {term1: (termFrequency, offset)...}

    dictionary = {}
    with open(filepath, "r") as f:
        ### read till eof
        while (line := f.readline()):
            ### term, docFreq, Offset in postingslist
            word, freq, offset = line.split(" ")
            dictionary[word] = (int(freq), int(offset))
    return dictionary

def update_documentvector(document_vectors, documents, token):
    # Update the weights of the document vectors when we get documents for a certain term 
    # :param document_vectors: Vector representations of all the documents -> format: {docId: {tk1: q1_weight, tk2: q2_weight, ...}, ...} qX_score representing the weight for the X-th term of the query
    # :param documents: Document's score [(docId1, score1), ...]
    # :param token: (str) Token we are updating
    for el in documents:
        document_vectors[el[0]][token] = el[1]

def compute_cosscore(document_vectors, query_dict):
    # :param document_vectors: Vector representations of all the documents -> format: {docId: {tk1: q1_weight, tk2: q2_weight, ...}, ...}
    # :param query_dict: Vector representation of the query -> format : {tk1: q1_weight, tk2: q2_weight, ...}, qX_weight representing the weight for the X-th term of the query

    cosscore = []
    for docid, vector_dict in document_vectors.items():
        score = 0
        for token in query_dict:
            score += query_dict[token] * vector_dict[token]

        if score != 0:
            cosscore.append((docid, normalize_docScore(docid,score))) # normalization with document length
    return cosscore

def get_documents(cosscores):
    # Keep the K better documents : those with the best cosscore.
    # :param cosscore: Scores for each documents, format : [(docId, cosscore), ...]
    # :return: K documents with the highest score
    
    cosscores.sort(key=lambda i:i[1], reverse=True) ### sort using the cosscore

    ### Get only the best K number of results
    if len(cosscores) > K:
        cosscores = cosscores[:K]
    print(cosscores)

    ### return only the docId
    return [str(docId[0]) for docId in cosscores]

def search_documents(token, dictionary, postings_file):
    # Get the document that contain a precise token
    # :param token: (str) Token we are processing
    # :param dictionary: Dictionary of the collection, format : {term1: (termFrequency, offset)...}
    # :param postings_file: (str) Path of the postings
    # :return: Set of documents that contain the token, format = [(docID,tf.idf) , ...]

    documents = [] 
    if token not in dictionary: ### if key does not exist
        return []
    
    with open(postings_file, "r") as f:
        f.seek(dictionary[token][1])
        line = f.readline()
        line = line.strip("\n")
        line = line.split(" ")  

        # Only consider the documents with high enough weight *Heur3*
        documents = []
        for elt in line:
            # docID_weight = ( int(elt.split("_")[0]),float(elt.split("_")[1]) ) # (docID,tf.idf)
            docID_weight = ( int(elt[:5]),float(elt[5:]) )
            # Optimization heuristic : we only return document with a high enough weight
            if HEURISTIC3 :
                if ( docID_weight[1] ) > WEIGHT_DOCUMENT_THRESHOLD :
                    documents.append(docID_weight)
                else:
                    break
            else:
                documents.append(docID_weight)
        
    return documents

def eval_AND(tokens,dictionary,posting_file):
    # Get documents that contains every token in tokens
    # :param tokens: Array of unigrams -> ["bank","of","newyork"]
    # :param dictionary: Dictionary of the collection, format : {term1: (termFrequency, offset)...}
    # :param postings_file: (str) Path of the postings
    # :return res: documents that match the AND query


    documents = [] # contains the list of documents that contains each token -> [ [(doc1 that contains tokens[0], score).. ], [(doc1 that contains tokens[1], score)..  ], ... ]
    res = [] # documents that contain all tokens

    # Get the documents lists for each token
    for token in tokens :
        print(token)
        documents.append( search_documents(token,dictionary,posting_file) )

    print(documents)
    pointers = [0]*len(documents)

    while [pointers[i] < len(documents[i]) for i in range(len(documents))] == [True]*len(documents):
        # A match exists if the three terms appear in the same document
        if len(documents) == 2 :
            match = documents[0][pointers[0]][0] == documents[1][pointers[1]][0]
        else:
            match = documents[0][pointers[0]][0] == documents[1][pointers[1]][0] == documents[2][pointers[2]][0]


        if match :
            res.append( documents[0][pointers[0]] )

        # Increment the pointer with the smallest docID
        min_ = min( documents[0][pointers[0]][0],documents[1][pointers[1]][0] ) # The smaller current docID
        min_ = min(min_,documents[2][pointers[2]][0]) if len(documents) == 3 else min_
        
        if documents[0][pointers[0]][0] == min_ :
            pointers[0] += 1
        elif documents[1][pointers[1]][0] == min_ :
            pointers[1] += 1
        else:
            pointers[2] += 1

    return res
        
def get_synonyms(query, dictionary):
    tokens = []
    for token, pos in nltk.pos_tag(query):
        synset = wordnet.synsets(token, pos=POS_SET.get(pos[0] if pos else None))
        
        results = [el.name().split(".")[0] for el in synset]
        results = set(results)
        
        for el in results:
            if el in dictionary and el != token:
                tokens.append(el)
            
    return tokens

def process_query(query, dictionary):
    # Get the query tokens and their scores from a free text query
    # :param query: (str) A free text query
    # :param dictionary: Dictionary of the collection, format : {term1: (termFrequency, offset)...}
    # :return final_query: Query terms we will considere during the search, format [queryterm1, queryterm2 ...]
    # :return token_score: Scores of each of the query term returned

    tokens = {}
    queries = word_tokenize(query)
    queries = [query.strip(punctuation) for query in queries]
    queries.extend(get_synonyms(queries))
    
    for query in queries:
        ### pre-process tokens similar to index
        token = (STEMMER.stem(query)) 

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

        tf_idf = (1 + log(tokens[token], 10)) * log(N/dictionary[token][0], 10) ### TODO: Check the data structure for dictionary and change accordingly -> ok with the data structure
        token_wtidf.append(tf_idf)
    
    
    ### get only the important terms of the query and get rid of those which don't give much information (1)
    queries_and_score = [(queries[i],tf) for i,tf in enumerate(token_wtidf) if tf > WEIGHT_QUERY_THRESHOLD]
    
    ### Optimization heuristic : the query terms are sorted by weights
    if HEURISTIC3:
        queries_and_score.sort(key=lambda i:i[1], reverse=True) 

    return dict(queries_and_score)  

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    dictionary = retrieve_dict(dict_file) # Get the dictionary

    # Get the query 
    with open(queries_file, "r") as file, open(results_file, "w") as output_file:              
        while query := file.readline():
            documents_vects = {} # { docID: document_vector ..}
            
            ### compute scores for the query and keep track of the ordering for the queries         
            print("Query : '{}'".format(query)) 
            query_dict = process_query(query, dictionary)

            for token in query_dict.keys():
                print("..search documents")
                documents = search_documents(token,dictionary,postings_file)

                # Create a vector for the documents if they don't already exist
                for elt in documents:
                    if int(elt[0]) not in query_dict:
                        documents_vects[int(elt[0])] = query_dict.fromkeys(query_dict, 0)
                
                update_documentvector(documents_vects, documents, token) # we got new document(s) for a token, we need to update the vector value

            print("..compute cosscore")
            cosscores = compute_cosscore(documents_vects, query_dict)
            result = get_documents(cosscores)

            # Write the result of the query 
            output_file.write(' '.join(result))
            output_file.write("\n")

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
# dictionary = retrieve_dict(dictionary_file)
# print(eval_AND(["real","madrid","footbal"],dictionary,postings_file))