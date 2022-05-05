#! C:\Python36\
# -*- encoding: utf-8 -*-
#
# File: soas_rnetwork_test.py
# Author: Ash Henson
# Purpose:
#   to try and recreate what Johann-Mattis List did in Using Network Models to Analyze
#   Old Chinese Rhyme Data. I was working off the unpublished 2016 version of the paper.
#   So, the code here is exploratory, not designed.
#
# IMPORTANT NOTE:
#  - the get_X_dir() functions are written to work on my machine, so anyone wanting to
#    run this code will have to modify these functions:
#    get_hanproject_dir()
#    get_soas_data_dir()
#    get_mattis_github_data_dir()
#    get_wang1980_data_dir()

import os

from py3_outlier_utils import readlines_of_utf8_file
from poepy import Poems
import networkx as nx
from py3_outlier_utils import append_line_to_utf8_file
import datetime
from test_is_hanzi import is_kana_letter
from py3_middle_chinese import get_mc_data_for_char

#globals
b92_label_dict = {}
b92_shijing_dict = {}
sj_num2name_dict = {}
sj_line2poem_dict = {}

def get_hanproject_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code', 'hanproject')

def get_soas_data_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'data')

def get_mattis_github_data_dir():
    return os.path.join(get_soas_data_dir(), 'mattis-github-data')

def get_wang1980_data_dir():
    return os.path.join(get_mattis_github_data_dir(), 'rhymes-master','datasets', 'Wang1980')

def readin_wang1980_rhyme_data():
    funct_name = 'readin_wang1980_rhyme_data()'
    data_file = os.path.join(get_wang1980_data_dir(), 'rhymes.tsv')
    if not os.path.isfile(data_file):
        print(funct_name + u' ERROR: input file: ' + data_file)
        print('\tDoes NOT exist!')
        return []
    data = readlines_of_utf8_file(data_file)
    return data

def readin_baxter1992_rhyme_data():
    funct_name = 'readin_baxter1992_rhyme_data()'
    data_file = os.path.join(get_soas_data_dir(), 'Baxter1992.tsv')
    if not os.path.isfile(data_file):
        print(funct_name + u' ERROR: input file: ' + data_file)
        print('\tDoes NOT exist!')
        return []
    data = readlines_of_utf8_file(data_file)
    return data
#

def readin_b92_sj_dict():
    funct_name = 'readin_b92_sj_dict()'
    data = readin_baxter1992_rhyme_data()
    global b92_shijing_dict
    if b92_shijing_dict:
        return
    data = data[1:len(data)] # remove labels
    for d in data:
        d = d.split('\t')
        poem_num = int(d[1])
        #id = int(poem_num)
        if poem_num not in b92_shijing_dict:
            b92_shijing_dict[poem_num] = []
        b92_shijing_dict[poem_num].append('\t'.join(d))

# gets data for a given shijing poem, given that poem's number
def get_data_for_shijing_poem_num(poem_num):
    funct_name = 'get_data_for_shijing_poem_num()'
    readin_b92_sj_dict()
    retval = []
    try:
        retval = b92_shijing_dict[poem_num]
    except KeyError as ke:
        retval = []
    return retval

# testcode for get_data_for_shijing_poem_num()
# gets data for a given shijing poem, given that poem's number
def test_get_data_for_shijing_poem_num():
    funct_name = 'test_get_data_for_shijing_poem_num()'
    print('Welcome to ' + funct_name)
    poem_list = [154, 211, 212]
    for pl in poem_list:
        poem_data = get_data_for_shijing_poem_num(pl)
        for pd in poem_data:
            print(pd)

def readin_b92_label_dict():
    funct_name = 'readin_b92_label_dict()'
    global b92_label_dict
    if b92_label_dict:
        return
    data = readin_baxter1992_rhyme_data()
    label_list = data[0]
    label_list = label_list.split('\t')
    for inc in range(0, len(label_list), 1):
        b92_label_dict[inc] = label_list[inc]

def print_baxter1992_rhyme_data_with_labels():
    funct_name = 'print_baxter1992_rhyme_data_with_labels()'
    readin_b92_label_dict()

    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # remove labels
    msg = ''
    for d in data:
        msg = ''
        d = d.split('\t')
        for inc in range(0, len(d), 1):
            msg += b92_label_dict[inc] + ': ' + d[inc] + ', '
        msg = msg[0:len(msg)-2]
        print(msg)

# data:
#   poem number (i.e., ordinal representing its position in the 《詩經》
#   stanza number - stanzas are made up of verses (basically a "paragraph")
#   verse number - a verse is essentially a line of poetry, and can be broken up into sections
#   section number - a section is part of a verse
#   Ex. from (List 2016: 12)
#
#   (1) 南有樛木，葛藟纍之。
#   (2) 樂只君子！福履綏之。
#
#   (3) 南有樛木，葛藟荒之。
#   (4) 樂只君子！福履成之。
#
#   「stanza」 - lines (1) and (2) make up a stanza, as do lines (3) and (4)
#   「verse」 - each of the numbered lines is a verse
#   「section」 line (1) is comprised of two sections, a) 南有樛木， and b) 葛藟纍之。
class b92_shijing_poem:
    def __init__(self):
        x = 1

def test_readin_wang1980_rhyme_data():
    funct_name = 'test_readin_wang1980_rhyme_data()'
    data = readin_wang1980_rhyme_data()
    for d in data:
        d = d.replace('\n','')
        if d.strip():
            print(d)

class wl1980_data_labels:
    def __init__(self):
        self.id = 0
        self.poem_num = 1
        self.poem_name = 2
        self.stanza_num = 3
        self.line_in_source = 4
        self.line = 5
        self.rhyme = 6
        self.rhymeword = 7
        self.gouni = 8
        self.comment = 9
        self.category = 10
        self.problems = 11

# ID	POEM_NUMBER	POEM	STANZA	LINE_ORDER	LINE_IN_SOURCE	LINE	ALIGNMENT	RHYME	RHYME_WORD	RHYMEIDS
class baxter92_data_labels:
    def __init__(self):
        self.id = 0
        self.poem_num = 1
        self.poem_name = 2
        self.stanza_num = 3
        self.line = 5
        self.rhyme = 6
        self.rhymeword = 7

def write_out_wangli_1980_rhyme_data_for_comparison():
    funct_name = 'write_out_wangli_1980_rhyme_data_for_comparison()'
    data = readin_wang1980_rhyme_data()
    labels = data[0]
    data = data[1:len(data)]
    wlindex = wl1980_data_labels()
    poem_num = 1
    print(labels)
    for d in data:
        d = d.replace('\n', '')
        #print(d)
        d = d.split('\t')
        #ID	POEM_NUMBER	POEM_NAME	STANZA	LINE_IN_SOURCE	LINE	RHYME	RHYMEWORD	RECONSTRUCTION	COMMENT	CATEGORY	PROBLEMS
        msg = 'ID = ' + d[wlindex.id] + ', Poem# = ' + d[wlindex.poem_num] + ', Poem Name = ' + d[wlindex.poem_name]
        msg += ', Stanza# = ' + d[wlindex.stanza_num] + ', Rhyme = ' + d[wlindex.rhyme]
        msg += ', Rhymeword = ' + d[wlindex.rhymeword]
        #print(msg)
        msg2 = d[wlindex.poem_name] + '(' + d[wlindex.poem_num] + ') ' + d[wlindex.rhyme] + '(' + d[wlindex.stanza_num]
        msg2 += ') -> ' +  d[wlindex.rhymeword] + '(注：' + d[wlindex.gouni] + ')'
        #print(msg2)
        if d[wlindex.rhymeword].strip():
            msg3 = d[wlindex.rhymeword] + ' (注：' + d[wlindex.gouni] + ') ' + d[wlindex.poem_name] + '(' + d[wlindex.poem_num] + ') ' + d[wlindex.rhyme] + '(' + d[wlindex.stanza_num]
            msg3 += ')'
            print(msg3)
        if 1:
            pn = d[wlindex.poem_num]
            if poem_num != int(pn):
                print('*-'*50)
                poem_num = int(pn)

def readin_shijing_num2name_dict():
    funct_name = 'readin_shijing_num2name_dict()'
    global sj_num2name_dict
    if sj_num2name_dict:
        return
    data = readin_baxter1992_rhyme_data()
    labels = data[0]
    data = data[1:len(data)] # remove labels
    for d in data:
        d = d.split('\t')
        poem_num = d[1]
        poem_name = d[2]
        if poem_num not in sj_num2name_dict:
            sj_num2name_dict[poem_num] = poem_name

def readin_shijing_line2poem_dict():
    funct_name = 'readin_shijing_line2poem_dict()'
    global sj_line2poem_dict
    if sj_line2poem_dict:
        return
    data = readin_baxter1992_rhyme_data()
    labels = data[0]
    data = data[1:len(data)] # remove labels
    for d in data:
        d = d.split('\t')
        k_line = d[6].replace(' + ', '')
        v_poem_num_n_stanza_num = d[8]
        #print('key = ' + line + u': value = ' + poem_num_n_stanza_num)
        if v_poem_num_n_stanza_num.strip():
            if k_line not in sj_line2poem_dict:
                sj_line2poem_dict[k_line] = []
            sj_line2poem_dict[k_line].append(v_poem_num_n_stanza_num)

def test_readin_shijing_line2poem_dict():
    funct_name = 'test_readin_shijing_line2poem_dict()'
    readin_shijing_line2poem_dict()
    for k in sj_line2poem_dict:
        if len(sj_line2poem_dict[k]) > 3:
            print('sj_line2poem_dict[' + k + '] = ')
            print('\t' + '\n\t'.join(sj_line2poem_dict[k]))

def get_poem_name_given_number(poem_num):
    funct_name = 'get_poem_name_given_number()'
    readin_shijing_num2name_dict()
    retval = ''
    try:
        retval = sj_num2name_dict[poem_num]
    except KeyError as ke:
        retval = ''
    return retval

def test_get_poem_name_given_number():
    funct_name = 'test_get_poem_name_given_number()'
    print('Welome to ' + funct_name)
    for inc in range(1, 305+1, 1):
        name = get_poem_name_given_number(str(inc))
        print(str(inc) + ' = ' + name)
        #print('inc=' + str(inc))

def get_rhyme_type_if_it_is_there(line):
    funct_name = 'get_rhyme_type_if_it_is_there()'
    retval = ''
    if '?' in line:
        return retval
    type_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    for t in type_list:
        if t in line:
            return t
    return retval

def is_line_a_rhyming_line(line):
    funct_name = 'is_line_a_rhyming_line()'
    retval = False
    if '?' in line:
        return retval
    type_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    if any(t in line for t in type_list):
        retval = True
    return retval

