from collections import defaultdict
import pysolr
from nltk import wordpunct_tokenize, PorterStemmer
from nltk.corpus import stopwords
from string import punctuation
import regex as re

import nltk
nltk.download('stopwords')

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

def findAssociations(localVocab, queryStems, doc_dict):
    associations = defaultdict(int)
    for stem in localVocab:
        for qStem in queryStems:
            cu = 0
            cv = 0
            for doc_terms in doc_dict.values():
                cs = doc_terms.count(stem)
                cqs = doc_terms.count(qStem)
                cu += cs
                cv += cqs
                associations[(qStem, stem)] += (cs*cqs)
            associations[(qStem, stem)] /= (cu*cu+cv*cv+cu*cv)
    return associations


def expandQueryAC(query, resultSet, orginalQuery):
    tokens = []
    doc_dict = {}
    print(resultSet)
    queryStems = tokenize_and_stem(query)
    for result in resultSet:
        url = ' '.join(result['url'])
        doc_tokens = tokenize_and_stem(' '.join(result['content']))
        doc_dict[url] = doc_tokens
        tokens.extend(doc_tokens)

    localVocab = set(tokens)
    associations = findAssociations(localVocab, queryStems, doc_dict)
    associations = sorted(associations.items(), key=lambda item: item[1], reverse=True)[:10]
    for item in associations:
        if item[0][1] not in queryStems and len(item[0][1]) > 2:
            query += " " + item[0][1]
            queryStems.append(item[0][1])

    #Change the query to include the most frequent token for each stem
    most_frequent_tokens = {}
    for stem, tokens in non_stemmed_words.items():
        most_frequent_tokens[stem] = max(tokens, key=tokens.get)


    ans = orginalQuery 
    for stem in wordpunct_tokenize(query[len(orginalQuery):]):
        ans += ' ' + most_frequent_tokens[stem]
    return ans




