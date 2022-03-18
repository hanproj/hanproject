#!/usr/bin/env python
# coding: utf-8

# In[13]:


#This file is mostly superfluous but did create a secondary Wang Li rhyme csv.

from poepy.poepy import Poems
import pandas as pd
import numpy as np
import re

wang = pd.read_csv('rhymes_WL.tsv', delimiter = '\t')
lines = []
for line in wang['LINE'].iteritems():
    line = str(line[1])
    if line != 'nan':
        line = ' + '.join(str(line))
        lines.append(line)
    else:
        lines.append(line)
        
wang["SPLIT_LINE"] = pd.Series(lines)
wang['ALIGNMENT'] = wang['LINE']


# In[14]:


wang.loc[wang['RHYME'].notna() == True,  'RHYME'] = wang['STANZA'].astype(str) + wang['RHYME']
wang['RHYME'] = wang['RHYME'].str.lower()


# In[15]:


unique_rhyme_vals = list(wang['RHYME'].unique())
unique_rhyme_vals.remove(np.nan)
rhyme_idx = enumerate(unique_rhyme_vals)
wang['RHYMEIDS'] = 'n/a'


# In[16]:


wang_nona = wang[wang['LINE'].notnull()]
wang_nona.loc[:, 'LENGTH'] = wang_nona['LINE'].str.len()
wang_nona.loc[:, 'LENGTH'] = wang_nona['LENGTH'].astype(int)


# In[17]:


len_enum = list(wang_nona['LENGTH'].iteritems())


# In[18]:


wang_nona.loc[:, 'RHYMEIDS'] = ['0'*n[1] for n in len_enum]


# In[19]:


wang_nona = wang_nona[wang_nona['RHYME'].notnull()]
character_match = list(zip(wang_nona['LINE'], wang_nona['RHYMEWORD']))


# In[20]:


idx_lst = [c[0].index(c[1])+1 for c in character_match]
unique_rhyme_vals = list(wang['RHYME'].unique())
unique_rhyme_vals.remove(np.nan)
rhyme_idx = enumerate(unique_rhyme_vals)
rhyme_id_dict = {}
for i in rhyme_idx:
    rhyme_id_dict[i[1]] = i[0]+1


# In[21]:


rhyme_enum = wang_nona['RHYME'].apply(lambda x: rhyme_id_dict[x])


# In[22]:


rhyme_list = list(zip(wang_nona['RHYMEIDS'], idx_lst))
rhyme_data = list(zip(rhyme_list, list(rhyme_enum)))
rhyme_ids = []
for rhyme_loc in rhyme_data:
    digits, pos = rhyme_loc[0]
    digits = [n for n in digits]
    _id = str(rhyme_loc[1])
    new_id = digits[:pos-1] + [_id] + digits[pos:]
    rhyme_ids.append(new_id)
rhyme_ids = [' '.join(r) for r in rhyme_ids]
wang_nona['RHYMEIDS'] = rhyme_ids


# In[23]:


wang_nona['ALIGNMENT'] = wang_nona['SPLIT_LINE']


# In[51]:


wang_nona.to_csv('Wang1980.tsv', sep = '\t', header = wang_nona.columns)


# In[40]:


rhymeid_index = dict(zip(wang_nona["ID"], wang_nona['RHYMEIDS']))
wang['RHYMEIDS'] = wang['ID'].apply(lambda x: rhymeid_index[x] if x in rhymeid_index.keys() else np.nan)


# In[45]:


wang = wang.drop(['RHYME_ID'], axis = 1)


# In[56]:


wang['RHYMEIDS'] = wang['RHYMEIDS'].fillna('0')


# In[54]:


wang['LENGTH'] = wang['LINE'].str.len()


# In[49]:


wang.to_csv('Wang1980_Engels.tsv', sep = '\t', header = wang.columns)


# In[ ]:





# In[ ]:




