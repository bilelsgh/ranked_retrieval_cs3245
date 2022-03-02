This is the README file for A0000000X and A0183158Y's submission             // To fill //
Email(s): 
e0926090@u.nus.edu                                                           
e0309953@u.nus.edu
== Python Version ==

Brian is using 3.8.10

I'm (We're) using Python Version <3.7.6 or replace version number> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

index.py:

search.py:

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

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py        - This file builds the dictionary and postings list from the reuters dataset.
search.py       - This file helps to evaluate single term queries and outputs the docID that matches the query. (example: a AND b OR c, but not ab AND bc OR cd)
dictionary.txt  - This file contains the sorted Terms, Document Frequency and Offset to find the corresponding posting lists of the terms. 
postings.txt    - This file contains the list of DocID for the individual Terms that we have extracted. Additionally skip pointers are also appended to speed up the search process.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.
//////////////////////////////////////////////////////////// TO BE FILLED
[x] We, A0000000X and A0183158Y, certify that I/we have followed the CS 3245 Information
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

- Link was used to understand, design and subsequently evaluate the postfix notation.
https://isaaccomputerscience.org/concepts/dsa_toc_rpn?examBoard=all&stage=all 

