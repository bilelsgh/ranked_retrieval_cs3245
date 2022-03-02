#!/usr/bin/python3
import filecmp
import re
from nbformat import write
import nltk
import os
import sys
import getopt
import math
import json
from nltk.tokenize import wordpunct_tokenize
from nltk import stem
from string import punctuation
from functions import clean

"""
Problems to fix :
- 'involvement...wheth' as an unique token
- ok ca créer bien plusieurs dico, il faut remove les bons en fonction de l'index maintenant
- outof range error
- ne s'arrete pas au break
"""


MEMORY = 99999999999999999999999999999999999999999999999999999999 #size ?
PUNCTUATION = [",",".",":","!",";","?","/",")","(","\"","'"]
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


def writeDict(idx,_dict,postL):
    offset = 0
    with open("./index/dict/dictionary_{}.txt".format(idx), "w") as f:
        for key,val in _dict.items():
            offset = offset+1 if offset != 0 else offset
            all_docIDS = " ".join(list(postL[str(val)].keys()))
            post_line = "{} {}\n".format(offset,all_docIDS)
            new_line = "{} {} {}\n".format(key,len( postL[str(val)] ),offset)
            f.write(new_line)
            offset += len(post_line)


def writeMergeDict(_dict,postL,idx):
    print("New dict merged : dictionary_{}.txt".format(idx))
    with open("./index/dict/dictionary_{}.txt".format(idx), "w") as f:
        for key,val in _dict.items():
            f.write("{} {} {}\n".format(key.split("/")[0],len( postL[val] ),val))

def writeMergePosting(_post,idx):
    with open("./index/post/posting_{}.txt".format(idx), "w") as f:
        for key,val in _post.items():
            all_postIDS = " ".join(val)
            f.write("{} {}\n".format(key,all_postIDS))

def writePosting(idx,post):
    offset = 0
    with open("./index/post/posting_{}.txt".format(idx), "w") as f:
        for postID,docIDS in post.items():
            offset = offset+1 if offset != 0 else offset
            sorted_docIDS = [int(elt) for elt in list(docIDS.keys())]
            sorted_docIDS.sort()
            sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            all_docIDS = " ".join( sorted_docIDS )
            skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len( sorted_docIDS) ) ) == 0)]
            skip_pointers = " ".join(skip_pointers_list)
            new_line = "{} {} {}\n".format(offset,all_docIDS,skip_pointers)
            offset += len(new_line)
            f.write(new_line)