class rnetwork: # rhyme network
    def __init__(self):
        self.node_dict = {}
        self.same_zi_multi_rhyme_cnt = 0 # Number of times the same characters rhyme more than once in the same stanza
                                         # over the whole Shijing
    def get_unique_edge_list(self):
        retval = []
        master_dict = {}
        for zi_a in self.node_dict:
            zi_a_dict = self.node_dict[zi_a].get_poem_stanza2edge_dict()
            for psn in zi_a_dict:
                if psn not in master_dict:
                    master_dict[psn] = []
                for e_tup in zi_a_dict[psn]:
                    # if we already have (zi_a, zi_b), then don't include (zi_b, zi_a)
                    if e_tup not in master_dict[psn] and (e_tup[1], e_tup[0]) not in master_dict[psn]:
                        master_dict[psn].append(e_tup)
        for key in master_dict:
            retval += master_dict[key]
        return retval

    def get_node_list(self):
        return self.node_dict.keys()

    def get_node_weight(self, zi):
        retval = 0
        if zi in self.node_dict:
            retval = self.node_dict[zi].get_node_weight()
        return retval

    def add_node(self, zi, poem_stanza_num, raw_line):
        if zi.isdigit():
            return
        if is_kana_letter(zi):
            return
        zi = remove_unwanted_chars_from_str(zi)
        if not zi.strip():
            return
        if zi in self.node_dict:
            self.node_dict[zi].increment_node_weight()
            self.node_dict[zi].add_an_occurrence(poem_stanza_num)
            return
        if zi not in self.node_dict:
            self.node_dict[zi] = rnode(zi, poem_stanza_num, raw_line)

    def add_edge(self, first_rhyme_word, sec_rhyme_word, num_rhymes_in_stanza, poem_stanza_num, enforce_ending_similarity=True):
        #NOTE: could change this so that it just adds the NODEs, but they're supposed to be there already
        is_verbose = False
        if not first_rhyme_word.strip() or not sec_rhyme_word.strip():
            return

        if first_rhyme_word not in self.node_dict:
            print('rnetwork::add_edge() ERROR: ' + first_rhyme_word + ' NOT in network!')
            return
        elif sec_rhyme_word not in self.node_dict:
            print('rnetwork::add_edge() ERROR: ' + sec_rhyme_word + ' NOT in network!')
            return
        # NODE::add_edge(self, zi_b, num_rhymes_in_stanza, poem_stanza_num):
        one_repeat = self.node_dict[first_rhyme_word].add_edge(sec_rhyme_word, num_rhymes_in_stanza, poem_stanza_num)
        self.same_zi_multi_rhyme_cnt += one_repeat
        self.node_dict[sec_rhyme_word].add_edge(first_rhyme_word, num_rhymes_in_stanza, poem_stanza_num)

    def get_edge_weight(self, zi_a, zi_b):
        retval = 0
        if zi_a in self.node_dict:
            retval = self.node_dict[zi_a].get_edge_weight(zi_b)
        return retval

    def get_num_times_two_zi_rhymed_more_than_once_in_same_stanza(self):
        return self.same_zi_multi_rhyme_cnt # over the whole shijing (or at least up to where we are now)

    def print_num_nodes(self):
        print(str(len(self.node_dict)))
        print(''.join(self.node_dict.keys()))

    def get_num_nodes(self):
        return len(self.node_dict)

    def print_num_edges(self):
        print(str(self.get_num_edges()) + ' edges for ' + str(int(self.get_num_nodes())) + ' nodes.')

    def get_num_edges(self):
        num_edges = 0
        for zi_a in self.node_dict:
            num_edges += self.node_dict[zi_a].get_num_edges()
        # since there are two chars per edge, the real number of edges is half what is reported by an individual node
        num_edges = num_edges/2.0
        return num_edges
        #print(str(num_edges) + ' edges for ' + str(int(self.get_num_nodes())) + ' nodes.')

    def get_edge_list_for_node(self, node):
        try:
            return self.node_dict[node].get_list_of_edges()
        except IndexError as ie:
            return []

    def print_all_edges(self):
        for zi_a in self.node_dict:
            print(zi_a)
            self.node_dict[zi_a].print_edges()

    def print_single_node_and_its_edges(self, zi_a):
        if zi_a in self.node_dict:
            print(zi_a)
            self.node_dict[zi_a].print_edges()

    def print_all_nodes_n_edges(self, is_verbose=False):
        retval = []
        for zi_a in self.node_dict:
            node_data = self.node_dict[zi_a].print_node(is_verbose)
            retval += node_data
        return retval

    def get_networkx_graph_of_rhyme_network(self, print_data=False):
        funct_name = 'get_networkx_graph_of_rhyme_network()'
        print('Entering ' + funct_name + '...')
        network_data = self.print_all_nodes_n_edges(is_verbose=False)
        retval = nx.Graph()
        current_node = ''
        id2edge_dict = {}
        for nd in network_data:
            if 'Node=' in nd:
                node = nd.split('\t')[0].replace('Node=','')
                node_weight = self.get_node_weight(node)
                retval.add_node(node, weight=node_weight)
                if print_data:
                    print('NODE=' + node + ', WEIGHT=' + str(node_weight))
            else:
                nd = nd.split('\t')
                zi_a = nd[0]
                zi_b = nd[1]
                edge_weight = nd[2]
                unique_id = nd[3]

                if unique_id not in id2edge_dict:
                    id2edge_dict[unique_id] = []
                # if the edge isn't already accounted for, then account for it
                if (zi_a, zi_b) not in id2edge_dict[unique_id]:
                    retval.add_edge(zi_a, zi_b, weight=edge_weight)
                    x = 1 #add edge
                id2edge_dict[unique_id].append((zi_a, zi_b))
                id2edge_dict[unique_id].append((zi_b, zi_a))
                if print_data:
                    print('\t' + 'EDGE=' + zi_a + ', ' + zi_b + ', weight=' + edge_weight + ',ID=' + unique_id)
        print('\tDone.')
        return retval

    def get_infomap_linked_list_of_rhyme_network(self, print_data=False):
        funct_name = 'get_infomap_linked_list_of_rhyme_network()'
        print('Entering ' + funct_name + '...')
        network_data = self.print_all_nodes_n_edges(is_verbose=False)
        retval = nx.Graph()
        current_node = ''
        id2edge_dict = {}
        node_inc = 0
        output_file = 'linked_list' + get_timestamp_for_filename() + '.txt'
        if os.path.isfile(output_file):
            os.remove(output_file)
        append_line_to_utf8_file(output_file, '# A network in Pajek format')
        append_line_to_utf8_file(output_file, '*Vertices in ' + str(self.get_num_nodes()))
        print('# A network in Pajek format')
        print('*Vertices in ' + str(self.get_num_nodes()))
        zi2node_dict = {}
        for nd in network_data:
            if 'Node=' in nd:
                node_inc += 1
                node = nd.split('\t')[0].replace('Node=', '')
                node_weight = self.get_node_weight(node)
                pmsg = str(node_inc) + ' "' + node + '" ' + str(node_weight)
                if 0:
                    print(pmsg)
                append_line_to_utf8_file(output_file, pmsg)
                if node not in zi2node_dict:
                    zi2node_dict[node] = 0
                zi2node_dict[node] = node_inc
        print('*Edges ' + str(self.get_num_edges()))
        append_line_to_utf8_file(output_file, '*Edges ' + str(self.get_num_edges()))
        for nd in network_data:
            if 'Node=' not in nd:
                nd = nd.split('\t')
                zi_a = nd[0]
                zi_b = nd[1]
                edge_weight = nd[2]
                unique_id = nd[3]
                if 0:
                    print(str(zi2node_dict[zi_a]) + ' ' + str(zi2node_dict[zi_b]) + str(edge_weight))
                msg_out = str(zi2node_dict[zi_a]) + ' ' + str(zi2node_dict[zi_b]) + ' ' + str(edge_weight)
                append_line_to_utf8_file(output_file, msg_out)
        print('\tDone.')
        return retval

def remove_unwanted_chars_from_str(tstr):
    unwanted_chars = [')','>','｛','？',']','「','”','）','■','；','：','\'','、','」', '･', '＊','×','?', '○','】','‐', '］',
                      '＝','●','々', 'e', ':','』','〕','Ⅱ']
    #if any(uc in tstr for uc in unwanted_chars):
    for c in unwanted_chars:
        if c in tstr:
            tstr = tstr.replace(c,'')
    return tstr
def get_timestamp_for_filename():
    return datetime.datetime.now().strftime("%A_%d_%B_%Y_%I_%M%p")

class rnode: # rhyme node
    # NOTE: 'poem_stanza_num' should actually be in the form '1.2a'
    #       where:
    #       1 = poem number, 2 = stanza number, a = rhyme type
    def __init__(self, zi, poem_stanza_num, raw_line, initial_weight=1):
        self.zi = zi
        self.zi_weight = initial_weight
        self.delimiter = '\t'
        self.OC = {} # {'baxter1992':'na', 'bns2014':'nˤa', 'panwuyun':'nˤa'}
        self.MC = [] # chars can have more than one reading
        self.poem_n_stanza = poem_stanza_num # first occurrence in the Shijing
        self.occurrences = []
        self.edge_dict = {} # key = {char_b}; value = ({Wab}, {# for poem & stanza + rhyme type})
        #
        self.raw_line = raw_line
        self.add_an_occurrence(raw_line)
        self.add_oc()
        self.add_mc()

    def get_node_weight(self):
        return self.get_num_edges()
        #return self.cnt_num_unique_stanzas()
        #return self.zi_weight

    def increment_node_weight(self):
        self.zi_weight += 1

    def get_poem_stanza2edge_dict(self):
        funct_name = 'get_poem_stanza2edge_dict()'
        retval = {}
        pns_pos = 1
        for zi_b in self.edge_dict:
            for tup_inc in self.edge_dict[zi_b]:
                if tup_inc[pns_pos] not in retval:
                    retval[tup_inc[pns_pos]] = []
                retval[tup_inc[pns_pos]].append((self.zi, zi_b))
                #retval.append((self.zi, zi_b, tup_inc[pns_pos]))
        return retval

    def get_list_of_edges(self):
        funct_name = 'get_list_of_edges()'
        retval = []
        pns_pos = 1
        for k in self.edge_dict:
            for tup_inc in self.edge_dict[k]:
                retval.append((self.zi, k, tup_inc[pns_pos]))
        return retval

    def print_edges(self, is_verbose=False): # rnode::
        w_ab_pos = 0
        pns_pos = 1
        stanza2data_dict = {}
        stanza_list = []
        retval = []
        for k in self.edge_dict:
            try:
                for tup_inc in self.edge_dict[k]:
                    pns = tup_inc[pns_pos]
                    pmsg = '\t' + self.zi + ' -> ' + k + ', W_ab = ' + str(tup_inc[w_ab_pos])
                    pmsg += '; from = ' + pns
                    retval.append(self.zi + '\t' + k + '\t' + str(tup_inc[w_ab_pos]) + '\t' + tup_inc[pns_pos])
                    if pns not in stanza_list:
                        stanza_list.append(pns)
                    if pns not in stanza2data_dict:
                        stanza2data_dict[pns] = []
                    stanza2data_dict[pns].append(pmsg)
            except IndexError as ie:
                print(self.zi + ': ERROR with key=' + k)
        for k in stanza2data_dict:
            for innerk in stanza2data_dict[k]:
                if is_verbose:
                    print(innerk)
        pmsg2 = '['
        for s in stanza_list:
            pmsg2 += '\'' + s + '\', '
        pmsg2 = pmsg2[0:len(pmsg2)-2] + ']'
        if is_verbose:
            print(pmsg2)
        return retval

    def cnt_num_unique_stanzas(self):
        pns_list = []
        for k in self.edge_dict:
            try:
                ttup = self.edge_dict[k][0]
                poem_n_stanza = str(ttup[1])
            except IndexError as ie:
                poem_n_stanza = ''
                continue
            if poem_n_stanza and poem_n_stanza not in pns_list:
                pns_list.append(poem_n_stanza)
        return len(pns_list)

    def get_num_edges(self):
        retval = 0 # zi_b = zi on the other end of the edge
        for zi_b in self.edge_dict:
            retval += len(self.edge_dict[zi_b])
        return retval

    def add_an_occurrence(self, raw_line):
        if raw_line not in self.occurrences:
            self.occurrences.append(raw_line)

    def calculate_edge_weight(self, num_rhymes_in_stanza):
        return 1.0/(num_rhymes_in_stanza - 1.0)

    # NOTE: this 'poem_stanza_num' is the one relevant to this EDGE
    #       May not be the same as the 'poem_stanza_num' used to create the NODE
    #       i.e., the one for the first occurrence of this zi as a rhyme
    # RULES:
    # 1. If two of the same exact lines rhyme (i.e., in different poems), they should only be counted once over
    #    the entire Shijing.
    # 2. If two characters rhyme more than once in the same stanza, then they should be counted only once
    def add_edge(self, zi_b, num_rhymes_in_stanza, poem_stanza_num):
        if zi_b == self.zi: # don't add edges for chars self-rhyming
            return 0
        if zi_b not in self.edge_dict:
            self.edge_dict[zi_b] = []
        else:
            for tp in self.edge_dict[zi_b]:
                if tp[1] == poem_stanza_num: # if zi_a and zi_b have already rhymed once in this stanza, then
                                             # don't count them again
                    print('Zi_a & zi_b rhyme more than once in the same stanza (' + poem_stanza_num + ')')
                    return 1
        W_ab = self.calculate_edge_weight(num_rhymes_in_stanza)
        self.edge_dict[zi_b].append((W_ab, poem_stanza_num))
        #self.edge_list.append((zi_b, num_rhymes_in_stanza, poem_stanza_num))
        return 0

    def get_edge_weight(self, zi_b):
        retval = 0
        if zi_b in self.edge_dict:
            retval = self.edge_dict[zi_b][0][0]
        return retval

    def get_node_str(self):
        d = self.delimiter
        # {zi} + delim + {unique # stanzas} + delim + {node weight}
        return self.zi + d + str(self.cnt_num_unique_stanzas()) + d + str(self.get_node_weight())

    def print_node(self, is_verbose=False):
        pmsg = 'Node = ' + self.zi + ' [ # unique stanzas = ' + str(self.cnt_num_unique_stanzas()) + '; weight = '
        pmsg += str(self.get_node_weight()) + ']'
        msg = 'Node=' + self.zi + '\t' + str(self.cnt_num_unique_stanzas()) + '\t' + str(self.get_node_weight())
        edge_list = self.print_edges(is_verbose)
        edge_list.insert(0, msg) # add node data to beginning of list
        return edge_list

    def add_oc(self):
        self.add_baxter1992_oc()
        self.add_bns2014_oc()
        self.add_panwuyun_oc()

    def add_baxter1992_oc(self):
        x = 1
        if 'baxter1992' not in self.OC:
            self.OC['baxter1992'] = []
        # Get Baxter 1992 data
        # add data

    def add_bns2014_oc(self):
        if 'bns2014' not in self.OC:
            self.OC['bns2014'] = []
        # get Baxter & Sagart 2014 data
        # add data
    def add_panwuyun_oc(self):
        if 'panwuyun' not in self.OC:
            self.OC['panwuyun'] = []
        # get Panwuyun's data
        # add data to self.OC
    def add_mc(self):
        x = 1
        # get MC data
        # add MC data

