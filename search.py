#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from nltk import stem
from string import punctuation

STEMMER = stem.PorterStemmer()
OPR = ["AND", "OR", "(", ")", "NOT"]
NUM_DOCUMENTS = 140

### populate hashtable for easy retrieval
def retrieve_dict(filepath):
    dictionary = {}
    with open(filepath, "r") as f:
        ### read till eof
        while (line := f.readline()):
            word, freq, offset = line.split(" ")
            dictionary[word] = (int(freq), int(offset))

    return dictionary

### check if token is a keyword or boolean operator
def match_opr(token):
    return token in OPR

def search_documents(token, dictionary, postings_file):
    if isinstance(token, list):
        return token
    ### if it is not the stated object do a search through posting
    with open(postings_file, "r") as f:
        f.seek(dictionary[token][1])
        line = f.readline()
        line = line.strip("\n")
        line = line.split(" ")  ### ignoring skip pointer not implemented yet
        line = list(map(int, line))
        line = list(set(line))  ### removing this later
        line.sort()             ### removing this later
    return line
    
### iterate through posting list instead of intersection fucntion. 
def eval_and(t1, t2, dictionary, postings_file):
    ### convert the token to a list
    t1[0] = search_documents(t1[0], dictionary, postings_file)
    t2[0] = search_documents(t2[0], dictionary, postings_file)

    ### NOT a AND NOT b = NOT(a OR b)
    if t1[1] and t2[1]:
        t1[1] = not t1[1] 
        t2[1] = not t2[2]

        l = eval_or(t1, t2, dictionary, postings_file)
        l[1] = not l[1]
        return l 
    ### a AND b
    elif not t1[1] and not t2[1]:
        i, j = 0, 0
        l = []
        l1, l2 = t1[0], t2[0]
        while i < len(l1) and j < len(l2):
            ### if match move both pointers forward
            if l1[i] == l2[j]:
                l.append(l1[i])
                i += 1
                j += 1
            ### t1[i] is smaller move t1 pointer forward
            elif l1[i] < l2[j]:
                i += 1
            ### t2[j] is smaller move t2 pointer forward
            else:
                j += 1
        return [l, 0]
    ### NOT a AND b / a AND NOT b
    else:
        l = []
        l1, l2 = [], []
        if t1[1]:
            l1, l2 = t1[0], t2[0]
        else:
            l1, l2 = t2[0], t1[0] 
        ### l1 is the NOT items
        for tk2 in l2:
            ### if item does not exist in l1 (the NOT list)
            if tk2 not in l1:
                l.append(tk2)

        return [l, False]

def eval_or(t1, t2, dictionary, postings_file):
    t1[0] = search_documents(t1[0], dictionary, postings_file)
    t2[0] = search_documents(t2[0], dictionary, postings_file)

    ### NOT a OR NOT b = NOT (a AND b)
    ### NOT a OR b = NOT(a AND NOT b)
    ### a OR NOT b = NOT(NOT a AND b)
    if t1[1] or t2[1]:
        t1[1] = not t1[1] 
        t2[1] = not t2[2]
    ### a OR b
    else:
        if len(t1[0]) == NUM_DOCUMENTS:
            return t1
        elif len(t2[0]) == NUM_DOCUMENTS:
            return t2
        i, j = 0, 0
        l = []
        l1, l2 = t1[0], t2[0]
        ### unable to use list(set(a) | set(b)) for sorted set
        ### hence to run in linear time require this linear scan
        while i < len(l1) and j < len(l2):
            ### if match move both pointers forward
            if l1[i] == l2[j]:
                l.append(l1[i])
                i += 1
                j += 1
            ### t1[i] is smaller move t1 pointer forward append to l
            elif l1[i] < l2[j]:
                l.append(l1[i])
                i += 1
            ### t2[j] is smaller move t2 pointer forward append to l
            else:
                l.append(l2[j])
                j += 1
        ### add the remaining items from l1 if there are still items
        while i < len(l1):
            l.append(l1[i])
            i += 1
        ### add the remainint items from l2 if there are still items
        while j < len(l2):
            l.append(l2[j])
            j += 1
        return [l, False]

    l = eval_and(t1, t2, dictionary, postings_file)
    l[1] = not l[1]
    return l

### to evaluate postfix notation format
def eval_query(query, dictionary, postings_file):
    l = []
    for i in range(len(query)):
        if query[i] == "NOT":
            t = l.pop()
            t[1] = not t[1]
            l.append(t)            
        elif query[i] == "AND":
            t2 = l.pop()
            t1 = l.pop()
            l.append(eval_and(t1, t2, dictionary, postings_file))
        elif query[i] == "OR":
            t2 = l.pop()
            t1 = l.pop()
            l.append(eval_or(t1, t2, dictionary, postings_file))
        else: 
            l.append(query[i])

    return l[0]

def query_processing(query):
    # ensure "(" and ")" are not sticked with the query term
    query = query.replace("(", "( ")
    query = query.replace(")", " )")
    query = query.strip("\n")
    query = query.split(" ")

    l = []

    for tk in query:
        if tk == "":
            continue
        if tk in OPR:
            l.append(tk)
            continue

        temp = STEMMER.stem(tk)         # stem the query term
        temp = temp.strip(punctuation)  # remove punctuation from query term
        l.append(temp)
    return l

def generate_postfix_notation(query):
    query = query_processing(query)
    l = []
    opr = []
    for token in query: # is an operand
        if match_opr(token):
            if len(opr) == 0:
                opr.append(token)
            elif token == "OR":
                if opr[-1] != "(":
                    l.append(opr.pop())
                opr.append(token)
            elif token == "AND":
                if opr[-1] == "OR":
                    opr.append(token)
                else:
                    l.append(token)
            elif token == "(":
                opr.append(token)
            elif token == ")":
                while opr[-1] != "(":
                    l.append(opr.pop())
                opr.pop()
                if len(opr) != 0 and opr[-1] == "NOT":
                    l.append(opr.pop())
            else: #token == "NOT"
                opr.append(token)
        else: # is a keywork
            l.append([token, False])
            if len(opr) != 0 and opr[-1] == "NOT":
                l.append(opr.pop())

    while len(opr) != 0:
        l.append(opr.pop())
    print(l)
    return l

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    
    ### retrieve and populate hashtable for easy lookup of posting position
    dictionary = retrieve_dict(dict_file)          
    with open(queries_file, "r") as f1: 
        with open(results_file, "w") as f2:
            ### eval each line of query before the next and write inside results_file              
            while line := f1.readline():
                query = generate_postfix_notation(line)
                result = eval_query(query, dictionary, postings_file)
                if isinstance(result[0], str):
                    result[0] = search_documents(result[0], dictionary, postings_file)
                if result[1]: ### to implement negation of single object
                    pass
                f2.write(' '.join(map(str, result[0])))  
                f2.write("\n")
    

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
