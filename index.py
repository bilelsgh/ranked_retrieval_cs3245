#!/usr/bin/python3
import pandas as pd
import filecmp
from pydoc import doc
import re
import nltk
import os
import sys
import getopt
import math
import json
from nltk.tokenize import word_tokenize
from nltk.util import bigrams
from nltk import stem
from string import punctuation
import math


"""
HOMEWORK 3
"""


STEMMER = stem.PorterStemmer()


# === Useful functions ===
def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def sortDict(_dict):
    keys = list(_dict.keys())
    keys.sort()
    res = {}

    for key in keys:
        res[key] = _dict[key]

    return res

def sortPosting(post,_dict):
    res = {}
    for postKey in list(_dict.values()):
        res[str(postKey)] = post[postKey]

    return res

#temporary function for debug -> remove before submitting
def printDico(dico,_iter):
    print("..print")
    idx = 0
    iter = _iter + 15210
    while idx < iter:
        for key,val in dico.items():
            if idx > 15210:
                if idx > iter:
                    break
                #print("{} => {}\n=====\n".format(key,val))
            idx +=1


# === Writting functions ===
def writeDict(_dict,postL):
    # Write a dictionary onto harddsik during the "build index" part.
    # :param idx: index in the name of the file
    # :param _dict: dictionary
    # :param postL: posting list {postingListID1: {docID1: (termFrequency, weight), docID2: ...} ...}
    # :return: void
    # print(_dict)
    # print(postL)
    offset = 0
    with open("dictionary.txt", "w") as f:
        for key,val in _dict.items():
            sorted_docIDS = [int(elt) for elt in list(postL[str(val)].keys())]
            sorted_docIDS.sort()
#            sorted_docIDS_5dig = ["{}{}".format( ("0000"+str(elt))[-5:], (str(postL[str(val)][(elt)][1]))[:5] ) for elt in sorted_docIDS]
            sorted_docIDS_5dig = ["{} {}".format( ("0000"+str(elt))[:], (str(postL[str(val)][(elt)][1]))[:5] ) for elt in sorted_docIDS] # temporary
            all_docIDS = " ".join( sorted_docIDS_5dig )

            post_line = "{}\n".format(all_docIDS)
            new_line = "{} {} {}\n".format(key,len( postL[str(val)] ),offset) 
            f.write(new_line)
            offset += len(post_line)+1

def writePosting(post):
    # Write a posting list onto harddisk during the "build index" part.
    # :param idx: index in the name of the file
    # :param post: posting list {postingListID1: {docID1: (termFrequency, weight), docID2: ...} ...}
    # :return: void
    offset = 0
    with open("postings.txt", "w") as f:
        for postID,docIDS in post.items():
            sorted_posting = sorted(docIDS.items(), key=lambda x: x[1][1], reverse=True) # sort according to weights *Heur3*
            sorted_docIDS = [int(elt[0]) for elt in sorted_posting]
            #sorted_docIDS = [int(elt) for elt in list(docIDS.keys())]
#            sorted_docIDS_5dig = ["{}{}".format( ("0000"+str(elt))[-5:], (str(docIDS[(elt)][1]))[:5] ) for elt in sorted_docIDS] #with term weights
            sorted_docIDS_5dig = ["{} {}".format( ("0000"+str(elt))[-5:], (str(docIDS[(elt)][1]))[:5] ) for elt in sorted_docIDS] # temporary
            all_docIDS = " ".join( sorted_docIDS_5dig )
           
            new_line = "{}\n".format(all_docIDS)
            f.write(new_line)
            offset += len(new_line)+1


# === Index building functions ===

def computeWeights(postingLists, N):
    # Compute idf.tf for each document of all the posting lists
    # :param postingLists: posting lists, format : {postingListID1: {docID1: termFrequency, docID2: ...} ...}
    # :param N: size of the collection
    # :return: posting lists, format : {postingListID1: {docID1: (termFrequency, weight), docID2: ...} ...}

    documents_length = {}
    print("..computing weights : N = {}".format(N))
    for pL_Id,docs in postingLists.items():
        for docID, termFreq in docs.items():
            weight = (1+math.log(int(termFreq), 10))
            postingLists[pL_Id][docID] = (termFreq,weight)

            # Update document length
            try : 
                documents_length[docID] += weight**2
            except :
                documents_length[docID] = weight**2

    # Export the length for normalization
    with open("documents_length.txt", "w") as f:
        for docID, length in documents_length.items():
            f.write("{} {}\n".format(docID,math.sqrt(length)))

    return postingLists

    

def build_index(in_dir, out_dict, out_postings,path_data):
    # Build index from documents stored in the input directory,
    # then output the dictionary file and postings file
    
    print('indexing...')

    columns_to_index = {"title","content"}
    data = pd.read_csv(path_data).head(1) # Get the data in a dataframe
    data["content"][0] = "salut je suis bilel et je suis a singapour!"
    data["title"][0] = "bilel a singapour"

    #Init
    dictionary = {} # Format : {"token": {title : postingListID, content: postingListID} ..}
    postingList = {} # Format : {postingListID1: { docID1: termFrequency,  docID2: termFrequency }, postingListID2: ... } 

    index = -1
    
    
    # We are going through all the documents
    for _,row in data.head().iterrows():
        docID = row["document_id"]
        index +=1

        for col in columns_to_index :
            line = row[col]

            # == PREPROCESS STUFF ==
            stemmed_tokens_without_punct = []

            #Tokenization
            for word in word_tokenize(line) : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                
                #Stemm
                stemmed_token = (STEMMER.stem(word)) # are -> be
                
                #Remove punctuations
                stemmed_tokens_without_punct += stemmed_token.strip(punctuation).split(" ")
                
            
            # finally  -> ["be", "u.s", "big"]

            bigrams_ = list(bigrams(stemmed_tokens_without_punct)) #get the bigrams


            # == Build dictionary and postings ==
             
            # for bigram in bigrams_: # Uncomment these two lines to use bigrams
            #     token = " ".join(bigram)
            for token in stemmed_tokens_without_punct :

                if token != "":
                    #Is the token in the dictionary ? 
                    try:
                        postingListID = dictionary[token]
                        
                        #We add the current docID to the posting list if it is not in yet
                        try:
                            postingList[postingListID][docID] += 1
                        except:
                            postingList[postingListID][docID] = 1
                    except:
                        dictionary[token] = list(dictionary.values())[-1]+1 if len(dictionary.values()) != 0 else 1
                        postingList[dictionary[token]] = {}
                        postingList[dictionary[token]][docID] = 1
                       

    # Write the current dictionary
    if len(dictionary) != 0:
        dictionary = sortDict(dictionary)
        postingList = sortPosting(postingList,dictionary)
        postingList = computeWeights(postingList, len( data ) )

        writePosting(postingList)
        writeDict(dictionary,postingList)
        #printDico(postingList,3)
        dictionary = {}
        postingList = {}

    print("end indexing...")
    return 1 #change




if __name__ == "__main__":

    # === INPUT PROCESS ===

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



    # === INDEX CONSTRUCTION ===
    try:
        os.remove(output_file_dictionary)
        os.remove(output_file_postings)
        print("Former dictionary and posting list deleted.")
    except FileNotFoundError:
        pass

    # Build index -> several dict and posting lists
    current_index = build_index(input_directory, output_file_dictionary, output_file_postings, input_directory)

    