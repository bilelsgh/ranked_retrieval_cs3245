#!/usr/bin/python3
import filecmp
import re
import nltk
import os
import sys
import getopt
import math
import json
from nltk.tokenize import word_tokenize
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
                print("{} => {}\n=====\n".format(key,val))
            idx +=1


# === Writting functions ===
def writeDict(_dict,postL):
    # Write a dictionary onto harddsik during the "build index" part.
    # :param idx: index in the name of the file
    # :param _dict: dictionary
    # :param postL: posting list
    # :return: void

    offset = 0
    with open("dictionary.txt", "w") as f:
        for key,val in _dict.items():
            sorted_docIDS = [int(elt) for elt in list(postL[str(val)].keys())]
            sorted_docIDS.sort()
            sorted_docIDS_5dig = ["{}{}".format( ("0000"+str(elt))[-5:], ("0000"+str(postL[str(val)][str(elt)]))[-5:] ) for elt in sorted_docIDS]
            all_docIDS = "".join( sorted_docIDS_5dig )
            # sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            # all_docIDS = " ".join( sorted_docIDS )
            # skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len(sorted_docIDS ) ) ) == 0)]
            # skip_pointers = " ".join(skip_pointers_list)

            post_line = "{}\n".format(all_docIDS)
            new_line = "{} {} {}\n".format(key,len( postL[str(val)] ),offset) 
            f.write(new_line)
            offset += len(post_line)+1

def writePosting(post):
    # Write a posting list onto harddisk during the "build index" part.
    # :param idx: index in the name of the file
    # :param post: posting list
    # :return: void

    offset = 0
    with open("postings.txt", "w") as f:
        for postID,docIDS in post.items():
            sorted_posting = sorted(docIDS.items(), key=lambda x: x[1][1], reverse=True)
            sorted_docIDS = [int(elt[0]) for elt in sorted_posting]
            #sorted_docIDS = [int(elt) for elt in list(sorted_posting.keys())]
            #sorted_docIDS.sort()
            #sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            #sorted_docIDS_5dig = ["{}{}".format( ("0000"+str(elt))[-5:], ("0000"+str(docIDS[str(elt)][0]))[-5:] ) for elt in sorted_docIDS] #with term frequency
            sorted_docIDS_5dig = ["{}{}".format( ("0000"+str(elt))[-5:], (str(docIDS[str(elt)][1]))[:5] ) for elt in sorted_docIDS] #with term weights
            #sorted_docIDS_5dig = ["{}|{}".format( (str(elt)), (str(docIDS[str(elt)])) ) for elt in sorted_docIDS]  #with weights
            all_docIDS = " ".join( sorted_docIDS_5dig )
           
            new_line = "{}\n".format(all_docIDS)
            f.write(new_line)
            offset += len(new_line)+1


def writeDocLength(docLength):
    # Write length of all the docID used during the indexing part.
    # :param docLength: dictionary where key=docID and value=length of the document
    # :return: void

    offset = 0
    with open("documents_length.txt", "w") as f:
        for docID,length in docLength.items():
            new_line = "{} {}\n".format(docID,length) 
            f.write(new_line)


# === Index building functions ===

def computeWeights(postingLists, N):
    # Compute idf.tf for each document of all the posting lists
    # :param postingLists: posting lists, format : {postingListID1: {docID1: termFrequency, docID2: ...} ...}
    # :param N: size of the collection
    # :return: posting lists, format : {postingListID1: {docID1: (termFrequency, weight), docID2: ...} ...}

    print("..computing weights : N = {}".format(N))
    for pL_Id,docs in postingLists.items():
        for docID, termFreq in docs.items():
            weight = (1+math.log(int(termFreq)))*math.log(N/len(docs),10)
            postingLists[pL_Id][docID] = (termFreq,weight)
    return postingLists
    

def build_index(in_dir, out_dict, out_postings,path_data):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    #Init
    dictionary = {} # Format : {"token": postingListID, ..}
    postingList = {} # Format : {postingListID1: { docID1: termFrequency,  docID2: termFrequency }, postingListID2: ... } 
    document_length = {} # Format : {docID1: length, ...}

    index = -1
    
    
    # We are going through all the documents
    for docID in os.listdir(path_data):
        file = os.path.join(path_data, docID)
        index +=1
        document_length[docID] = 0

        with open(file, 'r') as f:

            for line in f.readlines():
                document_length[docID] += len(line)

                # == PREPROCESS STUFF ==
                stemmed_tokens_without_punct = []

                #Tokenization
                for word in word_tokenize(line) : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                    
                    #Stemm
                    stemmed_token = (STEMMER.stem(word)) # are -> be
                    
                    #Remove punctuations
                    stemmed_tokens_without_punct += stemmed_token.strip(punctuation).split(" ")
                    
                
                # finally  -> ["be", "u.s", "big"]
 

                # == SPIMI INVERT == 
                for token in stemmed_tokens_without_punct:
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
        postingList = computeWeights(postingList, len(os.listdir(path_data)) )

        writePosting(postingList)
        writeDict(dictionary,postingList)
        writeDocLength(document_length)
        printDico(postingList,3)
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

    