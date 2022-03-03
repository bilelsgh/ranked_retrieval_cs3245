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
from nltk.tokenize import word_tokenize
from nltk import stem
from string import punctuation

"""
Problems to fix :
- 'involvement...wheth' as an unique token
"""


MEMORY = 30000
STEMMER = stem.PorterStemmer()


# === Useful function ===
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


# === Writting functions ===
def writeDict(idx,_dict,postL):
    # Write a dictionary onto harddsik during the "build index" part.
    # :param idx: index in the name of the file
    # :param _dict: dictionary
    # :param postL: posting list
    # :return: void

    offset = 0
    with open("dictionary_{}.txt".format(idx), "w") as f:
        for key,val in _dict.items():
            sorted_docIDS = [int(elt) for elt in list(postL[str(val)].keys())]
            sorted_docIDS.sort()
            sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            all_docIDS = " ".join( sorted_docIDS )


            #all_docIDS = " ".join(list(postL[str(val)].keys()))

            skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len(sorted_docIDS ) ) ) == 0)]
            skip_pointers = " ".join(skip_pointers_list)

            post_line = "{} {}\n".format(all_docIDS,skip_pointers) if len(skip_pointers) != 0 else "{}\n".format(all_docIDS)
            new_line = "{} {} {}\n".format(key,len( postL[str(val)] ),offset) 
            f.write(new_line)
            offset += len(post_line)+1

def writePosting(idx,post):
    # Write a posting list onto harddisk during the "build index" part.
    # :param idx: index in the name of the file
    # :param post: posting list
    # :return: void

    offset = 0
    with open("posting_{}.txt".format(idx), "w") as f:
        for postID,docIDS in post.items():
            sorted_docIDS = [int(elt) for elt in list(docIDS.keys())]
            sorted_docIDS.sort()
            sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            all_docIDS = " ".join( sorted_docIDS )
            skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len( sorted_docIDS) ) ) == 0)]
            skip_pointers = " ".join(skip_pointers_list)
            new_line = "{} {}\n".format(all_docIDS,skip_pointers) if len(skip_pointers) != 0 else "{} \n".format(all_docIDS)
            f.write(new_line)
            offset += len(new_line)+1

def writeMergeDict(_dict,postL,start_offset,file_name):
    # Write a dictionary onto harddisk during the merging part.
    # :param _dict: dictionary
    # :param postL: posting list
    # :param start_offset: position of the read pointer in the dictionary onto the harddisk (= 0 when it is empty)
    # :param file_name: File name of the dictionary
    # :return offset: position of the read pointer after writing in the dictionary

    offset = start_offset
    with open(file_name, "a") as f:
        for key,val in _dict.items():
            sorted_docIDS = [int(elt) for elt in postL[val]]
            sorted_docIDS.sort()
            sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            all_docIDS = " ".join(sorted_docIDS)
            skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len( sorted_docIDS) ) ) == 0)]
            skip_pointers = " ".join(skip_pointers_list)

            post_line = "{} {}\n".format(all_docIDS,skip_pointers) if len(skip_pointers) != 0 else "{}\n".format(all_docIDS)
            new_line = "{} {} {}\n".format(key,len( postL[(val)] ),offset)
            f.write(new_line)
            offset += len(post_line)+1

            #f.write("{} {} {}\n".format(key.split("/")[0],len( postL[val] ),val))
    return offset



def writeMergePosting(_post,start_offset,file_name):
    # Write a posting list onto harddisk during the merging part.
    # :param post: posting list
    # :param start_offset: position of the read pointer in the dictionary onto the harddisk (= 0 when it is empty)
    # :param file_name: File name of the dictionary
    # :return offset: position of the read pointer after writing in the posting file

    offset = start_offset
    with open(file_name, "a") as f:
        for key,val in _post.items():

            sorted_docIDS = [int(elt) for elt in val]
            sorted_docIDS.sort()
            sorted_docIDS = [str(elt) for elt in sorted_docIDS]
            all_postIDS = " ".join(sorted_docIDS)
            skip_pointers_list = [elt for idx,elt in enumerate( sorted_docIDS ) if ( len( sorted_docIDS) > 2 ) and (idx % round( math.sqrt(len( sorted_docIDS) ) ) == 0)]
            skip_pointers = " ".join(skip_pointers_list)
            new_line = "{} {}\n".format(all_postIDS,skip_pointers) if len(skip_pointers) != 0 else "{}\n".format(all_postIDS)
            f.write(new_line)
            offset += len(new_line)+1
    return offset