class rn_rhyme_pairs:
    def __init__(self):
        self.rhyme_pair_dict = {}
        self.occurrence_dict = {}
        #self.repeated_pairs = 0

    def is_only_occurrence(self, first_line, sec_line, rhyme_tag):
        retval = False
        if first_line in self.rhyme_pair_dict:
            if sec_line in self.rhyme_pair_dict[first_line]:
                if len(self.rhyme_pair_dict[first_line][sec_line]) == 1:
                    if self.rhyme_pair_dict[first_line][sec_line][0] == rhyme_tag:
                        retval = True
        return retval

    def is_first_occurrence(self, first_line, sec_line, rhyme_tag):
        retval = False
        if first_line in self.rhyme_pair_dict:
            if sec_line in self.rhyme_pair_dict[first_line]:
                if len(self.rhyme_pair_dict[first_line][sec_line]) == 1:
                    if self.rhyme_pair_dict[first_line][sec_line][0] == rhyme_tag:
                        retval = True
        return retval

    def add_pair_of_rhyming_lines(self, first_line, sec_line, rhyme_tag):
        if first_line not in self.rhyme_pair_dict:
            self.rhyme_pair_dict[first_line] = {}
        if sec_line not in self.rhyme_pair_dict[first_line]:
            self.rhyme_pair_dict[first_line][sec_line] = []
            self.rhyme_pair_dict[first_line][sec_line].append(rhyme_tag)
        self.add_occurrence(first_line, sec_line, rhyme_tag)

    def add_occurrence(self, first_line, sec_line, rhyme_tag):
        key = first_line + ' : ' + sec_line
        if key not in self.occurrence_dict:
            self.occurrence_dict[key] = []
        self.occurrence_dict[key].append(rhyme_tag) # add one occurrence

    def how_many_occurrences(self, first_line, sec_line):
        key = first_line + ' : ' + sec_line
        retval = 0
        if key in self.occurrence_dict:
            retval = len(self.occurrence_dict[key]) + 1
        return retval

    def print_out_unique_rhyming_pairs(self):
        cnt = 0
        for k in self.rhyme_pair_dict:
            for l in self.rhyme_pair_dict[k]:
                print(k + ' : ' + l)
                cnt += 1
        print(str(cnt) + ' unique rhyme pairs printed.')

    def print_out_rhyming_pairs_plus_num_occurrences(self, num_above=0):
        cnt = 0
        for k in self.occurrence_dict:
            # get first occurrence
            #self.rhyme_pair_dict[]
            if len(self.occurrence_dict[k]) > num_above:
                print(k + ': ' + ', '.join(self.occurrence_dict[k]))
                cnt += 1
        print(str(cnt) + ' pairs printed.')

    def print_out_rhyming_pairs(self, num_above=0):
        cnt = 0
        foccurrence = ''
        oc_list = []
        for k in self.occurrence_dict: # if it's in this dictionary, that means it's occurred multiple times
            # get first occurrence
            if len(self.occurrence_dict[k]) > num_above:
                for o in self.occurrence_dict[k]:
                    oc_list.append(o)
                    cnt += 1
            if len(oc_list) > num_above:
                print(k + ': ' + ', '.join(oc_list))
            #foccurrence = ''
            oc_list = []
        print(str(cnt) + ' pairs printed.')

def test_get_shijing_stats_for_single_char():
    funct_name = 'test_get_shijing_stats_for_single_char()'
    get_shijing_stats_for_single_char('濕')#'方')

def get_shijing_stats_for_single_char(tchar):
    funct_name = 'get_shijing_stats_for_single_char()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # remove labels
    raw_line_pos = 6
    rhyme_num_pos = 8
    rhyme_word_pos = 9
    sj_line_list = []
    tchar_as_rhyme_list = []
    tchar_double_rhyme = []
    tchar_non_rhyme = []
    for d in data:
        #print(d)
        if 'x + x + x + x' in d:
            continue
        if tchar not in d: # we're only concerned with lines containing tchar
            continue
        #if '?' in d:
        #    continue
        #
        # TO DO:
        #        - add support for counting number of NON-rhyme occurrences
        #        - add support for counting number of '?' lines skipped (with 'tchar' in it)

        d = d.split('\t')
        rhyme_num = d[rhyme_num_pos]
        rhyme_word = d[rhyme_word_pos]
        raw_line = d[raw_line_pos].replace(' + ','')
        sj_line_list.append(raw_line)

        if rhyme_num.strip() and rhyme_word == tchar:
            if rhyme_num in tchar_as_rhyme_list:
                tchar_double_rhyme.append(rhyme_num)
            tchar_as_rhyme_list.append(rhyme_num)
        elif rhyme_num.strip() and rhyme_word != tchar:
            tchar_non_rhyme.append(raw_line)
        elif not rhyme_num.strip():
            tchar_non_rhyme.append(raw_line)
    sj_str = '\n'.join(sj_line_list)
    print(tchar + ' occurs as a rhyme ' + str(len(tchar_as_rhyme_list)) + ' times:')
    print('\t' + ', '.join(tchar_as_rhyme_list))
    msg = '['
    for e in tchar_as_rhyme_list:
        msg += '\'' + e + '\', '
    msg = msg[0:len(msg)-2] + ']'
    print(msg)
    print(tchar + ' occurs more than once in a stanza ' + str(len(tchar_double_rhyme)) + ' times:')
    print('\t' + ', '.join(tchar_double_rhyme))
    print(tchar + ' occurs in the 《詩經》 ' + str(sj_str.count(tchar)) + ' times.')
    print(tchar + ' occurs as non-rhyme ' + str(len(tchar_non_rhyme)) + ' times (this doesn\'t take 2x in one line into account).')

def test_print_shijing_lines_for_given_char():
    funct_name = 'test_print_shijing_lines_for_given_char()'
    tchar = '濕'#'還'#'邁'#'遺'
    only_rhyme_words = True
    print_shijing_lines_for_given_char(tchar, only_rhyme_words)

#raw_shijing_lines, rhyme_line, non_rhyme_line =
def get_shijing_lines_for_list_of_chars(char_list, only_rhyme_words=False):
    funct_name = 'get_shijing_lines_for_list_of_chars'
    char2line_dict = {}
    for c in char_list:
        raw_lines, rhyme_line, non_rhyme_line = get_shijing_lines_for_given_char(c, only_rhyme_words)
        if c not in char2line_dict:
            char2line_dict[c] = []
        char2line_dict[c] = raw_lines
    return char2line_dict

def print_shijing_lines_for_list_of_chars(char_list, only_rhyme_words=False):
    funct_name = 'print_shijing_lines_for_list_of_chars'
    char2line_dict = {}
    for c in char_list:
        raw_lines = print_shijing_lines_for_given_char(c, only_rhyme_words)
        if c not in char2line_dict:
            char2line_dict[c] = []
        char2line_dict[c] = raw_lines
    return char2line_dict

def print_shijing_lines_for_given_char(tchar, only_rhyme_words=False):
    funct_name = 'print_shijing_lines_for_given_char()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    raw_line_pos = 6
    rhyme_word_pos = 9
    rhyme_line = []
    non_rhyme_line = []
    rhyme_word_msg = ''
    if only_rhyme_words:
        rhyme_word_msg = 'Rhyme words ONLY'
    else:
        rhyme_word_msg = 'ALL occurences'
    print('*-' * 40)
    data_line_msg = '《詩經》 data for 「' + tchar + '」 (' + rhyme_word_msg + '):'
    print(data_line_msg)
    print('-' * (len(data_line_msg)+5))
    raw_shijing_lines, rhyme_line, non_rhyme_line = get_shijing_lines_for_given_char(tchar, only_rhyme_words)
    prefix = ''
    cnt = 1
    for rsl in raw_shijing_lines:
        prefix = '(' + str(cnt) + ') '
        if not only_rhyme_words:
            if rsl in rhyme_line:
                prefix += '*'
        print(prefix + rsl)
        cnt += 1
    if 0:
        for d in data:
            if 'x + x + x + x' in d:
                continue
            if tchar not in d: # we're only concerned with lines containing tchar
                continue
            d_orig = d
            d = d.split('\t')
            raw_line = d[raw_line_pos].replace(' + ','')
            rhyme_word = d[rhyme_word_pos]

            if tchar in raw_line:
                if rhyme_word == tchar:
                    prefix = '*'
                    rhyme_line.append(tchar)
                else:
                    prefix = ''
                    non_rhyme_line.append(tchar)
                if only_rhyme_words:
                    if rhyme_word == tchar:
                        print('\t'.join(d))
                        raw_shijing_lines.append(d_orig)
                else:
                    raw_shijing_lines.append(d_orig)
                    print(prefix + '\t'.join(d))

    print('')
    print(tchar + ' appears in ' + str(len(rhyme_line) + len(non_rhyme_line)) + ' lines in the 《詩經》.')
    print('\t' + str(len(rhyme_line)) + ' of them rhyme.')
    print('\t' + str(len(non_rhyme_line)) + ' of them do not.')
    print('*-' * 40)
    return raw_shijing_lines

def get_shijing_lines_for_given_char(tchar, only_rhyme_words=False):
    funct_name = 'get_shijing_lines_for_given_char()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    raw_line_pos = 6
    rhyme_pos_pos = 8
    rhyme_word_pos = 9
    rhyme_line = []
    non_rhyme_line = []
    raw_shijing_lines = []
    cnt = 0
    for d in data:
        if 'x + x + x + x' in d:
            continue
        if tchar not in d: # we're only concerned with lines containing tchar
            continue
        d_orig = d
        d = d.split('\t')
        raw_line = d[raw_line_pos].replace(' + ','')
        rhyme_word = d[rhyme_word_pos]
        rhyme_pos = d[rhyme_pos_pos]
        cnt += 1
        if tchar in raw_line:
            if rhyme_word == tchar and rhyme_pos.strip():
                rhyme_line.append(d_orig)
            else:
                non_rhyme_line.append(d_orig)
            if only_rhyme_words:
                if rhyme_word == tchar and rhyme_pos.strip():
                    raw_shijing_lines.append(d_orig)
            else:
                raw_shijing_lines.append(d_orig)
    return raw_shijing_lines, rhyme_line, non_rhyme_line

def load_shijing_dictionary():
    funct_name = 'load_shijing_dictionary()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    poem_stanza_num_pos = 3
    line_num_pos = 4
    shijing_dict = {}
    for d in data:
        #print(d)
        #if '?' in d:
        #    continue
        d_local = d.split('\t')
        poem_stanza_num = d_local[poem_stanza_num_pos]
        poem_num = poem_stanza_num.split('.')[0]
        stanza_num = poem_stanza_num.split('.')[1]
        if int(poem_stanza_num.split('.')[0]) > 305:
            continue
        line_num = d_local[line_num_pos]
        if poem_num not in shijing_dict:
            shijing_dict[poem_num] = {}
        if stanza_num not in shijing_dict[poem_num]:
            shijing_dict[poem_num][stanza_num] = {}
        if line_num not in shijing_dict[poem_num][stanza_num]:
            shijing_dict[poem_num][stanza_num][line_num] = d

    if 0:
        for poem_k in shijing_dict:
            for stanza_k in shijing_dict[poem_k]:
                for line_k in shijing_dict[poem_k][stanza_k]:
                    print(shijing_dict[poem_k][stanza_k][line_k])
    return shijing_dict

def create_network_for_baxter1992_data_3():
    funct_name = 'create_network_for_baxter1992_data_3()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    rhyme_word_pos = 9
    rhyme_num_pos = 8
    line_w_rtype_pos = 3
    for d in data: # d - one line of data: 7492	303	玄鳥	303.1	9	商之先后	商 + 之 + 先 + 后	商 + 之 + 先 + 后		后	0 0 0 0
        print(d)
        if '?' in d:
            continue
        d = d.split('\t')
        line_w_rtype = d[line_w_rtype_pos]
        rhyme_word = d[rhyme_word_pos]
        rhyme_num = d[rhyme_num_pos]
        try:
            poem_num = rhyme_num.split('.')[0]
            if poem_num and int(poem_num) > 305:
                continue
            stanza_num = rhyme_num.split('.')[1]
        except IndexError as ie:
            x = 1
        print('poem# = ' + poem_num + ', stanza_num = ' + stanza_num + ', rhyme# = ' + rhyme_num + u', rhyme word = ' + rhyme_word)

def get_rhyme_word_from_line(line):
    funct_name = 'get_rhyme_word_from_line()'
    rhyme_word_pos = 9
    line = line.split('\t')
    rhyme_word = line[rhyme_word_pos]
    return rhyme_word

def get_rhyme_type_from_line(line):
    rhyme_num_pos = 8
    line = line.split('\t')
    rnum = line[rhyme_num_pos].split('.')
    try:
        rhyme_type = rnum[2]
    except IndexError as ie:
        rhyme_type = ''
    return rhyme_type

def get_shijing_line_from_raw_line(raw_line):
    funct_name = 'get_shijing_line_from_raw_line()'
    pos = 7
    line = raw_line.split('\t')[7]
    return line.replace(' + ', '')
    #8	1	關睢	1.2	4	寤寐a求之	寤 + 寐 + 求 + 之	寤 + 寐 + 求 + 之	1.2.a	求	0 0 2 0

def is_this_a_rhyming_line(raw_line, use_question_mark_lines=False):
    retval = False
    if not use_question_mark_lines:
        if '?' in raw_line:
            return retval
    raw_line = raw_line.replace('?', '')
    raw_line = raw_line.replace('x', '')
    rhyme_type = get_rhyme_type_from_line(raw_line)
    if rhyme_type.strip():
        retval = True
    return retval

