#!/usr/bin/python3
import re
from nbformat import write
import nltk
import os
import sys
import getopt
import json
from nltk.tokenize import wordpunct_tokenize
from nltk import stem

"""
Problems to fix :
- 'involvement...wheth' as an unique token
"""


MEMORY = 20 #size ?
PUNCTUATION = [",",".",":","!",";","?","/",")","(","\""]
STEMMER = stem.PorterStemmer()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def printDico(dic,post):
    for key in list(dic.keys()):
        print("> '{}' : \n   > #{} (size: {})".format(key,dic[key],len(post[dic[key]])))
    print("========================\n")

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


def writeDict(idx,_dict):
    with open("./index/dict/dictionary_{}.txt".format(idx), "w") as f:
        for key,val in _dict.items():
            f.write("{}:{}\n".format(key,val))

def writeMergeDict(_dict):
    with open("./index/dict/merge/dictionary_{}.txt".format(1), "w") as f:
        for key,val in _dict.items():
            f.write("{}:{}\n".format(key,val))

def writeMergePosting(_post):
    with open("./index/post/merge/posting_{}.txt".format(1), "w") as f:
        for key,val in _post.items():
            all_postIDS = ",".join(val)
            f.write("{}:{}\n".format(key,all_postIDS))

def writePosting(idx,post):
    with open("./index/post/posting_{}.txt".format(idx), "w") as f:
        for postID,docIDS in post.items():
            all_docIDS = ",".join(list(docIDS.keys()))
            f.write("{}:{}\n".format(postID,all_docIDS))


def merge(dict1, dict2, post1, post2):
    new_dict = {}
    new_post = {}
    nb_postingList = 1
    with open(dict1,"r") as d1:
        with open(dict2,"r") as d2:
            with open(post1,"r") as p1:
                with open(post2) as p2:
                    d1_line = d1.readline()
                    d1_term = d1_line.split(":")[0]
                    d2_line = d2.readline()
                    d2_term = d2_line.split(":")[0]
                    p1_line = p1.readline()
                    p2_line = p2.readline()


                    while(len(new_dict) < MEMORY and (d1_line and d2_line) ):
                        #print("\n============\nd1_term: {}, d2_term: {}".format(d1_term,d2_term))

                        # The term "d1_term" appears first in the alphabetical order
                        if d1_term < d2_term :
                            # The first term is already on the dictionary, we add the docID to the posting list linked to the term
                            try:
                                new_dict[d1_term]
                                new_post[new_dict[d1_term]] += [elt.replace("\n","") for elt in p1_line.split(":")[1].split(",") if elt.replace("\n","") ] 
                                new_post[new_dict[d1_term]] = list(set(new_post[new_dict[d1_term]])) #Remove duplicates

                            # The term is not in the dictionary : we add this term to the dictionary and create a new posting list
                            except KeyError:
                                new_post[nb_postingList] = [elt.replace("\n","") for elt in p1_line.split(":")[1].split(",") if elt.replace("\n","")  ]
                                new_dict[d1_term] = nb_postingList
                                nb_postingList +=1
                            d1_line = d1.readline()
                            d1_term = d1_line.split(":")[0]
                            p1_line = p1.readline()

                        # The term "d2_term" appears first in the alphabetical order
                        elif d1_term > d2_term :
                            try:
                                new_dict[d2_term]
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p2_line.split(":")[1].split(",") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates

                            except KeyError:
                                new_post[nb_postingList] =  [elt.replace("\n","") for elt in p2_line.split(":")[1].split(",") if elt.replace("\n","") ]
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1
                            d2_line = d2.readline()
                            d2_term = d2_line.split(":")[0]
                            p2_line = p2.readline()
                        
                        # The two terms are identical
                        else:
                            try:
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p2_line.split(":")[1].split(",") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p1_line.split(":")[1].split(",") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates
                            except KeyError:
                                new_post[nb_postingList] = [elt.replace("\n","") for elt in p2_line.split(":")[1].split(",") if elt.replace("\n","") ]
                                new_post[nb_postingList] += ( [elt.replace("\n","") for elt in p1_line.split(":")[1].split(",") if elt.replace("\n","")  ] )
                                new_post[nb_postingList] = list(set(new_post[nb_postingList])) #Remove duplicates
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1
                            d2_line = d2.readline()
                            d2_term = d2_line.split(":")[0]
                            p2_line = p2.readline()
    
    writeMergeDict(new_dict)
    writeMergePosting(new_post)



def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    #Init
    dictionary_written = 0
    dictionary = {} # Format : {"token": postingListID, ..}
    postingList = {} # Format : {postingListID1: { docID1: skipPointer,  docID2: -1 }, postingListID2: ... } -> skipPointer = a docID, -1 = no skippointer

    index = -1
    
    # 
    # We are going through all the documents
    for docID in os.listdir("nltk_data/corpora/reuters/demo/"):
        file = os.path.join("nltk_data/corpora/reuters/demo/", docID)
        if index > 0:
            break
        index +=1

        with open(file, 'r') as f:

            for line in f.readlines():
                # == PREPROCESS STUFF ==
                stemmed_tokens_without_punct = []

                #Tokenization
                for word in line.replace("\n","").split(" ") : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                    
                    #Stemm
                    stemmed_token = (STEMMER.stem(word)) # are -> be
                    
                    #Remove punctuations
                    if stemmed_token not in PUNCTUATION and stemmed_token != "":
                        stemmed_token = stemmed_token[:-1] if stemmed_token[-1] in PUNCTUATION else stemmed_token 
                        stemmed_token = stemmed_token[1:] if stemmed_token[0] in PUNCTUATION else stemmed_token 
                        stemmed_tokens_without_punct.append(stemmed_token)
                
                # finally  -> ["be", "u.s", "big"]


                # == SPIMI INVERT == 
                for token in stemmed_tokens_without_punct:
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
                    
                    # No more memory available !
                    if len(dictionary) >= MEMORY :
                        
                        dictionary = sortDict(dictionary)
                        postingList = sortPosting(postingList,dictionary)

                        # Write onto hardisk
                        writeDict(dictionary_written,dictionary)
                        writePosting(dictionary_written,postingList)
                        dictionary_written += 1
                        dictionary = {}
                        postingList = {}
        if index > 1:
            break

    # Write the current dictionary
    if len(dictionary) != 0:
        dictionary = sortDict(dictionary)
        postingList = sortPosting(postingList,dictionary)

        writeDict(dictionary_written,dictionary)
        writePosting(dictionary_written,postingList)
        dictionary_written += 1
        dictionary = {}
        postingList = {}



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

# Build index -> several dict and posting lists
build_index(input_directory, output_file_dictionary, output_file_postings)

# Merge to end up with one dictionary and one posting list
dict_repo = os.listdir("index/dict/")
post_repo = os.listdir("index/post/")

dic1 = dic2 = post1 = post2 = None
idx = 0
while len(dict_repo) != 1:
    dic2 = dic1 
    dic1 = os.path.join("index/dict/", dict_repo[idx] )
    post2 = post1
    post1 = os.path.join("index/post/", post_repo[idx] )
    
    if dic1 and dic2 and post1 and post2 :
        merge(dic1, dic2, post1, post2)
        os.remove(dic1)
        os.remove(post1)
    idx += 1
    
    if idx == len(dict_repo):
        dic1 = dic2 = post1 = post2 = None
        idx = 0