from nltk.corpus import stopwords
import pandas as pd
from pandas import DataFrame
import pprint as pp
from collections import OrderedDict
from nltk import sent_tokenize, word_tokenize, PorterStemmer, WordNetLemmatizer
import numpy as np
import math as m
import operator
import networkx as nx
import matplotlib.pyplot as plt


class Node:
    def __init__(self, link):
        self.link = link
        self.children = []
        self.parents = []
        self.auth = 1.0
        self.hub = 1.0
        self.pagerank = 1.0


def HITS(data):
    graph = nx.DiGraph()
    rows = data.shape[0]
    for i in range(0,rows):
        graph.add_edges_from([(data["SourceLink"][i],data["Link"][i])])
    hubs, authorities = nx.hits(graph, max_iter=10000, tol = 1e-04, normalized=True)
    print("Hub Scores: ", hubs)
    print("Authority Scores: ", authorities)
    return hubs, authorities



def pageRank(data):
    graph = nx.DiGraph()
    rows = data.shape[0]
    for i in range(0,rows):
        graph.add_edges_from([(data["source"][i],data["url"][i])])
    PageRank = nx.pagerank(graph, max_iter=10000, tol = 1e-06)
    print("PageRank Scores: ", PageRank)
    return PageRank



def readData(fileName):

    data = pd.read_csv(fileName)
    print(data.shape)
    return data