def cnt_num_unique_lines_for_baxter1992_data():
    funct_name = 'cnt_num_unique_lines_for_baxter1992_data()'
    shijing_dict = load_shijing_dictionary()
    #if rhyme_type not in stanza_dict:
    #    stanza_dict[rhyme_type] = []
    #stanza_dict[rhyme_type].append((line_num, line, rhyme_word, rhyme_num))
    sd_rhyme_word_pos = 2 # stanza dictionary (sd) indicies
    sd_rhyme_num_pos = 3
    sd_raw_line_pos = 4
    rhyme_pairs = rn_rhyme_pairs()
    stanza_dict = {}
    line_pairs_dict = {}
    rhyme_net = rnetwork()
    multi_list = []
    use_question_mark_lines = False
    num_skipped_multi_lines = 0 # counts the number of line pairs that are skipped because they appear more than once
    unique_lines = []
    for poem_k in shijing_dict: # once per poem
        for stanza_k in shijing_dict[poem_k]: # once per stanza
            # first: collect stanza data
            stanza_dict = {} # reset variable for next stanza
            for line_k in shijing_dict[poem_k][stanza_k]: # once per stanza line
                raw_line = shijing_dict[poem_k][stanza_k][line_k]
                print('raw_line = ' + raw_line)
                rhyme_word = get_rhyme_word_from_line(raw_line)
                rhyme_type = get_rhyme_type_from_line(raw_line)
                sj_line = get_shijing_line_from_raw_line(raw_line)
                if sj_line not in unique_lines:
                    unique_lines.append(sj_line)
    print(str(len(unique_lines)) + ' unique lines in the Shijing data.')

def test_get_single_stanza_data_for_baxter1992_data():
    funct_name = 'test_get_single_stanza_data_for_baxter1992_data()'
    print('Welcome to ' + funct_name + '!')
    shijing_dict = load_shijing_dictionary()
    stanza_list = ['114.3', '193.8', '253.2']
    #stanza_list = ['9.2.c', '12.2.a', '205.3.a', '234.1.a', '241.6.a', '274.1.a', '300.4.a', '304.1.a', '29.3.a', '223.4.a', '253.1.a', '108.2.a', '177.4.b', '255.6.a', '129.1.a', '168.3.a', '260.7.b', '238.5.a', '256.4.a', '211.2.a', '241.3.c', '236.1.a', '241.7.b', '262.2.a', '272.1.a', '294.1.a', '303.1.a']
#['205.3', '234.1', '241.6', '274.1', '300.4', '304.1']
    poem_num_pos = 0
    stanza_num_pos = 1
    for sl in stanza_list:
        sl = sl.split('.')
        poem_num = sl[poem_num_pos]
        stanza_num = sl[stanza_num_pos]
        stanza_raw_data = shijing_dict[poem_num][stanza_num]
        stanza_dict = {}
        rhyme_word_pos = 9
        line_w_type_pos = 5
#        rhyme_type_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        for s in stanza_raw_data:
            data = stanza_raw_data[s].split('\t')
            line_w_type = data[line_w_type_pos]
            rhyme_type = get_rhyme_type_if_it_is_there(line_w_type)
            rhyme_word = data[rhyme_word_pos]
            print(stanza_raw_data[s])
            #print('line_w_type = ' + line_w_type + ', rhyme_type = ' + rhyme_type + ', rhyme_word = ' + rhyme_word)
            #print('')
            if rhyme_type.strip():
                if rhyme_type not in stanza_dict:
                    stanza_dict[rhyme_type] = []
                stanza_dict[rhyme_type].append(rhyme_word)
        for key in stanza_dict: # key = rhyme type
            unique_rhymes = len(set(stanza_dict[key]))
            print(str(unique_rhymes) + ' unique rhymes of type ' + key + ': ' + u''.join(set(stanza_dict[key])))
            w_ab = 1.0/(unique_rhymes - 1.0)
            print('\tw_ab = ' + str(w_ab))

def get_single_stanza_data_for_baxter1992_data(pns_num):
    funct_name = 'get_single_stanza_data_for_baxter1992_data()'
    shijing_dict = load_shijing_dictionary()
    poem_num_pos = 0
    stanza_num_pos = 1
    pns_num = pns_num.split('.')
    poem_num = pns_num[poem_num_pos]
    stanza_num = pns_num[stanza_num_pos]
    stanza_raw_data = shijing_dict[poem_num][stanza_num]
    return stanza_raw_data

if 0:
    def get_single_stanza_data_for_baxter1992_data():
        funct_name = 'get_single_stanza_data_for_baxter1992_data()'
        shijing_dict = load_shijing_dictionary()
        #if rhyme_type not in stanza_dict:
        #    stanza_dict[rhyme_type] = []
        #stanza_dict[rhyme_type].append((line_num, line, rhyme_word, rhyme_num))
        sd_rhyme_word_pos = 2 # stanza dictionary (sd) indicies
        sd_rhyme_num_pos = 3
        sd_raw_line_pos = 4
        rhyme_pairs = rn_rhyme_pairs()
        stanza_dict = {}
        line_pairs_dict = {}
        rhyme_net = rnetwork()
        multi_list = []
        use_question_mark_lines = False
        num_skipped_multi_lines = 0 # counts the number of line pairs that are skipped because they appear more than once
        unique_lines = []
        for poem_k in shijing_dict: # once per poem
            for stanza_k in shijing_dict[poem_k]: # once per stanza
                # first: collect stanza data
                stanza_dict = {} # reset variable for next stanza
                for line_k in shijing_dict[poem_k][stanza_k]: # once per stanza line
                    raw_line = shijing_dict[poem_k][stanza_k][line_k]
                    print('raw_line = ' + raw_line)
                    rhyme_word = get_rhyme_word_from_line(raw_line)
                    rhyme_type = get_rhyme_type_from_line(raw_line)
                    sj_line = get_shijing_line_from_raw_line(raw_line)
                    if sj_line not in unique_lines:
                        unique_lines.append(sj_line)
        print(str(len(unique_lines)) + ' unique lines in the Shijing data.')

