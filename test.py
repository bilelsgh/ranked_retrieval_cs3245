import math

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

a = {"postingListID1": {1: 2, 2: 2 }}

print(computeWeights(a,4))