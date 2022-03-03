# with open("postings.txt","r") as f:
#     f.seek(2240454)
#     print(f.readline())

#  #            offset = offset+1 if offset != 0 else offset
from nltk.tokenize import sent_tokenize, word_tokenize
from string import punctuation
from nltk import stem

STEMMER = stem.PorterStemmer()

a = "salut, je suis bilel et j'habite à Lyon !"
print(word_tokenize(a))
stemmed_tokens_without_punct = []

for word in word_tokenize(a):
    stemmed_token = (STEMMER.stem(word)) # are -> be
    
    #Remove punctuations
    stemmed_tokens_without_punct += stemmed_token.strip(punctuation).split(" ")


print(stemmed_tokens_without_punct)

stemmed_tokens_without_punct = []
for word in a.replace("\n","").split(" ") : # "Is U.S. big?" --> ["Is", "U.S.", "big?"] 
                    
    #Stemm
    stemmed_token = (STEMMER.stem(word)) # are -> be
    
    #Remove punctuations
    stemmed_tokens_without_punct += stemmed_token.strip(punctuation).split(" ")

print(stemmed_tokens_without_punct)