def create_network_for_baxter1992_data_4():
    funct_name = 'create_network_for_baxter1992_data_4()'
    shijing_dict = load_shijing_dictionary()
    sd_rhyme_word_pos = 2 # stanza dictionary (sd) indicies
    sd_rhyme_num_pos = 3
    sd_raw_line_pos = 4
    rhyme_pairs = rn_rhyme_pairs()
    stanza_dict = {}
    line_pairs_dict = {}
    rhyme_net = rnetwork()
    multi_list = []
    use_question_mark_lines = False
    num_skipped_multi_lines = 0 # counts the number of line pairs that are skipped because they appear more than once
    print_up_to_poem_num = 305
    #
    # For each poem in the Shijing...
    for poem_k in shijing_dict: # once per poem
        if int(poem_k) > print_up_to_poem_num:
            break
        #
        # For each stanza in the current poem...
        for stanza_k in shijing_dict[poem_k]: # once per stanza
            # first: collect stanza data
            stanza_dict = {} # reset variable for next stanza
            #
            # for each line in the current stanza...
            for line_k in shijing_dict[poem_k][stanza_k]: # once per stanza line
                raw_line = shijing_dict[poem_k][stanza_k][line_k]
                #print('raw_line = ' + raw_line)
                rhyme_word = get_rhyme_word_from_line(raw_line)
                rhyme_type = get_rhyme_type_from_line(raw_line)
                sj_line = get_shijing_line_from_raw_line(raw_line)

                #
                # skip lines that don't rhyme
                if not is_this_a_rhyming_line(raw_line, use_question_mark_lines):
                    continue
                if rhyme_type not in stanza_dict:
                    stanza_dict[rhyme_type] = []
                #print('\trhyme_word = ' + rhyme_word + ', rhyme_type = ' + rhyme_type + u'Shijing line = ' + sj_line)
                stanza_dict[rhyme_type].append((line_k, sj_line, rhyme_word, rhyme_type, raw_line))
            #
            # Second: Process stanza data
            for k in stanza_dict: # k = rhyme type (like 'a', 'b', etc.) - per rhyme type in the stanza
                #print(k)
                G_ab = len(stanza_dict[k]) # the number of rhymes of the current type within this stanza
                s_rhyme_group = []
                if len(stanza_dict[k]) <= 1:
                    if stanza_dict[k]:
                        raw_line = stanza_dict[k][0][4]
                        raw_line = raw_line.split('\t')
                        line_w_type = raw_line[5]
                        if line_w_type.count(k) < 2:
                            continue
                for inc in range(0, len(stanza_dict[k]), 1): # go through each stanza line for this rhyme type --
                    # i.e., per stanza line for a given rhyme type
                    #
                    # NOTE: in add_node():
                    #       if the node doesn't already exist, it's created
                    #       if the node DOES exist, then this occurrence is added to its list of occurrences
                    #       (assuming it's not already there. If it is, it's not counted twice)
                    sd_raw_line = stanza_dict[k][inc][sd_raw_line_pos]
                    sd_rhyme_num = sd_raw_line.split('\t')[8]

                    rhyme_net.add_node(stanza_dict[k][inc][sd_rhyme_word_pos],
                                       sd_rhyme_num,
                                       sd_raw_line)

                    # deal with pairs of rhyming lines and edges
                    # -- need edge between each pair of rhyming words in stanza (for same rhyme type)
                    if inc < len(stanza_dict[k])-1: # stanza_dict[k] tup: (line_num, line, rhyme_word, rhyme_num, raw_line)
                        first_rhyming_line = stanza_dict[k][inc][1]
                        first_rhyme_word = stanza_dict[k][inc][sd_rhyme_word_pos]
                        sec_rhyming_line = stanza_dict[k][inc + 1][1]
                        sec_rhyme_word = stanza_dict[k][inc + 1][sd_rhyme_word_pos]
                        #print(str(inc) + ': ' + first_rhyming_line + ' -> ' + sec_rhyming_line)
                        rhyme_tag = poem_k + '.' + stanza_k
                        rhyme_pairs.add_pair_of_rhyming_lines(first_rhyming_line, sec_rhyming_line, rhyme_tag)
                        # if this is not the first occurrence of this pair of lines...
                        if rhyme_pairs.is_first_occurrence(first_rhyming_line, sec_rhyming_line, rhyme_tag):
                            s_rhyme_group.append(first_rhyme_word)
                            s_rhyme_group.append(sec_rhyme_word)
                        else:
                            num_skipped_multi_lines += 1

                        srhyme_num = stanza_dict[k][inc][3]
                        #print('first_rhyming_line = ' + first_rhyming_line + ', rhyme_num = ' + srhyme_num)

                s_rhyme_group  = list(set(s_rhyme_group)) # rhyme group per stanza per rhyme type
                num_lines_same_type = len(s_rhyme_group)
                #
                # add edges
                #
                # is_first_occurrence
                print_debug_msg = False
                for left_inc in range(0, num_lines_same_type, 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, num_lines_same_type, 1):
                        rhyme_num = poem_k + '.' + stanza_k + '.' + k # k = rhyme type (like a, b, c, etc.)
                        msg += s_rhyme_group[left_inc] + ':' + s_rhyme_group[right_inc] + ', num_lines_same_type = '
                        msg += str(num_lines_same_type) + ', poem_stanza_num = ' + rhyme_num
                        if print_debug_msg:
                            print(msg) # debug only
                        msg = ''
                        rhyme_net.add_edge(s_rhyme_group[left_inc], s_rhyme_group[right_inc], num_lines_same_type, rhyme_num)
                if print_debug_msg:
                    print('')
            stanza_dict = {} # reset dict for next stanza

    print('-*'*40)
    #fang_edge_list = rhyme_net.get_edge_list_for_node('方')
    #fmsg = '['
    #for e in fang_edge_list:
    #    fmsg += '(' + ', '.join(e) + '), '
    #fmsg = fmsg[0:len(fmsg)-2] + ']'
    #print(fmsg)
    #rhyme_net.print_all_edges()
    #rhyme_net.print_all_nodes_n_edges()
    #print(str(rhyme_net.get_num_times_two_zi_rhymed_more_than_once_in_same_stanza()))
    print('='*100)
    print('     Comparing NODES')

    ash_nodes = rhyme_net.get_node_list()
    data_file = os.path.join(get_poepy_data_dir(), 'Baxter1992.tsv')
    #data_file = os.path.join(get_soas_data_dir(), 'Baxter1992.tsv') # same file that Ash's code is using
    p = Poems(data_file)
    p.get_rhyme_network()
    x = p.G
    #p.G.edges() - returns list of edge tups
    poepy_nodes = []

    for key in p.G._node:
        poepy_nodes.append(key)

    print('Ash\'s code has ' + str(len(ash_nodes)))
    print('Poepy has ' + str(len(poepy_nodes)))
    print('Comparing the lists:')
    ash_set = set(ash_nodes)
    for n in ash_nodes:
        if not n.strip():
            print('INVISIBLE ASH NODE!!')
    for n in poepy_nodes:
        if not n.strip():
            print('INVISIBLE POEPY NODE!!')
        if n not in ash_nodes:
            print(n + ' MISSING FROM ASH NODES!')
            print('NOTE: 慍 is missing due to Ash\'s code not handling stanza 237.8 correctly.')
    diff_nodes = ash_set.difference(set(poepy_nodes))
    poepy_set = set(poepy_nodes)
    diff2_nodes = poepy_set.difference(ash_set) # .difference() shows which elements from the long set are missing in the
                                                #   shorter set
    intersection_nodes = ash_set.intersection(set(poepy_nodes))
    print('')
    print('='*100)
    print('     Comparing EDGES')
    print(str(num_skipped_multi_lines) + ' rhyming line pairs were skipped because they appeared more than once.')
    #print(str(rhyme_net.get_num_nodes() + ' number of nodes.'))
    rn_edge_list = rhyme_net.get_unique_edge_list()
    print(str(len(rn_edge_list)) + ' elements in rn_edge_list:')
    pp_edge_list = get_poepy_edge_list_for_baxter1992()
    in_rn_not_in_pp = [] # in Ash's list, not in Poepy's list
    in_pp_not_in_rn = [] # in Poepy's list, not in Ash's list
    in_rn_and_pp = [] # in both Ash's and Poepy's list
    for ttup in rn_edge_list:
        if ttup in pp_edge_list:
            in_rn_and_pp.append(ttup)
        elif ttup not in pp_edge_list:
            in_rn_not_in_pp.append(ttup)
    for ttup in pp_edge_list:
        if ttup in rn_edge_list:
            if ttup not in in_rn_and_pp:
                in_rn_and_pp.append(ttup)
        elif ttup not in rn_edge_list:
            in_pp_not_in_rn.append(ttup)
    print(str(len(pp_edge_list)) + ' elements in the poepy edge list (' + str(len(set(pp_edge_list))) + ' UNIQUE elements).')
    print(str(len(rn_edge_list)) + ' elements in Ash\'s edge list (' + str(len(set(rn_edge_list))) + ' UNIQUE elements).')
    print(str(len(in_rn_and_pp)) + ' elements in both Ash\'s edge list, and in the poepy edge list (' + str(len(set(in_rn_and_pp))) + ' UNIQUE elements).')

    rnp_msg = ''
    in_rn_and_pp.sort()
    for ttup in in_rn_and_pp:
        rnp_msg += '(' + ', '.join(ttup) + '), '
    rnp_msg = rnp_msg[0:len(rnp_msg)-2]
    print('\t' + rnp_msg)
    dupe_list = []
    non_dupe_list = []
    for e in in_pp_not_in_rn:
        x = e
        if e[0] == e[1]:
            dupe_list.append(e[0])
        else:
            non_dupe_list.append(e)
        y = 1
    print(str(len(in_pp_not_in_rn)) + ' elements in the poepy list, but not in Ash\'s list (' + str(len(set(in_pp_not_in_rn))) + ' UNIQUE elem.).')
    in_pp_not_in_rn.sort()
    p_not_r_msg = ''
    for ttup in in_pp_not_in_rn:
        p_not_r_msg += '(' + ', '.join(ttup) + '), '
    p_not_r_msg = p_not_r_msg[0:len(p_not_r_msg)-2]
    print('\t' + p_not_r_msg)
    print('Of these, ' + str(len(dupe_list)) + ' are dupes (i.e., a char rhyming with itself):')
    print('\t' + ', '.join(dupe_list))
    print('These are not dupes: ')
    nd_msg = ''
    reverse_is_in = []
    #
    # TO DO:
    #   write code to check if the elements in non_dupe_list
    #     are actual rhyming pairs
    #     - get the raw shijing lines for each character in the pair
    #     - for each char, make a list of which {poem #}.{stanza #} they appear in
    #     - compare the lists to find out where they actually rhyme
    #     - print out the actual stanzas and eyeball them
    for ttup in non_dupe_list:
        if (ttup[1], ttup[0]) in in_rn_not_in_pp: # check if the reverse ordered tup is in Ash's list
            reverse_is_in.append(ttup)
            non_dupe_list.remove(ttup)

    for ttup in non_dupe_list:
        nd_msg += '(' + ', '.join(ttup) + '), '
    nd_msg = nd_msg[0:len(nd_msg) - 2]
    # check for each non-dupe if it's the reverse of something in Ash's list
    print('\t' + nd_msg)
    print('Of the non-dupes, ' + str(len(reverse_is_in)) + ' are there, but in the reverse order.')
    rev_msg = ''
    for ttup in reverse_is_in:
        rev_msg += '(' + ttup[0] + ', ' + ttup[1] + '), '
    rev_msg = rev_msg[0:len(rev_msg)-2]
    print('\t' + rev_msg)
    print('-> removed these from the non-dupe list.')

    print(str(len(in_rn_not_in_pp)) + ' elements in Ash\'s list, but not in the poepy list (' + str(len(set(in_rn_not_in_pp))) + ' UNIQUE elem.).')
    r_not_p_msg = ''
    in_rn_not_in_pp.sort()
    for ttup in in_rn_not_in_pp:
        r_not_p_msg += '(' + ', '.join(ttup) + '), '
    r_not_p_msg = r_not_p_msg[0:len(r_not_p_msg)-2]
    print('\t' + r_not_p_msg)
    #rhyme_pairs.print_out_rhyming_pairs_plus_num_occurrences()
    #rhyme_pairs.print_out_rhyming_pairs(1) # 1 - print out pairs that occur more than once
    #print(''.join(rn_edge_list))
    if 0:
        poepy_nodes = '鳩洲逑流求得服側采友芼樂谷木萋飛喈莫濩綌斁歸私衣否母筐行崔虺罍懷岡黃觥傷砠瘏痡吁纍綏荒將縈成詵振薨繩揖蟄華家實室蓁人罝夫丁城逵仇林心有掇捋袺襭休廣永泳方楚馬蔞駒枚飢肄棄尾燬邇趾子定姓角族居御盈沚事中宮僮公祁還蟲螽忡降蕨惙說薇悲夷蘋濱藻潦筥釜下女伐茇敗憩拜露夜屋獄足牙墉訟從皮紽蛇革緎食縫總陽遑息處七吉三今塈謂星征東同昴裯猶汜以悔渚與沱過歌麇春包誘樕鹿束玉脫帨吠車李緡孫葭豝虞蓬豵舟憂酒遊茹據愬怒石席轉卷選悄小少摽微裏已裳亡絲治訧風羽野雨頏及泣音南淵身土顧冒好報良忘出卒述暴笑敖悼霾來思曀寐嚏靁鏜兵仲宋闊手老活洵信夭勞薪苦阻臧葉涉厲揭鳴軌牡鴈旦泮菲違體死遲畿薺弟笱後游救喪讎售鞫覆育毒冬窮潰故躬節日久戎耳舞俁虎組籥翟爵榛苓淇姬謀泲禰姊干言舝邁衛害泉歎漕悠門殷貧艱適益謫敦遺摧涼雱邪且霏狐烏姝隅躕孌管煒美荑異貽泚瀰鮮洒浼殄離施景養逝河儀它天特慝埽道醜襄詳長讀辱珈佗宜何髢揥皙帝展袢顏媛唐鄉姜麥北弋葑庸鶉彊兄君栗漆瑟虛堂京桑零田千蝀指隮姻命為齒止俟禮旄郊紕四畀旟都五予旌祝六告驅侯反遠濟閟蝱狂極尤之猗磋磨僩咺諼青瑩簀錫璧綽較虐澗寬阿薖陸軸宿頎妻姨脂蠐犀眉倩盼驕鑣朝瀖發孼朅蚩丘期媒垣關漣遷落若葚耽隕湯爽德怨岸宴晏哉竿右左儺滺支觿知遂悸韘甲杭望刀桀殳容疾背痗梁帶瓜琚桃瑤玖靡苗搖穗醉噎塒月佸括渴簧房陶翿申甫蒲許乾修歗淑濕羅罹吪罦造覺罿凶聰藟滸父涘漘昆聞葛蕭秋艾歲檻菼敢啍璊奔穴麻嗟國館粲蓆作里杞畏牆園檀仁狩武舉所揚射控送鴇首阜慢罕掤弓彭旁英翔消麃喬遙抽濡渝飾力直彥路怯惡魗爛加贈順問蘇松龍充童蘀伯吹和漂要餐溱洧士丰巷昌墠阪即淒瀟膠瘳晦喜衿佩達闕水雲存巾員闍荼藘娛漙婉願瀼渙蘭乎謔藥清聲明光夢憎間肩儇茂狼著素庭闥倒召晞顛令圃瞿兩蕩雙畝鞠克忉怛丱弁環鬈鋂偲鰥鱮唯薄鞹夕濔滔儦蹌名正甥霜襋提辟刺洳度曲藚殽謠其棘岵屺偕閒閑外泄廛貆輻億輪淪囷飧鼠號康除蹶慆樞榆婁愉栲杻考保鑿襮沃皓繡鵠粼升朋聊條匊篤芻戶者湑踽比佽菁睘袪褎究栩黍怙翼稷粱嘗常燠我周域巔旃然焉鄰耋楊碩獲收輈續轂馵驂合軜邑膺縢興蒼央湄躋坻梅裘慄防禦欽多櫟駮棣檖師袍矛澤戟渠餘簋飽輿上鼓夏缶差婆荍椒魴鯉紵語菅牂煌肺晢斯矣萃訊巢苕甓惕皎僚糾懰受慅照燎紹慘株陂荷蕑悁儼枕膏曜冠欒慱韡結一枝偈飄嘌弔鬵閱雪祋芾咮媾騏忒年嘆稂蓍火烈褐耜庚葦斨鵙績葽蜩穫貉狸功股宇薁菽棗稻壽壺苴樗稼穋茅綯穀沖陰蚤韭場響羊疆恩閔据租譙翛翹嘵濛蠋垤窒至縭嘉皇錡銶遒踐復胡膚几瑕苹笙蒿昭恌傚芩琴湛騑盬駸諗隰諏駱駰均詢威裒原難平寧生豆飫具孺翕帑圖嚶藇羜舅咎衍愆酤暇固庶祿陵增享王福崩承柔聘剛疚駕業捷騤依腓戒哀牧載旆況塗書杜幝痯恤近罶鯊鱧旨時罩汕衎又臺萊基枸楰耇寫泥豈濃雝草藏貺饗櫜酬莪浮棲飭熾急則顒章安軒憲祉芑奭衡瑲珩涖率旅闐焞雷攻龐囂奕舄馳破驚戊禱午麌矢兕醴寡宅嗷晣噦煇旂隼海懲錯饔藿客粟蓫葍山苞祖堵閣橐去芋楹冥簟寢羆祥床璋喤地裼瓦議群犉濈池訛餱蒸雄兢肱魚巖瞻惔談斬監瘥氐維毗迷親仕殆傭訩惠戾屆闋酲政領騁誦邦痒瘉口愈侮僕勝局蹐脊蜴滅輔意沼炤云慇椓獨卯騰宰史徒向徹逸罪辜鋪臻退瘁荅使血沮用邛厎集程經聽爭膴他冰富扈卜擣梓在嘒淠伎雌先墐掎杝幠涵讒盟盜甘餤共樹數厚麋階勇尰禍可陳舍盱易祇壎貫篪蜮錦甚箕幡昊詩頹萎蔚恥恃畜腹律弗匕砥履視涕空試漿箱舌暑濁漢紀鳶桋臣賢傍仰掌塵疧熲重罟奧蹙戚湝回鼛妯僭祀亨祊慶踖炙格酢熯式備起尸婦奏盡引甸理雰霂渥彧穡賓廬菹祜毛膋耔薿倉皁莠螣賊穉穧利黑茨珌白似胥屏翰那觩秣柏弈懌怲霰見鷮教譽樊設抗張的僊抑怭秩僛郵俄傞怠羖識鎬黼芹駟紓葵膍裕饇取附屬瀌髦柳蹈暱愒瘵撮髮蠆綠沐藍襜詹牛營幽愛煁卑誨趨燔獻炮高沒波玄矜民新世楨冔臭孚商妹渭莘洋瓞飴龜茲陾登馮伉慍拔兌駾喙槱趣峨楫相男恫臨廟入赫廓翳栵剔椐柘對季援羨恭色衝連茀仡肆忽拂亟囿伏濯翯躍樅鏞鍾廱逢賀佐崇豐夙靈字呱訏匐嶷穟幪唪秀秠負揄蹂叟惟軷爾斝臄咢堅鈞句鍭主醹斗祺融終俶匱類壼胤涇馨沙脯潀宗亹熏欣芬匹綱位糧囊繁宣巘曹牢匏飲單亂鍛密饎溉酋卬怓大殘板癉亶諫輯冾寮蕘蹻耄熇懠屎資圭攜藩壞豫諶懟內卿呼螗羹舊刑傾撥愚訓尚漏覯藐劉旬填黎翩泯燼頻往競梗辰痻圉毖熱削溺僾逮寶腸譖忌迪垢隧悖詈牲推助川焚遯贏神蕃郿粻番嘽賦吐補鏘齊解鍚幭厄屠到噳完蠻貊壑藉舒洸浦緒騷霆虜塞奪鴟寺織倍狄罔優幾深鞏訌玷貶替竭弘禋禎穰簡工秭妣皆瞽鮪肅穆后鶬嘏追孝敬鳥蓼柞耘畛傑香趙朽挃櫛紑俅鼒駓伾雒繹才騢祛徂駽燕始茷茆馘囚搜博逆黮琛金秬魯犧乘綅蒙諾尺假昔恪芒越截遟祗圍球旒絿厖動竦鉞曷櫱羌嚴濫丸虔梴'
        poepy_node_set = set(poepy_nodes)
        my_nodes_set = set(rhyme_net.get_node_list())
        isect = my_nodes_set.intersection(poepy_nodes)
        print('isect has ' + str(len(isect)) + ' members:')
        print(''.join(isect))
        idiff = my_nodes_set.difference(poepy_node_set)
        print('idiff ' + ''.join(idiff))
        diff_char = ''.join(idiff)
        if diff_char in my_nodes_set:
            print(diff_char + ' appears in my nodes.')
        elif diff_char in poepy_node_set:
            print(diff_char + ' appears in poepy_node_set.')

