#!/bin/python
import os
import re

def filter_title(title):
    title = re.sub("\'", "", title)
    return re.sub("\s+", " ", title).strip()

def filter_title_for_index(title):
    title = re.sub("[^a-z]", " ", title.lower())
    return re.sub("\s+", " ", title)

def match_title_idx(title_idx1, title_idx2):
    #how much of title1 matches title2?
    words_1 = re.compile("\s+").split(title_idx1)
    words_2 = re.compile("\s+").split(title_idx2)
    words1_dict = dict()
    for word in words_1:
        words1_dict[word] = 1
    count_match = 0
    total_words = 0
    for word in words_2:
        if len(word) <= 3:
            continue
        if word in words1_dict:     # testing only words greater than length 3
            count_match = count_match + 1
        total_words = total_words + 1
    percent_match = (count_match * 1.0) / (total_words * 1.0)
    return percent_match >= 0.80    # threshold is 80% match

def get_year_from_citation(title):
    pub_year = 0
    years = re.findall("\d{4}", title)
    for year in years:
        if 1980 <= int(year) <= 2016:
            pub_year = year
    return pub_year

def get_node_from_title(nodes, title):
    title_idx = filter_title_for_index(title)
    if len(nodes) == 0:
        nodes[0] = (title_idx, filter_title(title), get_year_from_citation(title))
        return 0
    else:
        # Search for title in the index
        for node_id, node_title_idx in nodes.items():
            if match_title_idx(node_title_idx[0], title_idx):
                return node_id
        nodes[len(nodes)] = (title_idx, filter_title(title), get_year_from_citation(title))
        return len(nodes) - 1

def is_valid_citation(title):
    years = re.findall("\d{4}", title)
    for year in years:
        if 1980 <= int(year) <= 2016:
            return True
    return False

def generate_node_dataset(nodes, citations):
    filename = "dataset-nodes.js"
    f = open(filename, "w")
    f.write("var dataset_nodes = [\n")
    for key,value in nodes.items():
        row = "\t{id: %d, value: %d, color: '%s', title: '%s', info: '%s'},\n" % (key, int(citations.get(key, 0)), get_color(value[2]), value[1], value[1])
        f.write(row)
    f.write("];");
    f.close()
    return

def generate_edges_dataset(edges):
    filename = "dataset-edges.js"
    f = open(filename, "w")
    f.write("var dataset_edges = [\n")
    for edge in edges.keys():
        row = "\t{from: %d, to: %d, arrows: 'to'},\n" % (edge[0], edge[1])
        f.write(row)
    f.write("];");
    f.close()
    return

def main():
    nodes = dict()      # dictionary of (node_id, <node_title_idx, node_title, year_of_pub>)
    citations = dict()
    edges = dict()      # list of (from, to) tuple edges
    source_dir = "references"
    for filename in os.listdir(source_dir):
        if filename.endswith(".txt"):
            filedata = open(source_dir + "/" + filename, 'r').read()
            data = re.compile("\[\d+\]").split(filedata)
            citation_count = re.search(".*Cited by (\d+).*", data[0], re.IGNORECASE).group(1)
            paper_title = re.compile(".*Cited by \d+\s+").split(data[0])[1]
            paper_node_id = get_node_from_title(nodes, paper_title)
            citations[paper_node_id] = citation_count
            for i in range(1,(len(data)-1)):
                if is_valid_citation(data[i]):
                    cited_id = get_node_from_title(nodes, data[i])
                    edges[(cited_id, paper_node_id)] = 1

    generate_node_dataset(nodes, citations)
    generate_edges_dataset(edges)

def get_color(year):
    colors = ["#21618C","#2874A6","#2E86C1","#3498DB","#5DADE2","#85C1E9","#AED6F1","#D6EAF8","#EBF5FB"]
    color_idx = (2016 - int(year)) / 4;  # 9 color groups
    return colors[color_idx]

if __name__ == "__main__":
    main()
