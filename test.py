
from urllib.parse import quote_from_bytes


def match_opr(token):
    OPR = ["AND", "OR", "(", ")", "NOT"]
    return token in OPR

def search_documents(token):
    if isinstance(token, list): ### tentatively list object (might change to sets for intersection/union fuction)
        return token
    
    ### if it is not the stated object do a search through posting and dictionary (TBD)
    pass

def eval_and(t1, t2):
    t1 = search_documents(t1)
    t2 = search_documents(t2)

    return list(set(t1) & set(t2))

def eval_or(t1, t2):
    t1 = search_documents(t1)
    t2 = search_documents(t2)

    return list(set(t1) | set(t2))

def eval_not(t):
    t = search_documents(t)
    ### should have a global with all the document id then we do a set difference
    pass

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
    query = query.replace("(", "( ")
    query = query.replace(")", " )")
    query = query.split(" ")
    return query

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

    return l
    

query = "bill OR Gates AND NOT (vista OR XP) AND NOT mac"
#query = "bill OR Gates AND (vista OR XP) AND (warren AND buffet)"
query_order = generate_postfix_notation(query)
print(query_order)
#eval_query(query_order)