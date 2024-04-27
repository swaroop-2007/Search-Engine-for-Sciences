from collections import defaultdict
import pysolr
from nltk import wordpunct_tokenize, PorterStemmer
from nltk.corpus import stopwords
from string import punctuation
import regex as re


solr = pysolr.Solr('http://localhost:8983/solr/science_search_engine', always_commit=True)


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

def expandQuery(query, resultSet, originalQuery):
    beta = 0.6
    gamma = 0.2
    queryStems = (tokenize_and_stem(' '.join(query)))
    query_vector = defaultdict(int)
    for stem in set(queryStems):
        query_vector[stem] = queryStems.count(stem)
    for result in resultSet[:20]:
        doc_tokens = (tokenize_and_stem(' '.join(result['text'])))
        for stem in set(doc_tokens):
            query_vector[stem] += (beta * doc_tokens.count(stem))
    for result in resultSet[20:]:
        doc_tokens = (tokenize_and_stem(' '.join(result['text'])))
        for stem in set(doc_tokens):
            query_vector[stem] -= (gamma * doc_tokens.count(stem))
    best = sorted(query_vector.items(), key=lambda item: item[1], reverse=True)[1:6]
    for item in best:
        if item[0] not in queryStems:
            query += ' ' + item[0]

    most_frequent_tokens = {}
    for stem, tokens in non_stemmed_words.items():
        most_frequent_tokens[stem] = max(tokens, key=tokens.get)

    ans = originalQuery 
    for stem in wordpunct_tokenize(query[len(originalQuery):]):
        ans += ' ' + most_frequent_tokens[stem]
    return ans


query = 'camp'
docs = solr.search(f'text:{query}', rows=30)
docs = list(solr.search(f'text:{query}', rows=30))
new_query = expandQuery(query, docs, query)
print(new_query)