import nltk
import pandas as pd
import numpy as np
import math
import operator
import pprint 
import pickle

from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize, PorterStemmer, WordNetLemmatizer
from pandas import DataFrame
from collections import OrderedDict
from string import punctuation

indexes = {}            # tokens : {tf(overall), df, [list_of_documents]}
document_info = {}      # doc_id : { doc_len, tf, max_tf, unique_token_set}

# STOP WORDS
englist_stopwords = stopwords.words("english")


#  Index token with following info (doc_id, tf, max_tf, unique_lemma, doc_len)
def add_index(token, doc_id, tf, max_tf, unique_lemma, doc_len):
    document_info = (doc_id, tf, max_tf, unique_lemma, doc_len)
    
    if token in indexes:
        term_freq, doc_freq, posting_list = indexes[token]
        
        posting_list.append(document_info)
        doc_freq = doc_freq+1
        term_freq = term_freq + 1
        indexes[token] = (term_freq, doc_freq, posting_list)

    else:
        indexes[token] = (1, 1, [document_info])


# document_info = { doc_len, tf, max_tf, unique }
def add_document_info(doc_id, doc_len,tf, max_tf, unique):
    document_info[doc_id] = (doc_len,tf,max_tf, unique)


# calculat freq of token in document
def freq_calculator(tokens):
    frequency={}
    for token in tokens:
        if token in frequency:
            frequency[token] += 1
        else:
            frequency[token] = 1 

    return frequency

def most_freq_lemma_in_doc(frequency):
    return max(frequency.values())

def read_data(file_name):
    print("Reading data from ", file_name)
    data = pd.read_csv(file_name)
    print("Done reading data from ", file_name)
    return data


def tokenization(data):
    
    rows = data.shape[0]

    for doc_id in range(0, rows):
        tokens = list()
        
        title_tokens = word_tokenize(data["title"][doc_id])
        for token in title_tokens:
            tokens.append(token)

        sentence_list = sent_tokenize(data["text"][doc_id])
        for sentence in sentence_list:
            sentence_tokens = word_tokenize(sentence)
            for token in sentence_tokens:
                tokens.append(token)

        # Remove stopwords, punctuation...
        tokens = [token for token in tokens if token not in englist_stopwords]
        tokens = [token for token in tokens if token not in punctuation]

        # Stemming
        stemmer=PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        
        # Lemmantization
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

        all_lemma_frequency = freq_calculator(tokens) # later used to calculate tf
        max_tf = most_freq_lemma_in_doc(all_lemma_frequency)
        doc_len = len(tokens)
        unique_lemma = set(tokens)
            
        for token in unique_lemma:
            add_index(token, doc_id, all_lemma_frequency[token], max_tf, len(unique_lemma), doc_len)

        add_document_info(doc_id, doc_len, len(all_lemma_frequency), max_tf, len(unique_lemma))

        return indexes, document_info

file_name='docs_v1.csv'
data = read_data(file_name)
tokenization(data)

print("Finised tokenization for file: ",file_name )


with open('pickelFiles/document_info.pickle', 'wb') as f:
    pickle.dump(document_info, f)

with open('pickelFiles/indexes.pickle', 'wb') as f:
    pickle.dump(indexes, f)
