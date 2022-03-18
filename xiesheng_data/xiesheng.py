import pandas as pd
import itertools
import networkx as nx

def xiesheng_graph():

#Read files    
    xiesheng = pd.read_csv('xiesheng_data.tsv', delimiter = '\t')
    xiesheng_recons = pd.read_csv('xiesheng_reconstructions.tsv', delimiter = '\t')
    xiesheng['NUMCODE'] = xiesheng.KARLGREN.astype(str) + xiesheng.KARLGRENCODE
    xiesheng_codes = dict(zip(xiesheng.CHARACTER, xiesheng.NUMCODE))
    xiesheng_nums = dict(zip(xiesheng.CHARACTER, xiesheng.KARLGREN))
#Join two datasets with Karlgren Xiesheng series and OC Reconstructions    
    recon_chars = xiesheng_recons.HANZI
    recon_karlgren_chars = [char for char in recon_chars if char in xiesheng_codes.keys()]
    trim_xiesheng_recons = xiesheng_recons.loc[xiesheng_recons['HANZI'].isin(recon_karlgren_chars)]
    trim_xiesheng_recons['KarlgrenCode'] = trim_xiesheng_recons.loc[:, 'HANZI'].map(lambda x: xiesheng_codes[x])
    trim_xiesheng_recons['KarlgrenNum'] = trim_xiesheng_recons.loc[:, 'HANZI'].map(lambda x: xiesheng_nums[x])
#Create new column for vowels from Baxter 2014, backing onto Zhengzhang Shangfang 2003   
    trim_xiesheng_recons.sort_values(by = 'KarlgrenNum')
    vowels = trim_xiesheng_recons['Baxter2014'].str[0]
    for i in vowels[vowels == '?'].index:
        zz_vowel = trim_xiesheng_recons.at[i, 'Zhengzhang2003'][0]
        if zz_vowel == 'ɯ':
            zz_vowel = 'ə'
        vowels[i] = zz_vowel    
    character_vowels = dict(zip(trim_xiesheng_recons.HANZI, vowels))
#Match Series Indices to Character Lists    
    series_index = dict()
    nums = trim_xiesheng_recons['KarlgrenNum'].unique()
    character_series = dict(zip(trim_xiesheng_recons.HANZI, trim_xiesheng_recons.KarlgrenNum))
    for char, idx in character_series.items():
        if idx not in series_index.keys():
            series_index[idx] = [char]
        else:
            series_index[idx].append(char)
#Build the Graph
    xs_graph = nx.Graph()
    for k in series_index.keys():
        xs_graph.add_nodes_from(series_index[k])
        xs_graph.add_edges_from(itertools.combinations(series_index[k], 2))
    nx.set_node_attributes(xs_graph, character_vowels, name = 'vowel')
    nx.set_node_attributes(xs_graph, {node: node for node in xs_graph.nodes()}, name = 'character')
    
    return xs_graph

#pass a dict of characters and readings in to final_filter. Returns a list of characters with that final.
def final_filter(readings, final):
    filtered_readings = dict()
    for k, v in readings.items():
        if final in v[-4:]:
            filtered_readings[k] = v
    return filtered_readings.keys()
