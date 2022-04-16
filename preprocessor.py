import re
import sys
import csv
import itertools
# import pandas as pd
from datetime import datetime
import nltk
from nltk.stem import snowball
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from typing import Sequence, Optional, Dict, Callable, Tuple, Any, Iterable, Set

CASE_FOLD = True
STEMMING = True
REMOVE_STOP_WORDS = True
REMOVE_PUNCTUATIONS = True

BOOLEAN_AND = 'AND'

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")

# read csv
def increase_csv_field_size_limit(new_limit: int):
    ## reference: https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
    while True:
        try:
            csv.field_size_limit(new_limit)
            break
        except OverflowError:
            new_limit //= 10

# def ReadChunksOfCSV(file, chunksize=100000):
#     chunks = pd.read_csv('dataset/dataset.csv',chunksize=chunksize)
#     return pd.concat(chunks)

class Preprocessor:
    def __init__(
        self,
        case_fold: bool,
        stemming: bool,
        remove_stop_words: bool,
        remove_punctuations: bool,
    ):
        self.case_fold = case_fold
        self.stemming = stemming
        self.remove_stop_words = remove_stop_words
        self.remove_punctuations = remove_punctuations

        ## newer porter stemmer that is widely considered to be better than the orginal
        self.stemmer = snowball.SnowballStemmer(language="english")

        self.stop_words = set(stopwords.words("english"))

        self.non_punctuations_regex = re.compile("[a-zA-Z0-9]+")
        self.phrases_regex = re.compile("('.*?'|\".*?\"|\S+)")
        self.and_regex = re.compile(f"[\W\s_]({BOOLEAN_AND})[\W\s_]")

    def tokenize(self, corpus: str, no_stemming: bool = False) -> Sequence[str]:
        """
        Extract tokens from a string with the necessary modificiations
        (stemming/case folding/stop words removal/punctuations removal)
        """
        words = (
            self.non_punctuations_regex.findall(corpus)
            if self.remove_punctuations
            else itertools.chain(*map(word_tokenize, sent_tokenize(corpus)))
        )

        if self.case_fold:
            words = map(lambda word: word.casefold(), words)

        if self.remove_stop_words:
            words = filter(lambda word: word not in self.stop_words, words)

        if self.stemming and not no_stemming:
            words = map(lambda word: self.stemmer.stem(word), words)

        return list(words)

    def get_query_type(self, query: str) -> str: 
        """
        Check and reurn the type of queries.
        """
        if 'AND' in query or '\"' in query:
            return 'boolean query'
        else:
            return 'free text query'
            
    def parse_query(self, query_data: str) -> Sequence[str]:
        """
        Parse a query into a list of space-separated tokens with the necessary
        modifications (case folding, stemming etc), preserving phrases in
        quotation marks.
        """
        tokens = [token.strip("\"' ") for token in self.phrases_regex.findall(query_data)]

        query = dict()
        query_type = self.get_query_type(query_data)
        query['type'] = query_type
        query['data'] = [ 
            " ".join(self.tokenize(token)) 
            for token in tokens
            if token != BOOLEAN_AND and self.tokenize(token)
        ]
        return query

    def ConcatenateWords(self, WordsList: Sequence[str]) -> str:
        """
        Concatenate all the words in the list.
        """
        return " ".join(WordsList)

    def QueryListToBooleanQuery(self, query: str) -> Sequence[str]:
        """
        Convert the list of queries to boolean queries.
        """
        QueryList = [token.strip("\"' ") for token in self.phrases_regex.findall(query)]
        phrase_word = list()
        NewQueryList = list()
        for query in QueryList:
            if query == BOOLEAN_AND:
                phrase = self.ConcatenateWords(phrase_word)
                NewQueryList.append(phrase)
                phrase_word = list()
                NewQueryList.append(BOOLEAN_AND)
            else:
                phrase_word.append(query)
        if phrase_word:
            phrase = self.ConcatenateWords(phrase_word)
            NewQueryList.append(phrase)
        return NewQueryList

    def QueryListToFreeText(self, query: str) -> Sequence[str]:
        """
        Convert the list of queries to free text queries.
        """
        QueryList = [token.strip("\"' ") for token in self.phrases_regex.findall(query)]
        return [query for query in QueryList if query != BOOLEAN_AND]
        
    def SplitTriwordToBiword(self, queryDict: Dict) -> Dict:
        """
        Split triwords queries to biwords queries.
        """
        newQueryData = list()
        for words in queryDict['data']:
            splitWords = words.split()
            if len(splitWords) == 3:
                newQueryData.append(splitWords[0] + ' ' + splitWords[1])
                newQueryData.append(splitWords[1] + ' ' + splitWords[2])
            else:
                newQueryData.append(words)
        queryDict['data'] = newQueryData
        return queryDict

    def SplitToUniword(self, queryDict: Dict) -> Dict:
        """
        Split the queries to uniword queries.
        """
        newQueryData = list()
        for words in queryDict['data']:
            splitWords = words.split()
            if len(splitWords) > 1:
                for splitWord in splitWords:
                    newQueryData.append(splitWord)
            else:
                newQueryData.append(words)
        queryDict['data'] = newQueryData
        return queryDict

    def is_boolean_query(self, query: str) -> bool:
        """
        Check if a query is a boolean query.
        """
        return bool(self.and_regex.search(query))

    def tokenize_date_string(self, date_string: str) -> Sequence[str]:
        """
        Extract the date tokens from a date string.
        """
        try:
            date = datetime.fromisoformat(date_string)
            ## only extract year, month and day
            return [str(date.year), str(date.month), str(date.day)]
        except:
            ## manually extract datetime tokens
            tokens = []

            for string in self.tokenize(date_string):
                for substring in self.non_punctuations_regex.findall(string):
                    if not substring:
                        continue

                    try:
                        tokens.append(str(int(substring)))
                    except:
                        tokens.append(substring)

            return tokens