def merge(dict1, dict2, post1, post2,current_index):
    print(" -> Merge")
    #print("\n -> Dic1 : {}\n -> Dic2 : {}\n -> Post1 : {}\n -> Post2 : {}\n".format(dict1,dict2,post1,post2))
    new_dict = {}
    new_post = {}
    nb_postingList = 1
    nb_merged_dict = current_index
    with open(dict1,"r") as d1:
        with open(dict2,"r") as d2:
            with open(post1,"r") as p1:
                with open(post2) as p2:
                    d1_line = d1.readline()
                    d1_term = d1_line.split(" ")[0]
                    d2_line = d2.readline()
                    d2_term = d2_line.split(" ")[0]
                    p1_line = p1.readline()
                    p2_line = p2.readline()
                    finished = False

                    while(not finished):
                        #if False:
                        if len(new_dict) >= MEMORY:
                            print("NEW DICO")
                            writeMergeDict(new_dict,new_post,nb_merged_dict)
                            writeMergePosting(new_post,nb_merged_dict)
                            new_dict = {}
                            new_post = {}
                            nb_postingList = 1
                            nb_merged_dict += 1

                        #print(" --> {} \n## {}\n".format(d1_term,d2_term))

                        #print("    --> {} ## {}\n".format(d1_term=="",d2_term==""))
                        
                        #print("\n============\nd1_term: {}, d2_term: {}".format(d1_term,d2_term))

                        # The term "d1_term" appears first in the alphabetical order
                        if ( (d1_term < d2_term) and d1_term != "") or (d2_term == ""):
                            # The first term is already on the dictionary, we add the docID to the posting list linked to the term
                            try:
                                new_dict[d1_term] 

                                #Get the docIDS only, without the skip pointers
                                docIDs_without_spointer = []
                                former_elt = -1
                                for elt in  p1_line.split(" ")[1:]:
                                    if int(elt) > former_elt:
                                        break
                                    docIDs_without_spointer.append(elt)

                                new_post[new_dict[d1_term]] += [elt.replace("\n","") for elt in docIDs_without_spointer if elt.replace("\n","") ] 
                                new_post[new_dict[d1_term]] = list(set(new_post[new_dict[d1_term]])) #Remove duplicates

                            # The term is not in the dictionary : we add this term to the dictionary and create a new posting list
                            except KeyError:
                                #Get the docIDS only, without the skip pointers
                                docIDs_without_spointer = []
                                former_elt = -1
                                for elt in  p1_line.split(" ")[1:]:
                                    if int(elt) > former_elt:
                                        break
                                    docIDs_without_spointer.append(elt)

                                new_post[nb_postingList] = [elt.replace("\n","") for elt in docIDs_without_spointer if elt.replace("\n","")  ]
                                new_dict[d1_term] = nb_postingList
                                nb_postingList +=1
                            d1_line = d1.readline()
                            d1_term = d1_line.split(" ")[0]
                            p1_line = p1.readline()

                        # The term "d2_term" appears first in the alphabetical order
                        elif ( (d1_term > d2_term) and d2_term != "") or (d1_term == ""):
                            try:
                                new_dict[d2_term]

                                #Get the docIDS only, without the skip pointers
                                docIDs_without_spointer = []
                                former_elt = -1
                                for elt in  p2_line.split(" ")[1:]:
                                    if int(elt) > former_elt:
                                        break
                                    docIDs_without_spointer.append(elt)

                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in docIDs_without_spointer if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates

                            except KeyError:
                                #Get the docIDS only, without the skip pointers
                                docIDs_without_spointer = []
                                former_elt = -1
                                for elt in  p2_line.split(" ")[1:]:
                                    if int(elt) > former_elt:
                                        break
                                    docIDs_without_spointer.append(elt)


                                new_post[nb_postingList] =  [elt.replace("\n","") for elt in docIDs_without_spointer if elt.replace("\n","") ]
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1
                            d2_line = d2.readline()
                            d2_term = d2_line.split(" ")[0]
                            p2_line = p2.readline()
                        
                        
                        # The two terms are identical
                        else:

                            #Get the docIDS only, without the skip pointers
                            docIDs_without_spointer1 = []
                            former_elt = -1
                            for elt in  p1_line.split(" ")[1:]:
                                if int(elt) > former_elt:
                                    break
                                docIDs_without_spointer1.append(elt)
                            
                            #Get the docIDS only, without the skip pointers
                            docIDs_without_spointer2 = []
                            former_elt = -1
                            for elt in  p2_line.split(" ")[1:]:
                                if int(elt) > former_elt:
                                    break
                                docIDs_without_spointer2.append(elt)


                            try:
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in docIDs_without_spointer2 if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in docIDs_without_spointer1 if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates
                            except KeyError:
                                new_post[nb_postingList] = [elt.replace("\n","") for elt in docIDs_without_spointer2 if elt.replace("\n","") ]
                                new_post[nb_postingList] += ( [elt.replace("\n","") for elt in docIDs_without_spointer1 if elt.replace("\n","")  ] )
                                new_post[nb_postingList] = list(set(new_post[nb_postingList])) #Remove duplicates
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1
                            d2_line = d2.readline()
                            d2_term = d2_line.split(" ")[0]
                            p2_line = p2.readline()
                            d1_line = d1.readline()
                            d1_term = d1_line.split(" ")[0]
                            p1_line = p1.readline()

                        if d1_line == "" and d2_line == "" :
                            finished = True
    
    if len(new_dict) != 0:
        writeMergeDict(new_dict,new_post,nb_merged_dict)
        writeMergePosting(new_post,nb_merged_dict)
        nb_merged_dict += 1

    return nb_merged_dict


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
    dict_doc = [] # at which index do we change of document ?
    # We are going through all the documents
    for docID in os.listdir("nltk_data/corpora/reuters/training/"):
        file = os.path.join("nltk_data/corpora/reuters/training/", docID)
        dict_doc.append(dictionary_written)
        # if index > 0:
        #     break
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
                                postingList[postingListID][docID]
                            except:
                                postingList[postingListID][docID] = -1 
                        except:
                            dictionary[token] = list(dictionary.values())[-1]+1 if len(dictionary.values()) != 0 else 1
                            postingList[dictionary[token]] = {}
                            postingList[dictionary[token]][docID] = -1
                        
                        # No more memory available !
                        #if False:
                        if len(dictionary) >= MEMORY :
                            dictionary = sortDict(dictionary)
                            postingList = sortPosting(postingList,dictionary)

                            # Write onto hardisk
                            writePosting(dictionary_written,postingList)
                            writeDict(dictionary_written,dictionary,postingList)
                            dictionary_written += 1
                            dictionary = {}
                            postingList = {}

    # Write the current dictionary
    if len(dictionary) != 0:
        dictionary = sortDict(dictionary)
        postingList = sortPosting(postingList,dictionary)

        writePosting(dictionary_written,postingList)
        writeDict(dictionary_written,dictionary,postingList)
        dictionary_written += 1
        dictionary = {}
        postingList = {}

    print("end indexing...")
    return dictionary_written



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
clean()

