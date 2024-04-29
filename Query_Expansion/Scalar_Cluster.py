from collections import defaultdict
import pysolr
from nltk import wordpunct_tokenize, PorterStemmer
from nltk.corpus import stopwords
from string import punctuation
import regex as re
import numpy as np

non_stemmed_words = defaultdict(lambda: defaultdict(int))

def tokenize_and_stem(text):
    english_stopwords = set(stopwords.words("english"))
    text = text.lower()
    text = re.sub('[^a-z]', ' ', text)
    tokens = wordpunct_tokenize(text)
    tokens = [token for token in tokens if token not in english_stopwords]
    tokens = [token for token in tokens if token not in punctuation]
    stemmer = PorterStemmer()
    stems = [stemmer.stem(token) for token in tokens]
    for token, stem in zip(tokens, stems):
        non_stemmed_words[stem][token] += 1
    return stems

# from indexer.solr_client import search
def findScalars(vocab, queryStems, docs):
    scalars = {}
    documents_terms = []
    doc_dict = {}
    i = 1
    for doc in (docs):
        documents_terms.extend(doc)
        doc_dict[i] = doc
        i += 1
    doc_terms = []
    for term in documents_terms:
        if term not in doc_terms:
            doc_terms.append(term)
    relevant_docs = docs
    # print(doc_terms.count('medal'))
    vector_relevant = []
    for doc in relevant_docs:
        rel_vec = np.zeros(len(doc_terms))
        for term in doc:
            count = doc.count(term)
            rel_vec[doc_terms.index(term)] = count
        vector_relevant.append(rel_vec)

    temp = np.array(vector_relevant)
    temp = temp.transpose()
    correlationMatrix = np.matmul(temp, temp.transpose())
    shape_temp = correlationMatrix.shape

    for i in range(shape_temp[0]):
        for j in range(shape_temp[1]):
            if correlationMatrix[i][j] != 0:
                correlationMatrix[i][j] = correlationMatrix[i][j] / (
                            correlationMatrix[i][j] + correlationMatrix[i][i] + correlationMatrix[j][j])

    for stem in queryStems:
        for word in vocab:
            if stem not in doc_terms:
                s = [0 for _ in range(shape_temp[0])]
                stem_vector = s
            else:
                s = doc_terms.index(stem)
                stem_vector = correlationMatrix[s]
            w = doc_terms.index(word)
            word_vector = correlationMatrix[w]
            val = np.dot(stem_vector, word_vector)
            if val != 0:
                val /= np.linalg.norm(stem_vector)
                val /= np.linalg.norm(word_vector)
            scalars[(stem, word)] = val
    return scalars

def expandQuerySC(query, resultSet, originalQuery):
    tokens = []
    doc_dict = {}
    queryStems = tokenize_and_stem(query)
    for result in resultSet:
        doc_tokens = tokenize_and_stem(' '.join(result['text']))
        doc_dict[' '.join(result['url'])] = doc_tokens
        tokens.extend(doc_tokens)
    localVocab = list(set(tokens))
    scalars = findScalars(sorted(localVocab), queryStems, doc_dict.values())
    scalars = sorted(scalars.items(), key=lambda item : item[1], reverse=True)[:10]
    for item in scalars:
        if item[0][1] not in queryStems and len(item[0][1]) > 2:
            query += ' ' + item[0][1]
            queryStems.append(item[0][1])
    
    most_frequent_tokens = {}
    for stem, tokens in non_stemmed_words.items():
        most_frequent_tokens[stem] = max(tokens, key=tokens.get)

    ans = originalQuery 
    for stem in wordpunct_tokenize(query[len(originalQuery):]):
        ans += ' ' + most_frequent_tokens[stem]
    
    return ans