class Query:
    def __init__(
        self,
        case_fold: bool,
        stemming: bool,
        remove_stop_words: bool,
        remove_punctuations: bool,
        query_file: str,
        to_biword: bool = True,
    ):
        self.case_fold = case_fold
        self.stemming = stemming
        self.remove_stop_words = remove_stop_words
        self.remove_punctuations = remove_punctuations
        self.query_file = query_file
        self.to_biword = to_biword

        self.preprocessor = Preprocessor(self.case_fold, self.stemming, self.remove_stop_words, self.remove_punctuations)
        self.queryDict = dict()

    def getQuery(self):
        """
        Get the queries and their relevant documents from the query file.
        """
        with open(self.query_file) as f:
            lines = f.readlines()
            query = lines[0]
            relevant_docs = []
            for line in lines[1:]:
                relevant_docs.append(line.strip("\n"))
        return query, relevant_docs

    def queryProcess(self):
        """
        Process the queries with Preprocessor.
        """
        query, relevant_docs = self.getQuery()
        self.queryDict = self.preprocessor.parse_query(query)
        self.queryDict['relevant_docs'] = relevant_docs
        if self.to_biword:
            self.queryDict = self.preprocessor.SplitTriwordToBiword(self.queryDict)
        else:
            self.queryDict = self.preprocessor.SplitToUniword(self.queryDict)
        return self.queryDict

# def test():
#     increase_csv_field_size_limit(int(sys.maxsize / 1000))

#     in_dir = 'dataset/dataset.csv'
#     QUERYFILE = 'queries/q1.txt'

#     DEVELOPMENT = True

#     DOCUMENT_ID = "document_id"
#     TITLE = "title"
#     CONTENT = "content"
#     DATE_POSTED = "date_posted"
#     COURT = "court"

#     # with open(in_dir, mode="r", encoding="utf-8") as f:
#     #     reader = csv.DictReader(f, restval="")
#     #     i = 0
#     #     for doc in reader:
#     #         ## uncomment to generate corpora
#     #         ## parse_csv_to_corpora(doc)
#     #         if DEVELOPMENT and i == 10:
#     #             break
#     #         # inverted_index.index(doc=doc)
#     #         i += 1
#     #         print('Num docs indexing:', i)
#     #         corpus = ' '.join([doc.get(TITLE), doc.get(CONTENT), doc.get(COURT)])
#     #         corpus_tokens = preprocessor.tokenize(corpus)

#     query = Query(CASE_FOLD, STEMMING, REMOVE_STOP_WORDS, REMOVE_PUNCTUATIONS, QUERYFILE)
#     print(query.queryProcess())

# test()