Ranked retrieval:
We built a language model and a dictionary allowing to perform time and memory efficient queries using TF-IDF method

# index.py

## RUN
    To run the index.py user is required to give 3 inputs : 
    1) The data folder containing the Reuters training data set provided by NLTK using the -i option
    2) The output dictionary file using the -d option
    2) The output posting list file using the -p option

## OVERVIEW
The program create a dictionary and a set of posting lists using the SPIMI Invert algorithm. We create a dummy memory (variable MEMORY at the beginning of the program) to make the use of such an algorithm useful. 
    
Thus, after the creation of our index, we obtain two dictionaries and two sets of posting lists that we have to merge. To do this, we will linearly scan the two dictionaries and the two set of posting lists line by line and create a new dictionary and a new posting list in memory. 
   
When these exceeds MEMORY, we write them to the hard disk and start again with a new dictionary and a new set of posting lists. Such a merge is possible because the dictionaries and the posting lists are sorted in the alphabetical order.

For each posting list, we use skip pointers that are sqrt(L) spaced (L = length of the posting list).

## FORMAT
In this program we use these formats :        
 - dictionary : {"token": postingListID, ..}  
 - posting list : {postingListID1: { docID1: -1,  docID2: -1 }, postingListID2: ... }

For the posting list, the value are dict data structure as it will be faster to know if a docID is in a posting list (instead of using list data structure and the "x in postingList" method that's longer)

    
The output format for a dictionary is :
        
term1 doc_frequency posting_list_ID1        
term2 doc_frequency posting_list_ID2
...

        
The posting list IDs are nothing more than the offset (position of the read/write pointer within the file) for this line. Then, it will be possible to get the docIDS of a posting list without reading the entire posting list by using the seek() function.

The output format for a posting list is :
        
doc_IDS1 skip_pointers1   
doc_IDS2 skip_pointers2        
...

As we use offset as posting list ID, we don't need to write it in the posting list.


# search.py:

To run the search.py, user is required to give 4 inputs. 
1) The dictionary file using the -d option
2) The postings list file using the -p option
3) The query file using the -q option
4) The result/output file using the -o option

The program reads queries from the query file and find the corresponding documentIDs that satisfy the query to be output to the result/output file. 

Since we are assuming that dictionary is compact and sufficiently small to be stored in memory, we first retrieve the dictionary(retrieve_dict) from dictionary.txt and store the information in memory. Since dictionary.txt has the information of the offset to the term's postings list, this will allow us to locate the posting list easily instead of scanning through the file to find the corresponding term's posting list in the postings.txt thus speeding up the retrieval of the documentIDs.

For every line of query, we will first preprocess the query terms(query_processing) in the same way we generate the tokens for our dictionary. Next in order to satisfy the boolean operation order of precedence, we will then convert the infix notation into a postfix notation (generate_postfix_notation). This allows us to remove the brackets and allow us to evaluate the terms in order just by doing a linear scan of the query line(eval_query). For all terms they are stored in the following format, (token/list, True/False) where the True or False corresponds to whether a NOT operation has been applied to the term.

During the evaluation of the query, we will do a linear scan of the postfix notation that we have generated in the previous step. Whenever we encounter an operation we will pop the values that we have visited before and do the corresponding boolean operation on them. 

If we encounter the NOT operation, we will pop the previous value and change the corresponding boolean stored in the term to the inverse of it and add it back to the list.

If we encounter the AND and OR operation, we will pop 2 previously encountered values and evaluate them in either eval_or or eval_and.

In both these functions we will first retrieve the posting lists for both terms(search_document) by using the offset of the term. Next we try to determine the state (whether NOT is applied on the terms), before proceeding with the evaluation.

For OR operation:
case 1 a OR b                       - simple union
case 2 if NOT exist                 - apply demorgans law, run eval_and, apply NOT to the result

For AND operation:
case 1 a AND b                      - linear scan and add docID to new list if a == b
case 2 NOT a AND not b              - apply demorgans law, run eval_or, apply NOT ot the result
case 3 if NOT exist                 - run double loops with the inner list being the NOT term
                                      if outer[i] does not exist in inner list, we append to a new list

Once the evaluation has been completed it will then be written to the output file.

## Architecure

index.py        - This file builds the dictionary and postings list from the reuters dataset.
search.py       - This file helps to evaluate single term queries and outputs the docID that matches the query. (example: a AND b OR c, but not ab AND bc OR cd)
dictionary.txt  - This file contains the sorted Terms, Document Frequency and Offset to find the corresponding posting lists of the terms. 
postings.txt    - This file contains the list of DocID for the individual Terms that we have extracted. Additionally skip pointers are also appended to speed up the search process.
all_docid.txt   - The docID universe so that we are able to evaluate NOT a query



- Link was used to understand, design and subsequently evaluate the postfix notation.
https://isaaccomputerscience.org/concepts/dsa_toc_rpn?examBoard=all&stage=all 