def playing_with_poepy_edge_list():
    pp_edge_list = get_poepy_edge_list_for_baxter1992()
    for p in pp_edge_list:
        x = 1

# here: 'repeating rhyme word' means the same character rhymes on different lines
def count_num_stanzas_w_repeating_rhyme_word_for_baxter_1992():
    funct_name = 'count_num_stanzas_w_repeating_rhyme_word_for_baxter_1992()'
    shijing_dict = load_shijing_dictionary()
    #if rhyme_type not in stanza_dict:
    #    stanza_dict[rhyme_type] = []
    #stanza_dict[rhyme_type].append((line_num, line, rhyme_word, rhyme_num))
    sd_rhyme_word_pos = 2 # stanza dictionary (sd) indicies
    sd_rhyme_num_pos = 3
    rhyme_pairs = rn_rhyme_pairs()
    stanza_dict = {}
    line_pairs_dict = {}
    rhyme_net = rnetwork()
    multi_list = []
    one_zi_multi_lines_dict = {}
    use_question_mark_lines = False
    for poem_k in shijing_dict: # once per poem
        for stanza_k in shijing_dict[poem_k]: # once per stanza
            # first: collect stanza data
            stanza_dict = {} # reset variable for next stanza
            for line_k in shijing_dict[poem_k][stanza_k]: # once per stanza line
                raw_line = shijing_dict[poem_k][stanza_k][line_k]
                #print('raw_line = ' + raw_line)
                rhyme_word = get_rhyme_word_from_line(raw_line)
                rhyme_type = get_rhyme_type_from_line(raw_line)
                sj_line = get_shijing_line_from_raw_line(raw_line)
                if not is_this_a_rhyming_line(raw_line, use_question_mark_lines):
                    continue
                if poem_k not in one_zi_multi_lines_dict:
                    one_zi_multi_lines_dict[poem_k] = {}
                if stanza_k not in one_zi_multi_lines_dict[poem_k]:
                    one_zi_multi_lines_dict[poem_k][stanza_k] = {}
                if rhyme_word not in one_zi_multi_lines_dict[poem_k][stanza_k]:
                    one_zi_multi_lines_dict[poem_k][stanza_k][rhyme_word] = []
                one_zi_multi_lines_dict[poem_k][stanza_k][rhyme_word].append(sj_line)
    cnt = 0
    for poem_k in one_zi_multi_lines_dict:
        for stanza_k in one_zi_multi_lines_dict[poem_k]:
            for rhyme_word in one_zi_multi_lines_dict[poem_k][stanza_k]:
                if len(one_zi_multi_lines_dict[poem_k][stanza_k][rhyme_word]) > 1:
                    cnt += 1
                    print(rhyme_word + ' rhymes in multiple lines in ' + poem_k + '.' + stanza_k)
    print(str(cnt) + ' occurrences.')

def count_num_stanzas_for_baxter_1992():
    funct_name = 'count_num_stanzas_for_baxter_1992()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    num_stanzas = 0
    poem2stanza_dict = {}
    for d in data:
        d = d.split('\t')
        if '306.1' in d:
            continue
        print(d[3])
        poem_num = d[3].split('.')[0]
        stanza_num = d[3].split('.')[1]
        if poem_num not in poem2stanza_dict:
            poem2stanza_dict[poem_num] = []
        if stanza_num not in poem2stanza_dict[poem_num]:
            poem2stanza_dict[poem_num].append(stanza_num)
            num_stanzas +=1

    stanza_cnt = 0
    for k in poem2stanza_dict:
        stanza_cnt += len(poem2stanza_dict[k])

    print('Two separate counts of the number of 《詩經》 stanzas:')
    print('\tnum_stanzas = ' + str(num_stanzas))
    print('\tstanza_cnt = ' + str(stanza_cnt))

def count_num_nodes_for_baxter_1992():
    funct_name = 'count_num_nodes_for_baxter_1992()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    line_num_pos = 4
    line_w_type_pos = 5
    line_pos = 6
    rhyme_word_pos = 9
    rhyme_num_pos = 8
    prev_stanza_num = -1
    prev_poem_num = 0
    stanza_dict = {}
    line_pairs_dict = {}
    rhyme_net = rnetwork()
    multi_list = []
    sd_line_num_pos = 0
    sd_line_pos = 1
    sd_rhyme_word_pos = 2
    sd_rhyme_num_pos = 3
    rhyme_pairs = rn_rhyme_pairs()
    rhyme_word_list = []
    question_marks = []
    potential_rhyme = []
    diff_chars = ['虔', '丸', '梴']
    lines_w_diff_chars = []
    double_rhyme_words = []
    for d in data: # d - one line of data: 7492	303	玄鳥	303.1	9	商之先后	商 + 之 + 先 + 后	商 + 之 + 先 + 后		后	0 0 0 0
        #print(d)
        #print('For ' + d + ':')
        for dc in diff_chars:
            if dc in d:
                lines_w_diff_chars.append(d)
        d = d.split('\t')
        rhyme_word = d[rhyme_word_pos]
        rhyme_num = d[rhyme_num_pos]
        line_w_type = d[line_w_type_pos]

        line = d[line_pos].replace(' + ', '')
        if line.count(rhyme_word) > 1:
            #double_rhyme_words.append((line, rhyme_num))
            print(line)
        if '?' not in line_w_type:
            if rhyme_num.strip():
                rhyme_word_list.append(rhyme_word)
            else:
                potential_rhyme.append(rhyme_word)
        else:
            question_marks.append(rhyme_word)
            potential_rhyme.append(rhyme_word)
        if rhyme_word.strip() and not rhyme_num.strip():
            x = 1

        #print('RHYME_NUM = ' + rhyme_num)
        rnum = rhyme_num.split('.')
        line_num = d[line_num_pos]
        poem_num = rnum[0]
        try:
            stanza_num = rnum[1]
        except IndexError as ie:
            #print('SKIPPING: ' + line_w_type)
            continue # skipping NON-rhyming line
        if not prev_poem_num: # initiate
            prev_poem_num = poem_num
        rhyme_type = rnum[2]
        if line_w_type.count(rhyme_type) > 1:
            double_rhyme_words.append((line_w_type, rhyme_num))

        poem_name = get_poem_name_given_number(poem_num)
        msg = '(' + poem_num + ') ' + poem_name + ', rhyme_word = ' + rhyme_word + ', rhyme num = ' + rhyme_num
        msg += ', stanza num = ' + stanza_num + ', rhyme type = ' + rhyme_type + ', line = ' + line + ', line # = ' + line_num
        msg += ', line_w_type = ' + line_w_type
    print(''.join(list(set(rhyme_word_list))))
    print(str(len(rhyme_word_list)) + ' rhyming characters in the Shijing (' + str(len(set(rhyme_word_list))) + ' are UNIQUE)')
    #print() + ' of those are unique.')
    print(str(len(question_marks)) + ' have question marks (' + str(len(set(question_marks))) + ' are UNIQUE)')
    #print() + ' that have question marks are UNIQUE.')
    print(str(len(potential_rhyme)) + ' potentials rhymes (' + str(len(set(potential_rhyme))) + ' are UNIQUE)')
    #print('Lines with diff chars:')
    #print('\n'.join(lines_w_diff_chars))
    #rhyme_net.print_num_edges()
    for l in double_rhyme_words:
        print(':'.join(l))
    print(str(len(double_rhyme_words)) + ' lines with double rhyme words.')

def compare_lists():
    # list_long is from the get Shijing stats for single char function

    list_long = ['9.1.c', '9.2.c', '9.3.c', '12.2.a', '29.3.a', '108.2.a', '129.1.a', '168.3.a', '168.3.a', '177.4.b', '205.3.a', '211.2.a', '223.4.a', '234.1.a', '236.1.a', '238.5.a', '241.3.c', '241.6.a', '241.7.b', '253.1.a', '255.6.a', '256.4.a', '260.7.b', '262.2.a', '272.1.a', '274.1.a', '294.1.a', '300.4.a', '303.1.a', '304.1.a']
    # list_short is from the Node printing code

    list_short = ['9.2.c', '12.2.a', '205.3.a', '234.1.a', '241.6.a', '274.1.a', '300.4.a', '304.1.a', '29.3.a', '223.4.a', '253.1.a', '108.2.a', '177.4.b', '255.6.a', '129.1.a', '168.3.a', '260.7.b', '238.5.a', '256.4.a', '211.2.a', '241.3.c', '236.1.a', '241.7.b', '262.2.a', '272.1.a', '294.1.a', '303.1.a']
    #list_long = ['One', 'Two', 'Three', 'Four']
    #list_short = ['One', 'Two']
    #s = set(list_short)
    #list_out = [x for x in list_long if x not in s]
    print('list_long is from the get Shijing stats for single char function:')
    print('list_long = ' + ', '.join(list_long))
    print('')
    print('list_short is from the Node printing code:')
    print('list_short = ' + ', '.join(list_short))
    set_short = set(list_short)
    list_out = [e for e in list_long if e not in set_short]
    print('diff = ' + u', '.join(list_out))

