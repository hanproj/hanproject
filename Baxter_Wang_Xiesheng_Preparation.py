#! C:\Python36\
# -*- encoding: utf-8 -*-

##!/usr/bin/env python
## coding: utf-8

# In[8]:


#This is the primary notebook for generating a network of rhymewords from both Karlgren's Xiesheng series and
#rhymes from Baxter & Sagart 2014. The same workflow can be used to generate a Xiesheng-Wang Li network. 

import pandas as pd
import re
import poepy
from poepy import Poems
import warnings
warnings.filterwarnings('ignore')
BS_rhymes = pd.read_csv('Baxter1992.tsv', delimiter = '\t')
WL_rhymes = pd.read_csv('Wang1980.tsv', delimiter = '\t')


# In[11]:


BS_vowels = pd.read_csv('BaxSag_Vowels.csv', delimiter = '\t')


# In[12]:


BS_vowels = dict(zip(BS_vowels['Unnamed: 0'], BS_vowels['0']))


# In[13]:


pattern = r'[aeiou]'
WL_vowels = []
for x in WL_rhymes.RECONSTRUCTION:
    try:
        #reverse the string to pull the nuclear vowel
        WL_vowels.append(re.search(pattern, x[::-1])[0])
    except:
        
        #if none, write "X"
        WL_vowels.append('X')
WL_rhymes['WL_vowels'] = WL_vowels


# In[14]:


merged_vowels = []
idx = 0
for c in WL_rhymes.RHYMEWORD:
    idx += 1
    try:
        merged_vowels.append(BS_vowels[c])
    except:
        merged_vowels.append(WL_rhymes.loc[idx, 'WL_vowels'])
WL_rhymes['VOWEL'] = merged_vowels


# In[15]:


WL_rhymes.to_csv('BS_WL_merged_rhymes.csv', sep = '\t')


# In[16]:


import networkx as nx
import altair as alt
#nx_altair is one of many visualization libraries for networkx. 
import nx_altair as nxa

#Use the poepy object Poems on a **filepath**
#get_rhyme_network() generates a graph, accessible with the .G method
#args: filepath (str)
def get_rhymes(fname):
    p = Poems(fname)
    p.get_rhyme_network()
    return p.G

#args: filepath (str)
def get_graph(fname):

    data = pd.read_csv(fname, delimiter = '\t')
    character_vowels = dict(zip(data['RHYME_WORD'], data['VOWEL']))
    rhymes = get_rhymes(fname)
    #sets attributes on the nodes, which must be done in a distinct operation. Association is done with a dict.
    #attributes are accessible with the get_node_attributes() call
    nx.set_node_attributes(rhymes, character_vowels, name = 'vowel')
    nx.set_node_attributes(rhymes, {node: node for node in rhymes.nodes()}, name = 'character')
    
    return rhymes

#args: filepath(str), filepath for new graph (str, must end in '.html')
def draw_network(rhyme_network, savename):
#**Must disable max_rows**. The dataset is not large enough to break the visualization with overflow. 
    alt.data_transformers.disable_max_rows()
    graph = nxa.draw_networkx(
    G=rhyme_network,
    pos=nx.spring_layout(rhyme_network),
    node_size=300,
    node_color='vowel',
    cmap='accent',
    node_label = 'character'
)
    #.interactive() enables click-and-drag and zoom on the graph. 
    graph = graph.interactive()
    #.properties() can set the width and height in pixels. 
    graph = graph.properties(height = 1000, width = 1000)
    graph.save(savename)
    return graph


# In[17]:


#An alternative function, that can draw a network directly from a filepath assuming that the csv/tsv is formatted
#according with the standard rhyme docs (e.g., Baxter1992.tsv, Wang1980.tsv). 

#args: filepath(str), filepath for new graph (str, must end in '.html')
def draw_network_from_file(fname, savename):
    
    alt.data_transformers.disable_max_rows()
    data = pd.read_csv(fname, delimiter = '\t')
    character_vowels = dict(zip(data['RHYME_WORD'], data['VOWEL']))
    rhymes = get_rhymes(fname)
    pos = nx.spring_layout(rhymes)
    
    nx.set_node_attributes(rhymes, character_vowels, name = 'vowel')
    nx.set_node_attributes(rhymes, {node: node for node in rhymes.nodes()}, name = 'character')
    
    graph = nxa.draw_networkx(
    G=rhymes,
    pos=pos,
    node_size=300,
    node_color='vowel',
    cmap='accent',
    node_label = 'character'
)
    graph = graph.interactive()
    graph = graph.properties(height = 1000, width = 1000)
    graph.save(savename)
    return graph


# In[19]:


#create a dictionary of Baxter-Sagart reconstructions
BS_readings = pd.read_csv('rhymes_Baxter2014.tsv', delimiter = '\t')
BS_readings = dict(zip(BS_readings.RHYME_WORD, BS_readings.OCBS))


# In[20]:


#This matches Baxter-Sagart rhyme words with Baxter-Sagart vowels, pulled by the previous regex
BS_rhymes['VOWEL'] = BS_rhymes.loc[:, 'RHYME_WORD'].map(lambda x: BS_vowels[x])
subbed_vowels = dict()
#
for char in list(BS_rhymes[BS_rhymes['VOWEL'] == 'X']['RHYME_WORD']):
    try:
        subbed_vowels[char] = zz_vowels[char]
    except:
        subbed_vowels[char] = 'X'
for char in BS_vowels.keys():
    if char in subbed_vowels.keys():
        BS_vowels[char] = subbed_vowels[char]
BS_rhymes.to_csv('BaxSag_Zhengzhang_Shijing.tsv', sep = '\t')


# In[21]:


for k, v in BS_readings.items():
    BS_readings[k] = v.strip()


# In[23]:


#pass a character-reconstruction dictionary into filter_final() to get the final-filtered slice
#args: readings (dict), final (str)
def final_filter(readings, final):
    filtered_readings = dict()
    for k, v in readings.items():
        if final in v[-4:]:
            filtered_readings[k] = v
    return filtered_readings.keys()
#example:
ng_rhymewords = final_filter(BS_readings, 'ŋ')


# In[14]:


ng_BS_rhymes = BS_rhymes[BS_rhymes['RHYME_WORD'].isin(ng_rhymewords)]


# In[15]:


#save the filtered rhymes
ng_BS_rhymes.to_csv('ng_BS_rhymes.tsv', sep = '\t')


# In[5]:


#from xiesheng import xiesheng and call xiesheng_graph() to generate the fully-connected xiesheng graph
import xiesheng
xs_graph = xiesheng.xiesheng_graph()


# In[32]:


ng_bs_graph = get_graph('ng_BS_rhymes.tsv')


# In[45]:


#the disjoint union of xiesheng and rhyme graphs will connect xiesheng nodes to extant Shijing nodes
test_graph = nx.disjoint_union(xs_graph, ng_bs_graph)


# In[44]:


draw_network(test_graph, 'xiesheng_baxter_graph.html')


# In[ ]:




