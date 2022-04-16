This is the README file for A0248444Y_A0183158Y_A0188693H_A0248812B's submission           
Email(s): 
e0926090@u.nus.edu                                                           
e0309953@u.nus.edu
e0324277@u.nus.edu
e0934074@u.nus.edu

== Python Version ==
A0248444Y is using 3.9.5
A0183158Y_A0188693H_A0248812B is using 3.8.10
 
== General Notes about this assignment ==

# index.py:

## RUN
    To run the index.py user is required to give 3 inputs : 
    1) The data folder containing the Reuters training data set provided by NLTK using the -i option
    2) The output dictionary file using the -d option
    2) The output posting list file using the -p option

## OVERVIEW
    The program create a dictionary and a set of posting lists assuming we have infinite memory (unlike to the previous homework where SPIMI invert algorithm was used). 
   Each token is first preprocessed (stemmatization, remove punctuation etc.) to improve the search and end up lighter dictionary and set of posting lists.
    Thus, after the creation of our index, we obtain one single dictionary and one single set of posting lists.
   In the posting lists, we replace term frequency by weight (= 1+log10(termFrequency)  ) that will be used at the query time to compute the score of each document. We chose not to use idf because with it documents containing only a part of the query terms but in large numbers are considered more relevant than a document containing all the query terms in smaller numbers that is not what we define by relevant results.
All the docIDs are sorted according to their weights, that is needed if we want to use optimization heuristic ( we chose the number 3 ) in the searching part.
Finally, we write all the documents’ length in a separate file (document_lengths.txt). These values will be used at the query time for normalization purposes.

## FORMAT
    In this program we use these formats :
        
        - dictionary : {"token": postingListID, ..}
        
        - posting list : 
- {postingListID1: { docID1: termFrequency,  docID2: termFrequency }, postingListID2: ... } before computing weights
-  {postingListID1: { docID1: (termFrequency,weight),  docID2: (termFrequency,weight) }, postingListID2: ... } after computing weights
    
    The output format for a dictionary is :
        
        term1 doc_frequency posting_list_ID1
        
        term2 doc_frequency posting_list_ID2
        
        ...

        
        The posting list IDs are nothing more than the offset (position of the read/write pointer within the file) for this line. Then, it will be possible to get the docIDS of a posting list without reading the entire posting list by using the seek() function.


    The output format for a posting list is :
        
        <doc_ID1><weight> <doc_ID2><weight> <doc_ID5><weight>
       <doc_ID7><weight> <doc_ID1><weight>  
...

    As we use offset as posting list ID, we don't need to write it in the posting list. Each group <doc_ID1><weight> has a length of 10digits : 5 for the docID and 5 for the length. Then, we can directly access to the different value during the search part and don’t have to perform several split operations. As the greater docID in the reuter dataset is 14818 and 3 decimals is accurate enough for a document weight, it doesn’t affect the efficiency of the search.


	The output for the documents’ length file :
docID1 length 
docID2 length
…
 


# search.py:

To run the search.py, user is required to give 4 inputs. 
1) The dictionary file using the -d option
2) The postings list file using the -p option
3) The query file using the -q option
4) The result/output file using the -o option

The program reads queries from the query file and find the K most relevant documentIDs that satisfy the query to be output to the result/output file. 

Since we are assuming that dictionary is compact and sufficiently small to be stored in memory, we first retrieve the dictionary(retrieve_dict) from dictionary.txt and store the information in memory. Since dictionary.txt has the information of the offset to the term's postings list, this will allow us to locate the posting list easily instead of scanning through the file to find the corresponding term's posting list in the postings.txt thus speeding up the retrieval of the documentIDs.

For every line of query, we will first preprocess the query terms(process_query) in the same way we generate the tokens for our dictionary. After we retrieve the tokens we will then process the wt.idf weights of the query and remove query terms with low wt.idf score(under a certain threshold). Finally we return 2 arrays, the first array contains the query term order and the second array consists of the score for the corresponding query term.

For each term in the queries array, we will use the token and search for documents that consists the document and get their corresponding docID and wt that has been precalculated in the indexing phase. The weight will then be added into the dictionary that maintains the vector score for the different docIDs. Once all the terms have been processed and converted a vector. We then call compute_cosscore to get the dot product between the query score and the doc score before normalizing all the score with their corresponding document length.

Lastly, we call get_documents to sort the documents in decreasing order of relevance before choosing the K most relevant documents that should be output into the output file.

We’ve also implemented the optimization heuristic 3 (seen in lecture) to improve the document searching and the query processing, to use it you just have to set the Boolean HEURISTIC3 to True (at the top of search.py). However, our tests showed that it leads to worse results, and so we don’t use it (HEURISTIC3=False by default).

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py             - This file builds the dictionary and postings list from the reuters dataset.
search.py            - This file helps to evaluate queries and outputs the K most relevant docID that matches the query, in decreasing order of relevance. 
preprocessor.py      - This file aims to preprocess the query file to queries information .
dictionary.txt       - This file contains the sorted Terms, Document Frequency and Offset to find the corresponding posting lists of the terms. 
postings.txt         - This file contains the list of DocID for the individual Terms that we have extracted. Additionally skip pointers are also appended to speed up the search process.
documents_length.txt - This file contains docID and docLength to remove recomputation of docLength everytime we process another query.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.
//////////////////////////////////////////////////////////// TO BE FILLED
[x] We, A0248444Y, A0183158Y, A0188693H, and A0248812B, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==