# Build index -> several dict and posting lists
current_index = build_index(input_directory, output_file_dictionary, output_file_postings)

# Merge to end up with one dictionary and one posting list
dict_repo = os.listdir("index/dict/")
post_repo = os.listdir("index/post/")

dic1 = dic2 = post1 = post2 = None
idx = 0
# input("start ?\n")
# while True:
#     if idx > 10 :
#         print("#STOP")
#         break 
#     dic2 = dic1 
#     dic1 = os.path.join("index/dict/", dict_repo[idx] )
#     print("#### {} // {}".format(dic1,dic2))
#     post2 = post1
#     post1 = os.path.join("index/post/", post_repo[idx] )
    
#     if dic1 and dic2 and post1 and post2 :
#         temp = current_index
#         print("About to merge [{}] and [{}]".format(dic1,dic2))
#         current_index = merge(dic1, dic2, post1, post2, current_index)
#         continue_ = input("\n**continue ?**\n")
#         #print("--> {} and {}".format(temp,current_index)) 
#         print("compare: {} and {}".format( "index/dict/dictionary_{}.txt".format(current_index-1),"index/dict/dictionary_{}.txt".format(current_index-3) ))
        
#         #if False:
#         if (len(os.listdir("index/dict/")) > 1) and (current_index-3 > 0):
#         #if len(os.listdir("index/dict/")) > 1:
#             if filecmp.cmp("index/dict/dictionary_{}.txt".format(current_index-1),"index/dict/dictionary_{}.txt".format(current_index-3)) : # !!!!!! check here for a different number of dict
#                 print("STOP")
#                 # os.remove("index/dict/dictionary_{}.txt".format(current_index-1))
#                 # os.remove("index/post/posting_{}.txt".format(current_index-1))

#                 # for index in range(current_index-3):
#                 #     os.remove("index/dict/dictionary_{}.txt".format(index))
#                 #     os.remove("index/post/posting_{}.txt".format(index))
                
#                 break
#     idx += 1
    
#     if idx == len(dict_repo):
#         print("**> updte repo")
#         dic1 = dic2 = post1 = post2 = None
#         idx = 0
#         # for elt in dict_repo:
#         #     os.remove("index/dict/{}".format(elt))
#         dict_repo = os.listdir("index/dict/")
#         post_repo = os.listdir("index/post/")