def compare():
    # a = 1809
    a = '芬威鋪雱錡子亨意甸瓦欒君桀穉銶神舍陾鼒香翯域千閔國振惕蟄狩谷殽矜塞鷮厚理狼附的食宿芋堂喤重夭保鬈六出士慝蒼躬落軌雲蒙袺名武履盡尚寧飛罝羹洲闍繡炤饇屆怭皮貽慢關庭宜弈瀌狐濈愛騤績慇絲肺啍薄齊載悄僛偲與教顏淒匹榆瑤懲難熯阻戚句刀褐宣北耳向梅則旅轂蛇襄鎬婉牡裏位員儼葍口瞿脂追衛遠佗畀番瑩婆酋冠邑傾貆陽截洸鏞德畏譖墐淠酬粻草贏劉增俶仇晢緡族彧荅集邛廛有秩潀周荒裯膠纍玉湄愆尾麥娛旌壎燕蚤菼牢俁旂舝掇衝幡斬芑帶鴇令先邦丱茆滅錯支籥輿熇祁柞錦珈薖屠鳥虛稼鏘羖高室暴嘆貺氐作涼房肆庶家怙田僩泥戶羨金率萋摧同犉莠說宋菹龐趨為沚豈怓蘋勇罪深訓蝱內李奕闋禱要煌鳩傷蹻一晞拂楨蠆角伎慘袪弋淑椒隧誨年詵踽荼朋餤懠茀潦賓蓫撮組瀰麋著慅冾阪櫜渴旨燼越季吪芻俅繹格覯外野慄鈞憂驕監皎亡衡防類怯膏屺背央癉卑黎傚他微視韭崔鍭醜澗胡入薺蠋棗据箱煒謂痗陂生痻脊具固腓漆懰砠藉鹿除聰沮謀阜仰治睘驚芒對備功苕知雷之海工悲壑洳迪垣杝趙郵僭忉雨恪博浼祝裒苴敗且霏裼畿怛噳簧泲違杞寡間遒苹瑕稷膺白遷觥猶湯私忌復伏四定風引匕瘳豫濫繩婦穗窮旒黍檖巢紽罍筥蝀綌斁璋召頹爾遙渭濟秣濱祀駽讒廓河射毖寬鉞綅使服尤軸儇願滺箕濡隅吁瓜群零替足泮葛送夫顛舄詩波霾麇憎數殘辟堅享訌屬祗惠閑過焉駸老妣鱧歗行原黑秠我極聘晏綽埽騰思陶友蹐瀟凶囂地丁容葚伾踖髦球涘受菽嘏紹襋讎醉抑綏罟杻駰紀久搖紓溉億藍妹鳴苦蕩養澤成京痡矛力歸葑敢式罔佸兄平完逆少藚圍秭匏蜮牂佽寢岸駱基鞹飭茲抽息篤蘇敬冰刑那所姨黃帝羽棣蕭砥飄翼吠盱飢罦卬喈薨蘀皓渙直陵攻篪虺遊熏嘉穡在禦束檻諫云豵矢罩赫言媾穟削鮪薪擣隼右嘽燬欣昌王鯉詹腸紕孼靡肅咺芼常蹌墠玖翕韡趾下泄妯律訟魯攜芩以怠虔莫碩趣鮮流藘選覆鑿戟歲珩望賀儀髮沒沖囚推來浮五舌大稂隰已粟身盬駒見斝松階遂急燔時僮滔虎詳蜩鍾姻租亂從恥鍛瞽痒禋談縫連尸淪譙羜簋休祺動襭杜館洋考新穧荍逮瀖其回南禰螗旆隮塒帨舟始琚豆淇紵池特椓洵申顧總栩縈豐展鋂弘腹問退沼悖尺消好爵醴畛疆寺登鱮忡僾予幽城加秋甘縢垤侯橐場訊蒲裘妻惔亟土側月仕蒸利曀異祿耄俄巾雪才局傭袢泣近愒昭飽曷甥粲裳天馘菲濯降緒霜渥樹栗史龍離祉瑲祥席呱卿嗟苞几柏鼛脫忽涉殷鍚臄囊暱僊葵賢舉諶糧莘偕絿收疧汜羆唯諏易括笙饗珌似孌閒駕軷齒漙徒湝閟慆匊飫升恫僚奏粱哀弁吐桋藏甚歎玄頻苗蓁汕夙喬道宴禮御舒鰥泯逸惟蒿巖民靁壺臺卯女宇雒簀咮用伉孺萎遑庸匐罹湛依政誦涕小芾章鶬鼠故指經逵父倒棲厲訧漕膍慱續垢艱秬梓得反喜稻夷餐羌昊騁門適盜抗張卜革寶幾今瀼邇號維斨樂舅閣控浦股帑彊事徹挃去露競炮溱梗聊櫟唪兵塵靈囿孝信征眉軜蟲修牧臭翳響燠兢沃磋蔚包涇翩懟辰雌姊傍畝芹孚賦鞏惙貫蹈茹雰尰游施陰謫饎憩救悁蓼克醹安照檀倩兕奪破奭鬵上魴櫛枝貶脯扈體者穴冒旄聞旃業炙酒順字痯臻顒圉正叟居程鏜恌美喙山溺栲孫鳶熾許鞠朽斗節貉逑媛肄仡餱麌皆婁將寮織鄰拜左杭葦惡錫搜廬玷竦甓佩贈營色廱諼飴綯綠午翟揭穫缶鶉遟提戾鑣藥遺飲怲皁書穆宮匱嶷吉獲臨姓磨耇郊甫弟胤巘漿茨襜蠻龜忒寫魚舊譽翛萊祖鴈儺虜東床報茅螽烏焚竿石毛夢藐后軒幠倍明度坻恤晦郿藇揄相儦告襮琛翹辜洧方噎丰株往滸鄉素諾輻騢泳昔笱景揥釜卷起幪否童筐仲猗沐隕環育穀火戊陸曹湑涖假管麻褎瘥發弓瓞萃戎剛斯敦騑差達逢盼識耘蹂厖犀丘鷊牆笑濁荑公死邪枸蹙壽牲愉嘗彥囷咎柔侮霆渚況處枕售鵙蓬逝柘蓍首泚黼殆夜揚害仁蹶舞濃堵兌宗掤可衿活盈闥里轉都濩血狄罶敖究暇勝茂踐車虞璧塈乾屏林饔曲栵躕楰康丸詢輔姬旦恭菁傑雙掌蕘朅還毒殳嘌輈試岡多翿梁衎祛福中躍燎日粼盟渝刺祇獄客據設訏悸瞻議梴狸騷爭謔肩媒奧永富枚雄彭泉榛圃昴光宅嘵融臣屋昆膋翔酲誘膚止漣獻密夕青犧曜岵漢楹茷喪馮慶薇頎川心三葭均旬毗渠柳賊緎甲恃棘棄忘餘華酤荷男簡耽怒牛暑領清楫肱馵嚴木吹淵傞遯螣哉椐期祜後袍結路罿填聲存若徂蔞補共空琴秀墉驅怨麃疚駮掎卒到瘁黮楊樕觿偈長七胥烈奔祋葉鴟英穰濕訩虐焞愚又蜴皇楚廟單悔蕑濛闊塗漘噦勞俟罕求它耜雝莪迷冔蚩衣佐桃飧薁厎祊語倉躋咢窒歌合悼蘭輪覺漏水艾瘵爽葽輯蕨干槱嚏手采簟宰貊伐鼓實狂裕主韘唐鯊閱音乘造師嚶嘒魗竭弔髢即駾皙綱熱朝屎圭闐厄茇鵠至益剔訛幭熲廣矣承馬撥姜資弗春夏愬蓆終樊及獨崇捋星乎晣何殄憲欽藟聽充騏拔糾解沙興菅薿愈陳寐樗穋羅呼煁姝取負摽援世紑優禍亹闕嗷樅羊伯觩爛衍遲崩縭臧藿悠耔辱峨旁酢駓繁恩煇諗苓畜蠐瘏較和巷邁疾璊人詈桑捷馳漂命良讀壞懌櫱樞戒冥藻霂謠飾濔亶沱揖貧冬藩牙翰駟助僕豝幝霰阿驂涵條母馨板蕃比瑟親潰旟巔園圖禎頏述然洒商壼兩庚懷鞫膴瘉耋'
    b = '鳩洲逑流求得服側采友芼樂谷木萋飛喈莫濩綌斁歸私衣否母筐行崔虺罍懷岡黃觥傷砠瘏痡吁纍綏荒將縈成詵振薨繩揖蟄華家實室蓁人罝夫丁城逵仇林心有掇捋袺襭廣永楚馬泳方蔞駒枚飢肄棄尾燬邇趾子定姓角族居御盈沚事中宮僮公祁還蟲螽忡降蕨惙說薇悲夷蘋濱藻潦筥釜下女伐茇敗憩拜露夜屋獄足牙墉訟從皮紽蛇革緎食縫總陽遑息處七吉三今塈謂星征東同昴裯猶汜以悔渚與沱過歌麇春包誘樕鹿束玉脫帨吠車李緡孫葭豝虞蓬豵舟憂酒遊茹據愬怒石席轉卷選悄小少摽微裏已裳亡絲治訧風羽野雨頏及泣音南淵身土顧冒好報良忘出卒述暴笑敖悼霾來思曀寐嚏靁鏜兵仲宋闊手老活洵信夭勞薪苦阻臧葉涉厲揭鳴軌牡鴈旦泮菲違體死遲畿薺弟笱後游救喪讎售鞫覆育毒冬窮潰故躬節日久戎耳舞俁虎組籥翟爵榛苓淇姬謀泲禰姊干言舝邁衛害泉歎漕悠門殷貧艱適益謫敦遺摧涼雱邪且霏狐烏姝隅躕孌管煒美荑異貽泚瀰鮮洒浼殄離施景養逝河儀它天特慝埽道醜襄詳長讀辱珈佗宜何髢揥皙帝展袢顏媛唐鄉姜麥北弋葑庸鶉彊兄君栗漆瑟虛堂京桑零田千蝀指隮姻命為齒止俟禮旄郊紕四畀旟都五予旌祝六告驅侯反遠濟閟蝱狂極尤之猗磋磨僩咺諼青瑩簀錫璧綽較虐澗寬阿薖陸軸宿頎妻姨脂蠐犀眉倩盼驕鑣朝瀖發孼朅蚩丘期媒垣關漣遷落若葚耽隕湯爽德怨岸宴晏哉竿右左儺滺支觿知遂悸韘甲杭望刀桀殳容疾背痗梁帶瓜琚桃瑤玖靡苗搖穗醉噎塒月佸括渴簧房陶翿申甫蒲許乾修歗淑濕羅罹吪罦造覺罿凶聰藟滸父涘漘昆聞葛蕭秋艾歲檻菼敢啍璊奔穴麻嗟國館粲蓆作里杞畏牆園檀仁狩武舉所揚射控送鴇首阜慢罕掤弓彭旁英翔消麃喬遙抽濡渝飾力直彥路怯惡魗爛加贈順問蘇松龍充童蘀伯吹和漂要餐溱洧士丰巷昌墠阪即淒瀟膠瘳晦喜衿佩達闕水雲存巾員闍荼藘娛漙婉願瀼渙蘭乎謔藥清聲明光夢憎間肩儇茂狼著素庭闥倒召晞顛令圃瞿兩蕩雙畝鞠克忉怛丱弁環鬈鋂偲鰥鱮唯薄鞹夕濔滔儦蹌名正甥霜襋提辟刺洳度曲藚殽謠其棘岵屺偕閒閑外泄廛貆輻億輪淪囷飧鼠號康除蹶休慆樞榆婁愉栲杻考保鑿襮沃皓繡鵠粼升朋聊條匊篤芻戶者湑踽比佽菁睘袪褎究栩黍怙翼稷粱嘗常燠我周域巔旃然焉鄰耋楊碩獲收輈續轂馵驂合軜邑群膺縢興蒼央湄躋坻梅裘慄防禦欽多櫟駮棣檖師袍矛澤戟渠餘簋飽輿上鼓夏缶差婆荍椒魴鯉紵語菅牂煌肺晢斯矣萃訊巢苕甓惕鷊皎僚糾懰受慅照燎紹慘株陂荷蕑悁儼枕膏曜冠欒慱韡結一枝偈飄嘌弔鬵閱雪祋芾咮媾騏忒年嘆稂蓍火烈褐耜庚葦斨鵙績葽蜩穫貉狸功股宇薁菽棗稻壽壺苴樗稼穋茅綯穀沖陰蚤韭場響羊疆恩閔据租譙翛翹嘵濛蠋垤窒至縭嘉皇錡銶遒踐復胡膚几瑕苹笙蒿昭恌傚芩琴湛騑盬駸諗隰諏駱駰均詢威裒原難平寧生豆飫具孺翕帑圖嚶藇羜舅咎衍愆酤暇固庶祿陵增享王福崩承柔聘剛疚駕業捷騤依腓戒哀牧載旆況塗書杜幝痯恤近罶鯊鱧旨時罩汕衎又臺萊基枸楰耇寫泥豈濃雝草藏貺饗櫜酬莪浮棲飭熾急則顒章安軒憲祉芑奭衡瑲珩涖率旅闐焞雷攻龐囂奕舄馳破驚戊禱午麌矢兕醴寡宅嗷晣噦煇旂隼海懲錯饔藿客粟蓫葍山苞祖堵閣橐去芋楹冥簟寢羆祥床璋喤地裼瓦議犉濈池訛餱蒸雄兢肱魚巖瞻惔談斬監瘥氐維毗迷親仕殆傭訩惠戾屆闋酲政領騁誦邦痒瘉口愈侮僕勝局蹐脊蜴滅輔意沼炤云慇椓獨卯騰宰史徒向徹逸罪辜鋪臻退瘁荅使血沮用邛厎集程經聽爭膴他冰富扈卜擣梓在嘒淠伎雌先墐掎杝幠涵讒盟盜甘餤共樹數厚麋階勇尰禍可陳舍盱易祇壎貫篪蜮錦甚箕翩幡昊詩頹萎蔚恥恃畜腹律弗匕砥履視涕空試漿箱舌暑濁漢紀鳶桋臣賢傍仰掌塵疧熲重罟奧蹙戚湝回鼛妯僭祀亨祊慶踖炙格酢熯式備起尸婦奏盡引甸理雰霂渥彧穡賓廬菹祜毛膋耔薿倉皁莠螣賊穉穧利黑茨珌白似胥屏翰那觩秣柏弈懌怲霰見鷮教譽樊設抗張的僊抑怭秩僛郵俄傞怠羖識鎬黼芹駟紓葵膍裕饇取附屬瀌髦柳蹈暱愒瘵撮髮蠆綠沐藍襜詹牛營幽愛煁卑誨趨燔獻炮高沒波玄矜民新世楨冔臭孚商妹渭莘洋瓞飴龜茲陾登馮伉拔兌駾喙槱趣峨楫相男恫臨廟入赫廓翳栵剔椐柘對季援羨恭色衝連茀仡肆忽拂亟囿伏濯翯躍樅鏞鍾廱逢賀佐崇豐匹孝夙靈字呱訏匐嶷穟幪唪秀秠負揄蹂叟惟軷爾斝臄咢堅鈞句鍭主醹斗祺融終俶匱類壼胤涇馨沙脯潀宗亹熏欣芬綱位糧囊繁宣巘曹牢匏飲單亂鍛密饎溉酋卬怓大殘板癉亶諫輯冾寮蕘蹻耄熇懠屎資圭攜藩壞豫諶懟內卿呼螗羹舊刑傾撥愚訓尚漏覯藐劉旬填黎泯燼頻往競梗辰痻圉毖熱削溺僾逮寶腸譖忌迪垢隧悖詈牲推助川焚遯贏神蕃郿粻番嘽賦吐補鏘齊解鍚幭厄屠到噳完蠻貊壑藉舒洸浦緒騷霆虜塞奪鴟寺織倍狄罔優幾深鞏訌玷貶替竭弘禋禎穰簡工秭妣皆瞽鮪肅穆后鶬嘏追敬鳥蓼柞耘畛傑香趙朽挃櫛紑俅鼒駓伾雒繹才騢祛徂駽燕始茷茆馘囚搜博逆黮琛金秬魯犧乘綅蒙諾尺假昔恪芒越截遟祗圍球旒絿厖動竦鉞曷櫱羌嚴濫'
    set_a = set(a)
    for e in set_a:
        if e not in b:
            print(e)

def test_get_max_index():
    funct_name = 'test_get_max_index()'
    #max(k for k, v in x.iteritems() if v != 0)
    tdict = {'1':'hello line 1', '2':'hello line 2', '5':'hello line 5', '7':'hello line 7'}
    max_ind = max(k for k, v in tdict.items())
    print(k for k, v in tdict.items())
    print('MAX = ' + max_ind)
    for linc in range(1, int(max_ind)+1, 1):
        try:
            print(str(linc) + ': ' + tdict[str(linc)])
        except KeyError as ke:
            continue
        for inner_linc in range(linc + 1, int(max_ind)+1, 1):
            if inner_linc == 4:
                break
            print('\tinner_linc = ' + str(inner_linc))

def list_test():
    funct_name = 'list_test()'
    mlist = ['a', 'b', 'c', 'd']
    for inc in range(0, len(mlist), 1):
        if inc < len(mlist) - 1:
            print(str(inc) + ': ' + mlist[inc] + ' > ' + mlist[inc+1])

def fancy_indexing():
    x = 1
    num_lines_same_type = 9
    #msg = ''
    for left_inc in range(0, num_lines_same_type, 1):
        msg = ''
        for right_inc in range(left_inc + 1, num_lines_same_type, 1):
            msg += str(left_inc) + '-' + str(right_inc) + ', '
        msg = msg[0:len(msg)-2]
        print(msg)

def fancy_indexing2():
    nodes2make_edges = ['仔', '仕', '以', '伺', '似', '你']
    num_lines_same_type = len(nodes2make_edges)
    for left_inc in range(0, num_lines_same_type, 1):
        msg = ''
        for right_inc in range(left_inc + 1, num_lines_same_type, 1):
            msg += nodes2make_edges[left_inc] + '-' + nodes2make_edges[right_inc] + ', '
        msg = msg[0:len(msg)-2]
        print(msg)

def get_poepy_data_dir():
    return os.path.join('C:' + os.sep + 'users', 'ash', 'vm4pdf', 'Lib', 'site-packages', 'poepy', 'data')

def get_poepy_network():
    funct_name = 'get_poepy_network()'
    data_file = os.path.join(get_poepy_data_dir(), 'Baxter1992.tsv')
    p = Poems(data_file)
    p.get_rhyme_network()
    return p.G

def get_poepy_edge_list_for_baxter1992():
    funct_name = 'get_poepy_edge_list_for_baxter1992()'
    data_file = os.path.join(get_poepy_data_dir(), 'Baxter1992.tsv')
    p = Poems(data_file)
    p.get_rhyme_network()
    retval = []
    for ttup in p.G.edges():
        retval.append(ttup)
    return retval
    #p.G.edges() - returns list of edge tups

def test_poepy_stuff():
    funct_name = 'test_poepy_stuff()'
    print('welcome to ' + funct_name)
    # data_file = os.path.join('C:' + os.sep + 'users', 'ash', 'vm4pdf', 'Lib', 'site-packages', 'poepy', 'data', 'Baxter1992.tsv')
    data_file = os.path.join(get_poepy_data_dir(), 'Baxter1992.tsv')
    p = Poems(data_file)
    p.get_rhyme_network()
    x = p.G
    #p.G.edges() - returns list of edge tups
    poepy_nodes = []

    for key in p.G._node:
        poepy_nodes.append(key)
    print('poepy_nodes: ')
    print(''.join(poepy_nodes))
    print('# Nodes: ' + str(len(p.G)))
    print('# UNIQUE Nodes: ' + str(len(set(p.G))))
    x = 1
    #p = Poems()

def test_print_list_of_entry_types_from_bib_file():
    funct_name = 'test_print_list_of_entry_types_from_bib_file()'
    print(funct_name + ' Welcomes you!')
    bib_file = os.path.join(get_hanproject_dir(), 'han.bib')
    if not os.path.isfile(bib_file):
        print('INVALID file: ' + bib_file)
        return
    print_list_of_entry_types_from_bib_file(bib_file)

def print_list_of_entry_types_from_bib_file(bib_file):
    funct_name = 'print_list_of_entry_types_from_bib_file()'
    file_data = readlines_of_utf8_file(bib_file)
    type_list = []
    for fd in file_data:
        fd = fd.replace('\n','')
        if '@' in fd:
            fd = fd.replace('@','')
            fd = fd.split('{')[0].strip()
            if fd not in type_list:
                type_list.append(fd)
            #print(fd)
    type_list.remove('abstract =') # this results from the code confusing a @ from an email address with a type
    type_list.sort()
    print('.bib file: ' + bib_file)
    print('\tHas the following types:' )
    print('\t\n'.join(type_list))

#(求, 休), (休, 舟), (休, 首), (休, 觩), (盈, 旌), (公, 鍾), (螽, 戎), (忡, 戎), (憂, 滺), (鳴, 旌), (鳴, 驚), (禮, 濟), (旌, 驚), (遷, 安), (問, 慍), (福, 載), (福, 備), (安, 山), (安, 丸), (安, 虔), (安, 梴), (鍾, 逢)
# for troubleshooting
# - the code figures out which stanzas each character of a pair appear in, and finds the common stanzas if they exist
# - if no common stanza exists for a pair, the code spits out a message: NO common stanzas for 安 & 山!
# - if a common stanza does exist, the stanza is printed to the screen so that you can eyeball it to confirm
#   that the two chars of the pair indeed rhyme in said stanza
def dupe_test():
    funct_name = 'dupe_test()'
    dupe_list = [('求', '休'), ('休', '舟'), ('休', '首'), ('休', '觩'), ('盈', '旌'), ('公', '鍾'), ('螽', '戎'), ('忡', '戎'), ('憂', '滺'), ('鳴', '旌'), ('鳴', '驚'), ('禮', '濟'), ('旌', '驚'), ('遷', '安'), ('問', '慍'), ('福', '載'), ('福', '備'), ('安', '山'), ('安', '丸'), ('安', '虔'), ('安', '梴'), ('鍾', '逢')]#[('求', '休')]
    #dupe_list = [('休', '首')]
    only_rhyme_words = True
    char_list = []
    for d in dupe_list:
        char_list.append(d[0])
        char_list.append(d[1])
    char2line_dict = get_shijing_lines_for_list_of_chars(char_list, only_rhyme_words)
    for dupe_tup in dupe_list:
        print('For tup (' + dupe_tup[0] + ', ' + dupe_tup[1] + '):')
        stanza_list_0 = given_list_of_raw_lines_get_list_of_poem_dot_stanza(char2line_dict[dupe_tup[0]])
        stanza_list_1 = given_list_of_raw_lines_get_list_of_poem_dot_stanza(char2line_dict[dupe_tup[1]])
        stanza_list_0 = set(stanza_list_0)
        common_stanzas = stanza_list_0.intersection(set(stanza_list_1))

        if common_stanzas:
            print('Stanzas common to ' + dupe_tup[0] + ' & ' + dupe_tup[1] + ': ')
            print('\t' + ', '.join(common_stanzas))
            for cs in common_stanzas:
                stanza = get_single_stanza_data_for_baxter1992_data(cs)
                if stanza:
                    for s in stanza:
                        print(stanza[s])
        else:
            print('NO common stanzas for ' + dupe_tup[0] + ' & ' + dupe_tup[1] + '!')
        print('*-'*40)

# troubleshooting:
# - Use this to print out all of the stanzas that each character in a dupe occurs in
# - Search the printed out to eyeball if the two chars appear as rhymes in a stanza
def raw_data_dupe_test():
    funct_name = 'raw_data_dupe_test()'
    #dupe_test_list = [('安', '虔'), ('安', '梴'), ('盈', '旌'), ('鳴', '旌'), ('鳴','驚'), ('旌', '驚'),('遷', '安'), ('問', '慍')]
    #dupe_test_list = [('遷', '安'), ('問', '慍')]
    dupe_test_list = [('安', '山'), ('安', '丸')]
    char_list = []
    for ttup in dupe_test_list:
        if ttup[0] not in char_list:
            char_list.append(ttup[0])
        if ttup[1] not in char_list:
            char_list.append(ttup[1])
    only_rhyme_words = False
    char2line_dict = get_shijing_lines_for_list_of_chars(char_list, only_rhyme_words)
#get_single_stanza_data_for_baxter1992_data()
    tup0_stanzas = []
    tup1_stanzas = []
    for ttup in dupe_test_list:
        print('-*'*40)
        print('(' + ttup[0] + ', ' + ttup[1] + ') data:')
        print(ttup[0])
        tup0_lines = char2line_dict[ttup[0]]
        tup0_stanzas = []
        tup1_stanzas = []
        for t0l in tup0_lines:
            poem_n_stanza_num = t0l.split('\t')[3]
            if poem_n_stanza_num not in tup0_stanzas:
                tup0_stanzas.append(poem_n_stanza_num)
        print(ttup[0] + ' appears in these stanza: ' + ', '.join(tup0_stanzas))
        for pns in tup0_stanzas:
            raw_stanza = get_single_stanza_data_for_baxter1992_data(pns)
            print('')
            for rs in raw_stanza:
                print(ttup[0] + ': ' + raw_stanza[rs])
#        print('\n'.join(char2line_dict[ttup[0]]))
        print('')
        print(ttup[1])
        tup1_lines = char2line_dict[ttup[1]]
        for t1l in tup1_lines:
            poem_n_stanza_num = t1l.split('\t')[3]
            if poem_n_stanza_num not in tup1_stanzas:
                tup1_stanzas.append(poem_n_stanza_num)
        print(ttup[1] + ' appears in these stanza: ' + ', '.join(tup1_stanzas))
        for pns in tup1_stanzas:
            raw_stanza = get_single_stanza_data_for_baxter1992_data(pns)
            print('')
            for rs in raw_stanza:
                print(ttup[1] + ': ' + raw_stanza[rs])


#        print('\n'.join(char2line_dict[ttup[1]]))


def given_list_of_raw_lines_get_list_of_poem_dot_stanza(rline_list):
    funct_name = 'given_list_of_raw_lines_get_list_of_poem_dot_stanza()'
    poem_dot_stanza_pos = 3
    retval = []
    for l in rline_list:
        l = l.split('\t')
        retval.append(l[poem_dot_stanza_pos])
    return retval

# print: 韋、旗、荒、商、光、同、邦、逸、室、衛、隊、城、生、耕、寧、京、征、平、楚、輔、弼、後
#   like
def print_list_of_chars_like_python_list(cline, delim):
    funct_name = 'print_list_of_chars_like_python_list()'
    clist = cline.split(delim)
    retval = ''
    for c in clist:
        retval += '\'' + c + '\', '
    print(retval[0:len(retval)-2])
    return retval[0:len(retval)-2]

def get_fayin_only(mc_list):
    fayin = []
    for m in mc_list:
        m = m.split(' ')[0]
        m = m.replace('X', '')
        m = m.replace('H', '')
        fayin.append(m)
    return fayin

def have_compatible_yunwei(zi_a, zi_b, is_verbose=False):
    funct_name = 'have_compatible_yunwei()'
    mc_a = get_mc_data_for_char(zi_a)
    mc_b = get_mc_data_for_char(zi_b)
    fayin_a = get_fayin_only(mc_a)
    fayin_b = get_fayin_only(mc_b)
    nonopen = ['g', 'n', 'm', 'k', 't', 'p']
    retval = False
    for f_a in fayin_a:
        last_f_a = f_a[len(f_a)-1]
        for f_b in fayin_b:
            last_f_b = f_b[len(f_b)-1]
            if last_f_a == 'g' and f_a[len(f_a)-2] == 'n' or last_f_a == 'k': # if f_a == 'ng'
                if last_f_b == 'g' and f_b[len(f_b)-2] == 'n':
                    retval = True
                    if is_verbose:
                        print(f_a + ' & ' + f_b + ' have compatible endings')
                    break
                elif last_f_b == 'k':
                    retval = True
                    if is_verbose:
                        print(f_a + ' & ' + f_b + ' have compatible endings')

                    break
            elif last_f_a == 'n' or last_f_a == 't': # if f_a == 'n'
                if last_f_b == 'n' or last_f_b == 't':
                    retval = True
                    if is_verbose:
                        print(f_a + ' & ' + f_b + ' have compatible endings')
                    break
            elif last_f_a == 'm' or last_f_b == 'p': # if f_a == 'm'
                if last_f_b == 'm' or last_f_b == 'p':
                    retval = True
                    if is_verbose:
                        print(f_a + ' & ' + f_b + ' have compatible endings')
                    break
            elif last_f_a not in nonopen and last_f_b not in nonopen: # all else is open syllables
                retval = True
                if is_verbose:
                    print(f_a + ' & ' + f_b + ' have compatible endings')
            else:
                if is_verbose:
                    print(f_a + ' & ' + f_b + ' are NOT compatible!')

    return retval

    #x = 1
        #print(poem_dot_stanza)
#test_poepy_stuff()
#count_num_nodes_for_baxter_1992()
#count_num_stanzas_for_baxter_1992()
#playing_with_poepy_edge_list()

#dupe_test()

#raw_data_dupe_test()

#create_network_for_baxter1992_data_4() #---


#test_get_single_stanza_data_for_baxter1992_data()
#test_get_shijing_stats_for_single_char()
#test_print_shijing_lines_for_given_char()
#print_shijing_lines_for_list_of_chars(['求', '休', '觩'], True)
#print_list_of_chars_like_python_list('方、旁、重、僮','、')