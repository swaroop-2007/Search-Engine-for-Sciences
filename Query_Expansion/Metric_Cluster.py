from collections import defaultdict
import pysolr
from nltk import wordpunct_tokenize, PorterStemmer
from nltk.corpus import stopwords
from string import punctuation
import regex as re


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


def find_indices(list_to_check, item_to_find):
    return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]

def findMostCorrelated(tokens, queryTerms, doc_dict):
    metrics = defaultdict(int)
    for term in set(queryTerms):
        for stem in set(tokens):
            c = 0
            for doc in doc_dict.values():
                term_count = doc.count(term)
                stem_count = doc.count(stem)
                if term_count == 0 or stem_count == 0:
                    continue
                term_list = find_indices(doc, term)
                stem_list = find_indices(doc, stem)
                for idx1 in term_list:
                    for idx2 in stem_list:
                        if idx1 != idx2:
                            c += (1/abs(idx1 - idx2))
            c /= (tokens.count(term) * tokens.count(stem))
            metrics[(term, stem)] = c
    return metrics


def expandQueryMC(query, resultSet, orginalQuery):
    tokens = []
    doc_dict = {}
    queryStems = tokenize_and_stem(query)
    for result in resultSet:
        # Convert the list of URLs to a string
        url = ' '.join(result['url'])
        doc_tokens = tokenize_and_stem(' '.join(result['content']))  # Access 'text' field instead of 'meta_info'
        doc_dict[url] = doc_tokens
        tokens.extend(doc_tokens)

    # localVocab = set(tokens)
    metrics = findMostCorrelated(tokens, queryStems, doc_dict)
    metrics = sorted(metrics.items(), key=lambda item: item[1], reverse=True)[:10]
    for item in metrics:
        if item[0][1] not in queryStems and len(item[0][1]) > 2:
            query += ' ' +item[0][1]
            queryStems.append(item[0][1])
    most_frequent_tokens = {}
    for stem, tokens in non_stemmed_words.items():
        most_frequent_tokens[stem] = max(tokens, key=tokens.get)

    ans = orginalQuery 
    for stem in wordpunct_tokenize(query[len(orginalQuery):]):
        ans += ' ' + most_frequent_tokens[stem]
    return ans
