#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import altair as alt
import networkx as nx
import nx_altair as nxa
import sinopy
from poepy import Poems
def read_tsv(path):
    return pd.read_csv(path, delimiter = '\t')


# In[2]:


data = read_tsv('BaxSag_Zhengzhang_Shijing.tsv')
char_vowels = dict(zip(data['RHYME_WORD'], data['VOWEL']))


# In[3]:


def get_rhymes(fname):
    p = Poems(fname)
    p.get_rhyme_network()
    return p.G

def draw_cc_network(fname, savename):
    
    alt.data_transformers.disable_max_rows()
    data = pd.read_csv(fname, delimiter = '\t')
    character_vowels = dict(zip(data['RHYME_WORD'], data['VOWEL']))
    character_vowels['慍'] = 'u'
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


# In[4]:


data[data['RHYME_WORD'] == '痻']


# In[5]:


#draw_cc_network('BaxSag_Zhengzhang_Shijing.tsv', 'BaxSag_Zhengzhang.html')


# In[6]:


#draw_cc_network('BaxSag_Zhengzhang_Shijing.tsv', 'BaxSag_Zhengzhang.html')


# In[10]:


list(data[data['VOWEL']=='X']['RHYME_WORD'])


# In[11]:


def lookup_char(df, char):
    return df[df['RHYME_WORD'] == char]


# In[21]:


lookup_char(data, '痻')


# In[26]:


diff_chars = dict()
diff_chars['滺'] = 'i', 'liw'
diff_chars['鷊'] = 'e', 'ngˤek'
diff_chars['椓'] = 'o', 'tˤrok'
diff_chars['穉'] = 'ə', 'dˤrəj-s'
diff_chars['兌'] = 'o', 'lˤot-s'
diff_chars['冾'] = 'o', 'gˤrop'
diff_chars['痻'] = 'ə', 'mrən'


# In[ ]:





# In[ ]:




