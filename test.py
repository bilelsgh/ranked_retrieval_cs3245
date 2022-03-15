import math


### tf is the number of a particular term
### li is the list of terms that contributes to the distance (considering only query terms here)
def normalize(tf, li):
    if tf == 0:
        return 0
    
    deno = 0
    for i in li:
        deno += math.pow(i, 2)

    deno = math.sqrt(deno)

    return tf / deno

### both parameters are list
def cosscore(queries, documents):
    score = 0
    for query, document in zip(queries, documents):
        score += query * document
    
    return score

### might be updated to a for loop and return for the entire list
def getidf(docfreq, termfreq):
    return math.log10(docfreq/termfreq)

### most terms have 1 / 2 documents only hence using base 2 for now
def getwt(tf):
    return 1 + math.log2(tf)

a = {"a":(1,3),"b":(1,4),"c":(1,2),"d":(1,1)}
sort_orders = sorted(a.items(), key=lambda x: x[1][1], reverse=True)
print(sort_orders)