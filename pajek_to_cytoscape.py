import pandas as pd
import networkx as nx
import json

def p2c_convert(path, network_fname):

    working_network = pd.read_csv(path, delimiter = ' ')
    num_of_nodes = int(working_network.at[working_network.index[0], working_network.columns[-1]])

    nodes = working_network.iloc[1:num_of_nodes+1]
    nodes.columns = ['node', 'weight']

    edges = working_network.iloc[num_of_nodes+3:]
    edges = edges.reset_index()
    edges.columns = ['node1', 'node2', 'weight']

    nodelist = nodes['node']
    edgelist = edges[['node1', 'node2', 'weight']]
    edgelist = edgelist.drop_duplicates()
    character_node_dict = dict(enumerate(nodes['node'], 1))

    for col in 'node1', 'node2':
        edges[col] = edges[col].astype(int)
        edges[col] = edges[col].map(character_node_dict)

    edgelist = list(zip(edges['node1'], edges['node2'], edges['weight']))

    G = nx.Graph()
    G.add_nodes_from(nodelist)
    G.add_weighted_edges_from(edgelist)

    cyto_graph = nx.cytoscape_data(G)
    with open(network_fname+'.json', 'w') as f:
        f.write(json.dumps(cyto_graph))
