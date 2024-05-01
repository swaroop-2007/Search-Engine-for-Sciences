from flask import Flask, render_template, url_for

from Query_Expansion.Association_Cluster import expandQueryAC as association_main
from Query_Expansion.Metric_Cluster import expandQueryMC as metric_cluster_main
from Query_Expansion.Scalar_Cluster import expandQuerySC as scalar_main

import flask
from flask_cors import CORS
import pysolr
import re
from flask import request, jsonify
import json
# from spellchecker import SpellChecker

# spell = SpellChecker()
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True


# Location of our database, solr 
solr = pysolr.Solr('http://localhost:8983/solr/science', always_commit=True, timeout=10)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/indexer', methods=['GET'])
def get_query():
    query_expansion = ''
    if 'query' in request.args and 'type' in request.args:
        query = str(request.args['query'])
        type =  str(request.args['type'])
        
        print(query, type)
        total_results = 20
        if type == "association_qe" or type == "metric_qe" or type == "scalar_qe":
            total_results = 20

        solr_results = get_results_from_solr(query, total_results)
        api_resp = parse_solr_results(solr_results)
        if type == "page_rank":
            result = api_resp
        elif "clustering" in type:
            result = get_clustering_results(api_resp, type)
        elif type == "hits":
            result = get_hits_results(api_resp)
        elif type == "association_qe":
            # query = spell.correction(query)
            api_resp = ''
            print("HERE ")
            expanded_query = association_main(query, solr_results, query)
            print(expanded_query)
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)
            api_resp = parse_solr_results(solr_res_after_qe)
            api_resp.append(expanded_query)
            print(expanded_query)
            print(api_resp[20])
            result = api_resp
        elif type == "metric_qe":
        # query = spell.correction(query)
            expanded_query = metric_cluster_main(query, solr_results, query)
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)  # Pass expanded_query to Solr
            api_resp = parse_solr_results(solr_res_after_qe)
            api_resp.append(expanded_query)
            result = api_resp
        elif type == "scalar_qe":
        # query = spell.correction(query)
            expanded_query = scalar_main(query, solr_results, query)
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)  # Pass expanded_query to Solr
            api_resp = parse_solr_results(solr_res_after_qe)
            api_resp.append(expanded_query)
            result = api_resp

        return jsonify(result)
    
    else:
        return "Error: No query or type provided"


def get_results_from_solr(query, no_of_results):
    results = solr.search(query, search_handler="/select", **{
        "wt": "json",
        "rows": no_of_results, 
        "df": "content"
    })
    print("in get_results_solr", results)
    return results


def parse_solr_results(solr_results):
    if solr_results.hits == 0:
        print('I am in if part!')
        return jsonify("query out of scope")
    
    else:
        print('I am in else part!')
        api_resp = list()
        rank = 0
        # print(solr_results)
        for result in solr_results:
            rank += 1
            title = ""
            url = ""
            content = ""
            if 'title' in result:
                title = result['title']
            if 'url' in result:
                url = result['url']
            if 'content' in result:
                content = ' '.join(result['content'])
                meta_info = content[:200]
                meta_info = meta_info.replace("\n", " ")
                meta_info = " ".join(re.findall("[a-zA-Z]+", meta_info))
            link_json = {
                "title": title,
                "url": url,
                "meta_info": meta_info,
                "rank": rank
            }
            api_resp.append(link_json)
    return api_resp


# CLUSTERING 
def get_clustering_results(clust_inp, param_type):
    if param_type == "flat_clustering":
        f = open(r'C:\Users\swaro\CS Spring 2024\IR\Final Search Engine\Search-Engine-for-Sciences\\clustering_f.txt')
        lines = f.readlines()
        f.close()
    elif param_type == "singlelink_clustering":
        f = open(r'C:\Users\swaro\CS Spring 2024\IR\Final Search Engine\Search-Engine-for-Sciences\\clustering_hs.txt')
        lines = f.readlines()
        f.close()
    elif param_type =='completelink_clustering':
        f = open(r'C:\Users\swaro\CS Spring 2024\IR\Final Search Engine\Search-Engine-for-Sciences\\clustering_hc.txt')
        lines = f.readlines()
        f.close()

    cluster_map = {}
    for line in lines:
        line_split = line.split(",")
        if line_split[1] == "":
            line_split[1] = "99"
        cluster_map.update({line_split[0]: line_split[1]})

    for curr_resp in clust_inp:
        curr_url = ' '.join(curr_resp["url"])
        curr_cluster = cluster_map.get(curr_url, "99")
        curr_resp.update({"cluster": curr_cluster})
        curr_resp.update({"done": "False"})

    clust_resp = []
    curr_rank = 1
    for curr_resp in clust_inp:
        if curr_resp["done"] == "False":
            curr_cluster = curr_resp["cluster"]
            curr_resp.update({"done": "True"})
            curr_resp.update({"rank": str(curr_rank)})
            curr_rank += 1
            clust_resp.append({"title": curr_resp["title"], "url": curr_resp["url"],
                               "meta_info": curr_resp["meta_info"], "rank": curr_resp["rank"]})
            for remaining_resp in clust_inp:
                if remaining_resp["done"] == "False":
                    if remaining_resp["cluster"] == curr_cluster:
                        remaining_resp.update({"done": "True"})
                        remaining_resp.update({"rank": str(curr_rank)})
                        curr_rank += 1
                        clust_resp.append({"title": remaining_resp["title"], "url": remaining_resp["url"],
                                           "meta_info": remaining_resp["meta_info"], "rank": remaining_resp["rank"]})

    return clust_resp


def get_hits_results(clust_inp):
    authority_score_file = open(r"C:\Users\swaro\CS Spring 2024\IR\Final Search Engine - Copy for clustering\Search-Engine-for-Sciences\hubs_score.txt", 'r').read()
    authority_score_dict = json.loads(authority_score_file)

    clust_inp = sorted(clust_inp, key=lambda x: authority_score_dict.get(' '.join(x['url']), 0.0), reverse=True)
    return clust_inp




if __name__ == "__main__":
    app.run(debug=True)