# === Index building functions ===

def merge(dict1, dict2, post1, post2,file_dict, file_post):
    # Merge two dictionaries and two set of posting lists to endup with one dictionary and one set of posting lists. This method is used because we have a memory limit.
    # :param dict1: A dictionary to merge with..
    # :param dict2: .. another one
    # :param post1: A set of posting lists to merge with ..
    # :param post2: .. another one.
    # :param file_dict: File name of the final dictionary
    # :param file_post: File name of the final set of posting lists
    # :return: void

    new_dict = {}
    new_post = {}
    nb_postingList = 1
    with open(dict1,"r") as d1:
        with open(dict2,"r") as d2:
            with open(post1,"r") as p1:
                with open(post2) as p2:
                    finished = False
                    d1_line = d1.readline()
                    d1_term = d1_line.split(" ")[0]
                    d2_line = d2.readline()
                    d2_term = d2_line.split(" ")[0]
                    
                    # Get the first posting list of the first file
                    p1_line_skP = p1.readline()
                    p1_line_skP = [int(elt) for elt in p1_line_skP.split(" ")[:-1]] 
                    max1 = max(p1_line_skP)
                    p1_line = []
                        #Remove the skip pointers
                    for elt in p1_line_skP :
                        p1_line.append(str(elt))
                        if elt == max1 :
                            break
                    p1_line = " ".join(p1_line)

                    # Get the second posting list of the first file
                    p2_line_skP = p2.readline()
                    p2_line_skP = [int(elt) for elt in p2_line_skP.split(" ")[:-1]]
                    max2 = max(p2_line_skP)
                    p2_line = []
                        #Remove the skip pointers
                    for elt in p2_line_skP :
                        p2_line.append(str(elt))
                        if elt == max2 :
                            break
                    p2_line = " ".join(p2_line)

                    #Offset for dict and posting lists
                    start_offset = 0
                    start_offset1 = 0

                    while(not finished):
                        # Memory exceeded : write onto the harddisk
                        if len(new_dict) >= MEMORY:
                            start_offset1 = writeMergeDict(new_dict,new_post,start_offset1,file_dict)
                            start_offset = writeMergePosting(new_post,start_offset,file_post)
                            new_dict = {}
                            new_post = {}
                            nb_postingList = 1


                        # The term "d1_term" appears first in the alphabetical order
                        if ( (d1_term < d2_term) and d1_term != "") or (d2_term == ""):
                            # The first term is already on the dictionary, we add the docID to the posting list linked to the term
                            try:
                                new_dict[d1_term] 

                                #Get the docIDS only, without the skip pointers
                                docIDs_without_spointer = []
                                former_elt = -1
                                for elt in  p1_line.split(" "):
                                    if int(elt) > former_elt:
                                        break
                                    docIDs_without_spointer.append(elt)

                                new_post[new_dict[d1_term]] += [elt.replace("\n","") for elt in docIDs_without_spointer if elt.replace("\n","") ] 
                                new_post[new_dict[d1_term]] = list(set(new_post[new_dict[d1_term]])) #Remove duplicates

                            # The term is not in the dictionary : we add this term to the dictionary and create a new posting list
                            except KeyError:
                                #Get the docIDS only, without the skip pointers
                                new_post[nb_postingList] = [elt.replace("\n","") for elt in p1_line.split(" ") if elt.replace("\n","")  ]
                                new_dict[d1_term] = nb_postingList
                                nb_postingList +=1

                            # Get the next line of the posting list and the dictionary
                            d1_line = d1.readline()
                            d1_term = d1_line.split(" ")[0]
                            
                            # Get the next posting list
                            p1_line_skP = p1.readline()
                            p1_line_skP = [int(elt) for elt in p1_line_skP.split(" ")[:-1]] 
                            max1 = max(p1_line_skP) if len(p1_line_skP) != 0 else 0 
                            p1_line = []
                                #Remove the skip pointers
                            for elt in p1_line_skP :
                                p1_line.append(str(elt))
                                if elt == max1 :
                                    break
                            p1_line = " ".join(p1_line)

                        # The term "d2_term" appears first in the alphabetical order
                        elif ( (d1_term > d2_term) and d2_term != "") or (d1_term == ""):
                            try:
                                new_dict[d2_term]

                                #Get the docIDS only, without the skip pointers
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p2_line.split(" ") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates

                            except KeyError:
                                #Get the docIDS only, without the skip pointers
                                new_post[nb_postingList] =  [elt.replace("\n","") for elt in p2_line.split(" ") if elt.replace("\n","") ]
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1

                            # Get the next line of the posting list and the dictionary
                            d2_line = d2.readline()
                            d2_term = d2_line.split(" ")[0]
                            
                            # Get the next posting list for this file
                            p2_line_skP = p2.readline()
                            p2_line_skP = [int(elt) for elt in p2_line_skP.split(" ")[:-1]]
                            max2 = max(p2_line_skP) if len(p2_line_skP) != 0 else 0
                            p2_line = []
                                #Remove the skip pointers
                            for elt in p2_line_skP :
                                p2_line.append(str(elt))
                                if elt == max2 :
                                    break
                            p2_line = " ".join(p2_line)
                        
                        
                        # The two terms are identical
                        else:

                            #Get the docIDS only, without the skip pointers
                            try:
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p2_line.split(" ") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] += ( [elt.replace("\n","") for elt in p1_line.split(" ") if elt.replace("\n","") ] ) 
                                new_post[new_dict[d2_term]] = list(set(new_post[new_dict[d2_term]])) #Remove duplicates
                            except KeyError:
                                new_post[nb_postingList] = [elt.replace("\n","") for elt in p2_line.split(" ") if elt.replace("\n","") ]
                                new_post[nb_postingList] += ( [elt.replace("\n","") for elt in p1_line.split(" ") if elt.replace("\n","")  ] )
                                new_post[nb_postingList] = list(set(new_post[nb_postingList])) #Remove duplicates
                                new_dict[d2_term] = nb_postingList
                                nb_postingList +=1

                            # Get the next line of the posting list and the dictionary
                            d2_line = d2.readline()
                            d2_term = d2_line.split(" ")[0]
                            
                            # Get the next posting list for this file
                            p2_line_skP = p2.readline()
                            p2_line_skP = [int(elt) for elt in p2_line_skP.split(" ")[:-1]]
                            max2 = max(p2_line_skP) if len(p2_line_skP) != 0 else 0
                            p2_line = []
                                #Remove the skip pointers
                            for elt in p2_line_skP :
                                p2_line.append(str(elt))
                                if elt == max2 :
                                    break
                            p2_line = " ".join(p2_line)

                            d1_line = d1.readline()
                            d1_term = d1_line.split(" ")[0]
                            
                            # Get the next posting list for this file
                            p1_line_skP = p1.readline()
                            p1_line_skP = [int(elt) for elt in p1_line_skP.split(" ")[:-1]] #put offset
                            max1 = max(p1_line_skP) if len(p1_line_skP) != 0 else 0
                            p1_line = []
                                #Remove the skip pointers
                            for elt in p1_line_skP :
                                p1_line.append(str(elt))
                                if elt == max1 :
                                    break
                            p1_line = " ".join(p1_line)

                        if d1_line == "" and d2_line == "" :
                            finished = True
    
    # The dictionary don't exceed the memory but has to be written in the harddisk
    if len(new_dict) != 0:
        writeMergeDict(new_dict,new_post,start_offset1,file_dict)
        writeMergePosting(new_post,start_offset,file_post)

    # Delete the previous dictionaries and posting lists to keep only the final ones
    os.remove(dict1)
    os.remove(dict2)
    os.remove(post1)
    os.remove(post2)


def build_index(in_dir, out_dict, out_postings,path_data):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    #Init
    dictionary_written = 0
    dictionary = {} # Format : {"token": postingListID, ..}
    postingList = {} # Format : {postingListID1: { docID1: skipPointer,  docID2: -1 }, postingListID2: ... } 

    index = -1
    
    
    # We are going through all the documents
    for docID in os.listdir(path_data):
        file = os.path.join(path_data, docID)
        index +=1

        with open(file, 'r') as f:

            for line in f.readlines():
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

    # Merge to end up with one dictionary and one posting list

    dic1 = dic2 = post1 = post2 = None
    idx = 0
    merge("dictionary_0.txt", "dictionary_1.txt", "posting_0.txt", "posting_1.txt", output_file_dictionary, output_file_postings)