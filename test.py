from nltk import stem
from string import punctuation

STEMMER = stem.PorterStemmer()
OPR = ["AND", "OR", "(", ")", "NOT"]
NUM_DOCUMENTS = 100000

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

def search_documents(token):
    ### processed terms will already be a list -> return list directly
    if isinstance(token, list): ### tentatively list object (might change to sets for intersection/union fuction)
        return token
    
    ### if it is not the stated object do a search through posting and dictionary (TBD)
    pass

### iterate through posting list instead of intersection fucntion. 
def eval_and(t1, t2):
    t1 = search_documents(t1)
    t2 = search_documents(t2)

    i, j = 0, 0
    l = []
    while i < len(t1) and j < len(t2):
        ### if match move both pointers forward
        if t1[i] == t2[j]:
            l.append(t1[i])
            i += 1
            j += 1
        ### t1[i] is smaller move t1 pointer forward
        elif t1[i] < t2[j]:
            i += 1
        ### t2[j] is smaller move t2 pointer forward
        else:
            j += 1
    return l

### union function works since it requires scanning through the entire set of both list
def eval_or(t1, t2):
    t1 = search_documents(t1)
    t2 = search_documents(t2)

    if len(t1) == NUM_DOCUMENTS:
        return t1
    elif len(t2) == NUM_DOCUMENTS:
        return t2

    return list(set(t1) | set(t2))

### should have a global with all the document id then we do a set difference (TBD)
def eval_not(t):
    t = search_documents(t)
    pass

### to evaluate postfix notation format
def eval_query(query):
    l = []
    for token in query:
        if token == "NOT":
            t = l.pop()
            l.append(eval_not(t))
        elif token == "AND":
            t2 = l.pop()
            t1 = l.pop()
            l.append(eval_and(t1, t2))
        elif token == "OR":
            t2 = l.pop()
            t1 = l.pop()
            l.append(eval_or(t1, t2))
        else: 
            l.append(token)

    return l[0]

def query_processing(query):
    # ensure "(" and ")" are not sticked with the query term
    query = query.replace("(", "( ")
    query = query.replace(")", " )")
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
                if opr[-1] == "(":
                    opr.append(token)
                else:
                    l.append(token)
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
                if opr[-1] == "NOT":
                    l.append(opr.pop())
            else: #token == "NOT"
                opr.append(token)
        else: # is a keywork
            l.append(token)
            if len(opr) != 0 and opr[-1] == "NOT":
                l.append(opr.pop())

    while len(opr) != 0:
        l.append(opr.pop())

    print(l)
    return l
    

query = "bill OR   ./Gates/ AND NOT NOT (NOT vista OR NOT XP) AND NOT mac"
#query = "bill OR Gates AND (vista OR XP) AND (warren AND buffet)"
query_order = generate_postfix_notation(query)
#eval_query(query_order)
# dictionary = retrieve_dict("./index/dict/dictionary.txt")
