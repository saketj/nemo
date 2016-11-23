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
    return percent_match >= 0.50    # threshold is 50% match

def get_year_from_citation(title):
    pub_year = 0
    years = re.findall("\d{4}", title)
    for year in years:
        if 1980 <= int(year) <= 2016:
            pub_year = year
    return pub_year

def create_node_from_title(nodes, title, category):
    title_idx = filter_title_for_index(title)
    # Search for title in the index
    for node_id, node_title_idx in nodes.items():
        if match_title_idx(node_title_idx['title_idx'], title_idx):
            return node_id
    nodes[len(nodes)] = { 'title_idx': title_idx,
                          'title': filter_title(title),
                          'category': category,
                          'year': get_year_from_citation(title),
                          'indegree': 0,
                          'outdegree': 0 }
    return len(nodes) - 1


def get_node_from_title(nodes, title):
    title_idx = filter_title_for_index(title)
    # Search for title in the index
    for node_id, node_title_idx in nodes.items():
        if match_title_idx(node_title_idx['title_idx'], title_idx):
            return node_id
    return -1

def is_valid_reference(title):
    years = re.findall("\d{4}", title)
    for year in years:
        if 1980 <= int(year) <= 2016:
            return True
    return False

def add_edge(nodes, edges, from_id, to_id):
    if from_id == to_id:
        return
    edges[(from_id, to_id)] = 1
    nodes[from_id]['outdegree'] = nodes[from_id]['outdegree'] + 1           # Update indegree
    nodes[to_id]['indegree'] = nodes[to_id]['indegree'] + 1      # Update outdegree


def generate_node_dataset(nodes):
    # Get citations count first
    citations = dict()
    lines = open("citations.csv", "r").readlines()
    for row in lines:
        row = row.strip()
        citation_count = int(re.compile(",").split(row, 1)[0])
        paper_title = re.compile(",").split(row, 1)[1]
        paper_id = get_node_from_title(nodes, paper_title)
        if (paper_id != -1):
            citations[paper_id] = citation_count

    filename = "dataset-nodes.js"
    f = open(filename, "w")
    f.write("var dataset_nodes = [\n")
    for key,value in nodes.items():
        color = get_color(value['year'], value['category'])
        row = "\t{id: %d, value: %d, color: '%s', title: '%s', info: '%s', category: '%s', indegree: %d, outdegree: %d},\n" \
               % (key, citations.get(key, 0), color, value['title'], value['title'], value['category'], value['indegree'], value['outdegree'])
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
    nodes = dict()      # dictionary of (node_id, <node_title_idx, node_title, year_of_pub, indegree, outdegree>)
    edges = dict()      # list of (from, to) tuple edges
    source_dir = "references"
    for filename in os.listdir(source_dir):
        if filename.endswith(".txt"):
            filedata = open(source_dir + "/" + filename, 'r').read()
            data = re.compile("\[\d+\]").split(filedata)
            category = re.compile("\n").split(data[0])[0]       # first line in the file
            paper_title = re.compile("\n").split(data[0])[1]    # second line in the file
            paper_node_id = create_node_from_title(nodes, paper_title, category)
            for i in range(1,(len(data)-1)):
                if is_valid_reference(data[i]):
                    cited_id = create_node_from_title(nodes, data[i], category)
                    add_edge(nodes, edges, cited_id, paper_node_id)

    generate_node_dataset(nodes)
    generate_edges_dataset(edges)

def get_color(year, category):
    colors = dict()
    colors['DISK'] = ["#FF6F00","#FF8F00","#FFA000","#FFB300","#FFC107","#FFCA28","#FFD54F","#FFE082","#FFECB3"] # amber band
    colors['SSD'] = ["#21618C","#2874A6","#2E86C1","#3498DB","#5DADE2","#85C1E9","#AED6F1","#D6EAF8","#EBF5FB"] # blue band
    colors['CPU'] = ["#B71C1C","#C62828","#D32F2F","#E53935","#F44336","#EF5350","#E57373","#EF9A9A","#FFCDD2"] # red band
    colors['NETWORK'] = ["#4E342E","#5D4037","#6D4C41","#795548","#8D6E63","#A1887F","#BCAAA4","#D7CCC8"] # brown band
    colors['MEMORY'] = ["#1B5E20","#2E7D32","#388E3C","#43A047","#4CAF50","#66BB6A","#81C784","#A5D6A7","#C8E6C9"] # gree band
    color_idx = (2016 - int(year)) / 4;  # 9 color groups
    return colors[category][color_idx]

if __name__ == "__main__":
    main()
