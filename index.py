#!/usr/bin/python3
import re
import nltk
import os
import sys
import getopt
import time
from nltk.tokenize import wordpunct_tokenize
from nltk import stem

"""
Problems to fix :
- 'involvement...wheth' as an unique token
"""


MEMORY = 100000 #size ?
PUNCTUATION = [",",".",":","!",";","?","/",")","("]
STEMMER = stem.PorterStemmer()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def printDico(dic,post):
    for key in list(dic.keys()):
        print("> '{}' : \n   > #{} (size: {})".format(key,dic[key],len(post[dic[key]])))
    print("========================\n")


def SPIMIInvert(file,docID):
    dictionary = {} # Format : {"token": postingListID, ..}
    postingList = {} # Format : {postingListID1: { docID1: skipPointer,  docID2: -1 }, postingListID2: ... } -> skipPointer = a docID, -1 = no skippointer
    
    with open(file, 'r') as f:
        i = -1

        for line in f.readlines():
            # == PREPROCESS STUFF ==
            stemmed_tokens_without_punct = []
            i +=1

            #Tokenization
            for word in line.replace("\n","").split(" ") : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                
                #Stemm
                stemmed_token = (STEMMER.stem(word)) # are -> be
                
                #Remove punctuations
                if stemmed_token not in PUNCTUATION and stemmed_token != "":
                    stemmed_token = stemmed_token[:-1] if stemmed_token[-1] in PUNCTUATION else stemmed_token 
                    stemmed_tokens_without_punct.append(stemmed_token)
            
            # finally  -> ["be", "u.s", "big"]

            # == SPIMI INVERT == 
            for token in stemmed_tokens_without_punct:
                if len(dictionary) < MEMORY :
                    #Is the token in the dictionary ?
                    try:
                        postingListID = dictionary[token]
                        
                        #We add the current docID to the posting list if it is not in yet
                        try:
                            postingList[postingListID][docID]
                        except:
                            postingList[postingListID][docID] = -1 
                    except:
                        dictionary[token] = list(dictionary.values())[-1]+1 if len(dictionary.values()) != 0 else 1
                        postingList[dictionary[token]] = {}
                        postingList[dictionary[token]][docID] = -1
        
        printDico(dictionary,postingList)
        

        #sort
        #write



def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    index = 0
    for filename in os.listdir("nltk_data/corpora/reuters/training/"):
        SPIMIInvert(os.path.join("nltk_data/corpora/reuters/training/", filename),filename)
        if index == 1:
            return 0
        index +=1 
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
