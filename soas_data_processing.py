#! C:\Python36\
# -*- encoding: utf-8 -*-
#
#
# Notes about the REWRITE:
# 1. need filename object that takes care of all input and output files
# 2. need poem data object that keeps track of stanza, data_type (received_shi, mirrors, stelae), meta data, etc.
# 3. Functions parsing raw data should be called: parse_raw_{data source name}_data()
# 4. Functions that read in parsed data should be called: readin_parsed_{data source name}_data()
# 5. parse_raw_{data source name}() should be called from inside readin_parsed_{data source name}()
#    and only run if the parsed data file does not exist
# 6. Consider keeping a log file
# 7. Overriding bracket operators [ ] in Python: https://stackoverflow.com/questions/1957780/how-to-override-the-operator-in-python
# 8. Need overarching naming convention
#    - when "graph" means the type of network you need to run com det algos, call it "nxgraph" or "nx_graph"
#    - "rnetwork" only refers to the "rnetwork"
#    - change all instances of "pvis" to "pyvis"
#    - need to distinguish between "annotator" which literally puts markers in files vs. networks representing an annotator
# 9. Change name of "processing_...()" files to "pre_com_det_processing(data_type)"


# About this code:
# 1. It is exploratory, not pre-designed
# 2. The goal is to solve problems as quickly as possible. Any code that would need to be used
#    for mass production (e.g., as part of a publicly available library) will need to be
#    designed and re-coded
# 3. The code is written to run on my machine. In order to get it to run on other machines,
#    there is a set of get_X_dir() functions that need to be modified:
#    get_soas_code_dir()
#    get_hanproj_dir()
#    get_mirrors_dir()
#    get_stelae_dir()
#    etc.

# rhyming assumptions for naive annotators:
#
# For the mao 2008 stelae data
# - each line rhymes, i.e., all words before a 。 or ； rhyme (except special words like 兮、也、etc.)
# For the Lu 1983 received shi
# - every other line rhymes
import os
import codecs
from copy import deepcopy
encode = codecs.utf_8_encode
import sinopy
#import scipy
#import numpy
import cydifflib
from hanproj_filename_depot import filename_depot
#from num_conversion import kansuji2arabic
from soas_rnetwork_test import rnetwork
from soas_rnetwork_test import calculate_edge_weight_given_num_rhymes
from soas_rnetwork_test import let_this_char_become_node
from soas_rnetwork_test import get_timestamp_for_filename
from soas_rnetwork_test import delete_file_if_it_exists
from soas_rnetwork_test import print_debug_message
from soas_imported_from_py3 import readlines_of_utf8_file
#from soas_imported_from_py3 import get_soas_code_dir
#from soas_imported_from_py3 import get_phonological_data_dir
#from soas_imported_from_py3 import get_hanproj_dir
from soas_network_utils import load_schuessler_data
from soas_network_utils import lhan_initials
from soas_network_utils import aspiration
from soas_network_utils import zero_initial
from soas_network_utils import post_codas
from soas_network_utils import rhyme2color
from soas_network_utils import utf8_bom_b
from soas_network_utils import lh_main_vowels
from soas_network_utils import lh_medials
from soas_network_utils import get_schuessler_late_han_for_glyph
from soas_network_utils import get_late_han_rhyme_for_glyph
from soas_network_utils import parse_schuessler_late_han_syllable
from soas_network_utils import get_rhyme_from_schuessler_late_han_syllable
from soas_network_utils import readin_most_complete_schuessler_data
from soas_network_utils import cleanup_ocm_ipa
from soas_network_utils import cleanup_late_han_ipa
from soas_network_utils import handle_short_parens
from soas_network_utils import get_schuessler_late_han_data
from soas_network_utils import sch_glyph2phonology
from soas_network_utils import rhyme_color_tracker
from soas_network_utils import readlines_of_utf8_file
#from soas_network_utils import readin_results_of_community_detection
from soas_network_utils import readin_community_detection_group_descriptions
from soas_network_utils import get_rhyme_from_late_han
from soas_network_utils import append_line_to_output_file
#from soas_network_utils import get_com_det_group_descriptions_for_combo_data
from soas_network_utils import group2color
from soas_network_utils import is_hanzi
from soas_network_utils import exception_chars
from soas_network_utils import if_file_exists
from soas_rhyme_net_structs import stanza_processor
from soas_rhyme_net_structs import create_tree
from soas_rhyme_net_structs import given_root_node_get_list_of_possible_paths
from soas_rhyme_net_structs import retreive_path_from_nodes
from soas_rhyme_net_structs import find_path_optimized_for_rhyme
from soas_rhyme_net_structs import rhyme_marker
from soas_rhyme_net_structs import if_special_mirror_punctuation
from soas_rhyme_net_structs import append_line_to_utf8_file
from soas_rhyme_net_structs import if_not_unicode_make_it_unicode
from soas_rhyme_net_structs import is_unicode
from soas_rhyme_net_structs import safe_open_utf8_file_for_appending
from soas_rhyme_net_structs import get_rhyme_words_for_kmss2015_mirror_inscription
from soas_rhyme_net_structs import grab_last_character_in_line
from pyvis.network import Network
from pyvis.options import EdgeOptions
from annotator_comparison import compare_annotation_between_different_annotators
#import PyQt5
#from PIL import Image
#from PIL.Image import core as _imaging
#import pandas as pd
import networkx as nx
import altair as alt
import altair_viewer as alt_view
#nx_altair is one of many visualization libraries for networkx.
import nx_altair as nxa
import matplotlib.pyplot as plt
from infomap import Infomap
from soas_imported_from_py3 import get_mc_data_for_char
from soas_imported_from_py3 import is_kana_letter
#from anytree import Node, RenderTree, PreOrderIter, AsciiStyle
from soas_tree_structure import get_list_of_fayin_paths
import datetime
# from: https://www.programcreek.com/python/example/89583/networkx.draw_networkx_labels
plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

punctuation = ['。', '、', '；', '{', '}', '*', '＊']
filename_storage = filename_depot() # all paths should be taken from here

# the mirror data has '\r' instead of '\r\n' or '\n'
def readlines_of_utf8_file_for_mirror_data(filename):
    funct_name = 'readlines_of_utf8_file_for_mirror_data()'
    retval = []
    if not os.path.isfile(filename):
        print(funct_name + u' ERROR: filename INVALID: ' + filename)
        return retval
    with open(filename, 'rb') as f:
        line_list = f.readlines()
    line_list[0] = line_list[0].replace(utf8_bom_b, b'')
    for line in line_list:
        line = line.decode('utf8')
        line = line.replace('\r', '\r\n')
        line = line.split('\r\n')
        for l in line:
            retval.append(l)
    return retval

def readin_raw_han_poetry(is_verbose=False):
    funct_name = 'readin_raw_han_poetry()'
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', '3 Han Poetry.csv')
    line_list = readlines_of_utf8_file(input_file)
    label_list = line_list[0].replace('\n','')
    label_list = label_list.split(',')
    line_list = line_list[1:len(line_list)]
    poem_name_list = []
    inc = 0
    for l in line_list:
        l = l.split(',')
        pname = l[0].replace('"','')
        poem_name_list.append(simp2trad(pname))
        if pname != simp2trad(pname) and is_verbose:
            inc += 1
            print('(' + str(inc) + ') ' + pname)
            print('(' + str(inc) + ') ' + simp2trad(pname))
    if is_verbose:
        print(str(len(poem_name_list)) + ' poems in')
        print('\t' + input_file)
        print(', '.join(poem_name_list))
    return poem_name_list

def get_list_poem_names_from_3_han_poetry():
    funct_name = 'get_list_poem_names_from_3_han_poetry()'
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', '3 Han Poetry.csv')
    line_list = readlines_of_utf8_file(input_file)
    label_list = line_list[0].replace('\n','')
    label_list = label_list.split(',')
    line_list = line_list[1:len(line_list)]
    poem_name_list = []
    for l in line_list:
        l = l.split(',')
        poem_name_list.append(l[0].replace('"',''))
    return poem_name_list

arabic2zh_num_dict = {1:'一', 2:'二', 3:'三', 4:'四', 5:'五', 6:'六', 7:'七', 8:'八', 9:'九', 10:'十', 11:'十一', 12:'十二'}
def given_arabic_num_get_chinese_num(arabic_num):
    return arabic2zh_num_dict[arabic_num]

def remove_tags(line, start_tag, stop_tag):
    if not line:
        return line
    line = line.replace(start_tag, '')
    return line.replace(stop_tag, '')

class lu_poem_no_poet_name:
    def __init__(self):
        self.line_return = '\n'
        self.delim = '\t'

    def set_data(self, poem_name, poem_content, poem_large_commentary, juan):
        self.zero_out_data()
        if '〖' in poem_name:
            self.poem_name = poem_name.split('〖')[0].strip()
            self.poem_references = '〖' + poem_name.split('〖')[1]
        else:
            self.poem_name = poem_name.strip()
            self.poem_references = ''
        self.poem_large_commentary = poem_large_commentary.strip()
        self.poem_content = poem_content[:]
        self.juan = juan.strip()
        self.line_return = '\n'
        self.delim = '\t'

    def zero_out_data(self):
        self.poem_name = ''
        self.poem_references = ''
        self.poem_large_commentary = ''
        self.poem_content = []
        self.juan = ''

    def get_poem_sans_references(self):
        pure_poem = []
        for line in self.poem_content:
            if '（' in line:
                pure_poem.append(line.split('（')[0].strip())
            else:
                pure_poem.append(line.strip())
        return pure_poem

    def get_print_msg(self):
        msg = 'Poem Name: ' + self.poem_name + self.line_return
        msg += 'Poem References: ' + self.poem_references + self.line_return
        msg += 'Poem Large Commentary: ' + self.poem_large_commentary + self.line_return
        msg += 'Poem: ' + self.line_return
        msg += '(without references): ' + self.line_return
        pure_poem = self.get_poem_sans_references()
        msg += self.line_return.join(pure_poem)
        msg += self.line_return + '(with references):' + self.line_return
        msg += self.line_return.join(self.poem_content)
        msg += self.line_return + 'From 逯欽立《先秦漢魏晉南北朝詩》：' + self.juan
        return msg

    def print(self):
        if 1:
            print(self.get_print_msg())

    def get_storage_file_msg(self):
        delim = self.delim
        poet_name = '' # keeping this here for compatibility with poems that do have poet information
        poet_intro = ''
        msg = self.poem_name + delim + poet_name + delim + poet_intro + delim + self.poem_references + delim
        #poem_msg = ''
        #for l in self.poem_content:
        #    poem_msg += l
        #if len(self.poem_content) > 1:
        #    x = 1
        msg += self.poem_large_commentary + delim + 'X'.join(self.poem_content)
        return msg

class lu_poem:
    def __init__(self):
        self.line_return = '\n'
        self.delim = '\t'

    def get_poem_name(self):
        return self.poem_name

    def set_data(self, poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, juan):
        self.zero_out_data()
        self.poet_name = poet_name.strip()
        if poet_intro.strip() == '〈〉':
            self.poet_intro = ''
        else:
            self.poet_intro = poet_intro.strip()
        if '〖' in poem_name:
            self.poem_name = poem_name.split('〖')[0].strip()
            self.poem_references = '〖' + poem_name.split('〖')[1].strip()
        else:
            self.poem_name = poem_name.strip()
            self.poem_references = ''
        self.poem_large_commentary = poem_large_commentary.strip()
        self.poem_content = poem_content[:]
        self.juan = juan.strip()
        self.line_return = '\n'
        self.delim = '\t'

    def zero_out_data(self):
        self.poet_name = ''
        self.poet_intro = ''
        self.poem_name = ''
        self.poem_references = ''
        self.poem_large_commentary = ''
        self.poem_content = []
        self.juan = ''

    def get_poem_sans_references(self):
        pure_poem = []
        for line in self.poem_content:
            if '（' in line:
                pure_poem.append(line.split('（')[0].strip())
            else:
                pure_poem.append(line.strip())
        return pure_poem

    def get_print_msg(self):
        msg = 'Poet: ' + self.poet_name + self.line_return
        msg += 'Poet Intro: ' + self.poet_intro + self.line_return
        msg += 'Poem Name: ' + self.poem_name + self.line_return
        msg += 'Poem References: ' + self.poem_references + self.line_return
        msg += 'Poem Large Commentary: ' + self.poem_large_commentary + self.line_return
        msg += 'Poem: ' + self.line_return
        msg += '(without references): ' + self.line_return
        pure_poem = self.get_poem_sans_references()
        msg += self.line_return.join(pure_poem)
        msg += self.line_return + '(with references):' + self.line_return
        msg += self.line_return.join(self.poem_content)
        msg += self.line_return + 'From 逯欽立《先秦漢魏晉南北朝詩》：' + self.juan
        return msg

    def print(self):
        print(self.get_print_msg())

    def get_storage_file_msg(self):
        delim = self.delim
        msg = self.poem_name + delim + self.poet_name + delim + self.poet_intro + delim + self.poem_references + delim
        msg += self.poem_large_commentary + delim + 'X'.join(self.poem_content)
        return msg

#
# This class is a combination of lu_poem (which handles poems that have poet names) and lu_poem_no_poet_name
# (which handles poems that do not have poet names). It makes sense at this point to combine these two.
class lu1983_poem:
    def __init__(self):
        self.line_return = '\n'
        self.delim = '\t'
        self.data_dict = {}
        self.labels = []
        self.unique_id = ''

    def set_data_labels(self, label_line):
        self.labels = label_line.split(self.delim)

    def print_labels(self):
        print(self.delim.join(self.lables))
        #currently: Unique Poem#	Juan.Seq#	Poem Name	Poet's Name	Poet Intro	Poem Refs	Poem Commentary	Poem Content

    def print_poem_content(self):
        poem = self.get_poem_content_as_list()
        for l in poem:
            print(l)

    def get_poem_content_as_str(self):
        return self.line_return.join(self.get_poem_content_as_list())

    def get_poem_content_as_list(self):
        retval = []
        try:
            if self.data_dict['Poem Content'] and self.data_dict['Poem Content'][0] == 'X':
                self.data_dict['Poem Content'] = self.data_dict['Poem Content'][1:len(self.data_dict['Poem Content'])]
            poem = self.data_dict['Poem Content'].replace('X', '\n').split('\n')
            for l in poem:
                retval.append(l.split('（')[0])
                #print(l.split('（')[0])
        except:
            x = 1 # dummy line
        return retval

    def given_label_get_data(self, label):
        retval = ''
        try:
            retval = self.data_dict[label]
        except:
            x = 1
        return retval

    def set_data_with_line_from_file(self, unique_id, line, is_verbose=False):
        if not line.strip():
            return
        self.zero_out_data()
        if is_verbose:
            print(unique_id + self.delim + line)
        self.unique_id = unique_id
        line = unique_id + self.delim + line
        data = line.split(self.delim)
        for inc in range(0, len(self.labels), 1):
            if self.labels[inc] not in self.data_dict:
                self.data_dict[self.labels[inc]] = ''
            if is_verbose:
                print('\tself.data_dict[' + self.labels[inc] + '] = ' + data[inc])
            try:
                self.data_dict[self.labels[inc]] = data[inc]
            except IndexError as ie:
                x = 1

    def zero_out_data(self):
        self.unique_id = ''
        self.data_dict = {}

    def get_poem_id(self):
        return self.unique_id

    def get_poem_sans_references(self):
        pure_poem = []
        for line in self.poem_content:
            if '（' in line:
                pure_poem.append(line.split('（')[0].strip())
            else:
                pure_poem.append(line.strip())
        return pure_poem

    def get_print_msg(self):
        msg = 'Poet: ' + self.poet_name + self.line_return
        msg += 'Poet Intro: ' + self.poet_intro + self.line_return
        msg += 'Poem Name: ' + self.poem_name + self.line_return
        msg += 'Poem References: ' + self.poem_references + self.line_return
        msg += 'Poem Large Commentary: ' + self.poem_large_commentary + self.line_return
        msg += 'Poem: ' + self.line_return
        msg += '(without references): ' + self.line_return
        pure_poem = self.get_poem_sans_references()
        msg += self.line_return.join(pure_poem)
        msg += self.line_return + '(with references):' + self.line_return
        msg += self.line_return.join(self.poem_content)
        msg += self.line_return + 'From 逯欽立《先秦漢魏晉南北朝詩》：' + self.juan
        return msg

    def print(self):
        print(self.get_print_msg())

    def get_storage_file_msg(self):
        delim = self.delim
        msg = self.poem_name + delim + self.poet_name + delim + self.poet_intro + delim + self.poem_references + delim
        msg += self.poem_large_commentary + delim + 'X'.join(self.poem_content)
        return msg

zh2arabic_num_dict = {'十二':12, '十一':11, '十':10, '九':9, '八':8, '七':7, '六':6, '五':5, '四':4, '三':3, '二':2, '一':1}
def get_arabic_num_given_chinese_num(zh_num):
    funct_name = 'get_arabic_num_given_chinese_num()'
    return zh2arabic_num_dict[zh_num]

def test_get_arabic_num_given_chinese_num():
    funct_name = 'test_get_arabic_num_given_chinese_num()'
    print(funct_name + ' Welcome!')
    test_list = ['十二', '十一', '十', '九', '八', '七', '六', '五', '四', '三', '二', '一']
    base = '全漢詩卷'
    for tnum in test_list:
        print('get_arabic_num_given_chinese_num(' + tnum + ') = ' + str(get_arabic_num_given_chinese_num(tnum)))

def get_zh_juan_num_from_juan_tag(juan_tag):
    base ='全漢詩卷'
    return juan_tag.replace(base,'')

def get_arabic_juan_num_from_juan_tag(juan_tag):
    return get_arabic_num_given_chinese_num(get_zh_juan_num_from_juan_tag(juan_tag))

class rolling_n_lines:
    def __init__(self, num_lines, has_poets):
        self.n = num_lines
        self.line_list = []
        self.has_poets = has_poets
        if self.has_poets:
            self.author_list = readin_han_authors_in_lu_1983()
        else:
            self.author_list = []

    # change the code for this function to fit the situation you're testing for
    def is_condition_true(self, line, is_verbose=False):
        retval = False
        self.add_line(line)
        if len(self.line_list) == self.n:
            if '全漢詩卷' in self.line_list[0] or '全漢詩卷' in self.line_list[2]:
                return retval
            if self.has_poets:
                if self.line_list[1] == '':
                    if self.line_list[0] and \
                                    '〖' not in self.line_list[0] and \
                                    '【' not in self.line_list[0] and \
                                    '〈' not in self.line_list[0]:
                        if self.line_list[2] and \
                                        '〖' not in self.line_list[2] and\
                                        '【' not in self.line_list[2] and\
                                        '〈' not in self.line_list[2]:
                            if self.line_list[2].strip() not in self.author_list:
                                retval = True
            else:
                if self.line_list[1] == '':
                    if self.line_list[0] and \
                                    '〖' not in self.line_list[0] and \
                                    '【' not in self.line_list[0]:
                        if self.line_list[2] and \
                                        '〖' not in self.line_list[2] and\
                                        '【' not in self.line_list[2]:
                            if self.line_list[2].strip() not in self.author_list:
                                retval = True
        if is_verbose:
            self.print_lines()
            condition = 'is NOT'
            if retval:
                condition = 'IS'
            print('\tCondition ' + condition + ' met!')
        return retval

    def print_lines(self):
        inc = 0
        for l in self.line_list:
            inc += 1
            print('line_list[' + str(inc) + '] = ' + l)

    def add_line(self, line):
        self.line_list.append(line)
        if len(self.line_list) > self.n:
            self.line_list.pop(0)

def readin_han_authors_in_lu_1983():
    funct_name = 'readin_han_authors_in_lu_1983()'
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'han-authors-in-lu.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    retval = readlines_of_utf8_file(input_file)
    return retval


def test_rolling_n_lines():
    funct_name = 'test_rolling_n_lines()'
    print(funct_name + ' welcomes you!')
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    has_poets = True
    rlines = rolling_n_lines(3, has_poets)
    start_tag = '全漢詩卷七'
    stop_tag = '全漢詩卷八'#'魏詩卷一' # first non-Han section after start of han section
    entered_han_sec = False
    start_cnt = 0
    for l in line_list:
        if start_tag in l:
            start_cnt += 1
            if start_cnt >= 2:
                entered_han_sec = True
        if stop_tag in l:
            entered_han_sec = False
        if entered_han_sec:
            rlines.is_condition_true(l, True)
            print('-'*100)
            x = 1

def parse_raw_lu_1983_for_has_poet_names(is_verbose=False):
    funct_name = 'parse_raw_lu_1983_for_has_poet_names()'
    print('Welcome to ' + funct_name + '!')
    global juan_num2data_dict
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    start_tag = '全漢詩卷一'
    stop_tag = '魏詩卷一' # first non-Han section after start of han section
    num_lines_to_roll = 3
    has_poets = True
    roll_lines = rolling_n_lines(num_lines_to_roll, has_poets)
    LU_poem = lu_poem()
    poet2data_dict = {}
    start_cnt = 0
    han_section = '全漢詩卷'
    entered_han_sec = False
    poet_list = get_list_of_author_names_from_lu_1983()
    current_poet = ''
    poet2juan_dict = {}

    for l in line_list:
        l = l.strip()
        if han_section in l:
            current_juan = l
        if start_tag in l:
            start_cnt += 1
            if start_cnt >= 2:
                entered_han_sec = True
        if stop_tag in l:
            entered_han_sec = False
        if entered_han_sec:
            if not does_juan_contain_poet_names(current_juan): # TEMPORARY
                continue
            for poet in poet_list:
                if l == poet:
                    current_poet = poet
                    if current_poet not in poet2juan_dict:
                        poet2juan_dict[current_poet] = current_juan
                    else:
                        print(current_poet + ' in multiple juan!')
                    if poet not in poet2data_dict:
                        poet2data_dict[poet] = []
                    #print('POET found! ' + poet)
                    break
            if current_poet and l != current_poet:
                if not l.strip():
                    if poet2data_dict[current_poet]:
                        poet2data_dict[current_poet].append(l)
                else:
                    poet2data_dict[current_poet].append(l)

    # lu_poem.set_data(self, poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, juan)
    prev_juan = -1
    seq_num = 0
    for poet in poet2data_dict:
        if is_verbose:
            print('POET: ' + poet)
        poet_intro = ''
        for l in poet2data_dict[poet]:
            if '〈' in l:
                poet_intro = l
                break
        poet_data = '\n'.join(poet2data_dict[poet])
        poet_data = poet_data.replace(poet_intro + '\n\n','')
        if is_verbose:
            print(poet_data)
        poet_data = poet_data.split('【')
        juan = poet2juan_dict[poet]
        juan_num = get_arabic_juan_num_from_juan_tag(juan)
        if juan_num != prev_juan:
            prev_juan = juan_num
            seq_num = 0
        if poet_data[0] == '':
            poet_data = poet_data[1:len(poet_data)]
        for pline in poet_data:
            poem_name = '【' + pline.split('\n')[0]
            if is_verbose:
                print('POEM_NAME = ' + poem_name)
            pline = '【' + pline
            pline = pline.replace(poem_name + '\n', '')
            if not pline.strip():
                continue
            if '〗' in pline:
                poem_large_commentary = pline.split('〗')[0].strip() + '〗'
                if is_verbose:
                    print('POEM_LARGE_COMMENTARY = ' + poem_large_commentary)
                pline = pline.replace(poem_large_commentary + '\n','').lstrip()
            else:
                poem_large_commentary = ''
            poem_content = pline.strip()
            if han_section in pline:
                x = 1
            poem_content = poem_content.split('\n')
            line2remove = ''
            for pl in poem_content:
                if han_section in pl:
                    line2remove = pl
            if line2remove:
                poem_content.remove(line2remove)
                if poem_content[len(poem_content)-1] == '':
                    poem_content.pop() # remove last item
            #def set_data(self, poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, juan)
            LU_poem.set_data(poet, poet_intro, poem_name, poem_large_commentary, poem_content, juan)
            seq_num += 1
            #LU_poem.set_data(poet, poet_intro, poem_name, poem_large_commentary, poem_content, juan)
            print(LU_poem.get_print_msg())
            print('-*'*50)
            if is_verbose:
                print('POEM_CONTENT = ' + '\n'.join(poem_content))

            if juan_num not in juan_num2data_dict:
                juan_num2data_dict[juan_num] = {}
            if seq_num not in juan_num2data_dict[juan_num]:
                juan_num2data_dict[juan_num][seq_num] = ''
            pmsg = LU_poem.get_storage_file_msg()
            print('juan_num2data_dict[' + str(juan_num) + '][' + str(seq_num) + '] = ' + pmsg)
            juan_num2data_dict[juan_num][seq_num] = pmsg
    print(str(len(poet2data_dict.keys())) + ' poets found.')

juan_num2data_dict = {}
def parse_han_data_from_lu_1983_form_poems_with_poet_names(is_verbose=False):
    funct_name = 'parse_han_data_from_lu_1983_form_poems_with_poet_names()'
    print('Welcome to ' + funct_name + '!')
    global juan_num2data_dict
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    han_section = '全漢詩卷'
    start_tag = '全漢詩卷一'
    stop_tag = '魏詩卷一' # first non-Han section after start of han section
    entered_han_sec = False
    prev_line = ''
    raw_prev_line = ''
    raw_l = ''
    poem_name_list = []
    poet_list = []
    start_cnt = 0
    current_juan = ''
    new_item = False
    has_poets = True
    rlines = rolling_n_lines(3, has_poets)
    LU_poem = lu_poem()
    author_cnt = 0
    current_poet = ''
    prev_poet_name = ''
    prev_poem_name = ''
    poet_intro = ''
    poem_large_commentary = ''
    poet_name = ''
    poem_name = ''
    poem_commentary = ''
    poem_content = []
    prev_line_raw = ''
    seq_num = 0
    add_stanza_break = False
    outer_prev_line = ''
    print_rolling = False
    lu_test = False
    for l in line_list:
        if entered_han_sec:
            if rlines.is_condition_true(outer_prev_line, print_rolling):
                add_stanza_break = True
        if not l.strip():
            outer_prev_line = l
            continue
        if start_tag in l:
            start_cnt += 1
            if start_cnt >= 2:
                entered_han_sec = True
        if stop_tag in l:
            entered_han_sec = False
            if poet_name and poem_name:
                if not poem_content:
                    poem_content.append(raw_l.strip())
                    add_stanza_break = False
                LU_poem.set_data(poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, current_juan)
                if lu_test:
                    print(LU_poem.get_print_msg())
                seq_num += 1
                juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                #
                # zero out data
                poem_name = ''
                poem_large_commentary = ''
                poem_content = []

                if is_verbose:
                    print('POEM Sequence number: ' + str(juan_num) + '.' + str(seq_num))
                pmsg = LU_poem.get_storage_file_msg()
                if is_verbose:
                    print(pmsg)
                if juan_num not in juan_num2data_dict:
                    juan_num2data_dict[juan_num] = {}
                if seq_num not in juan_num2data_dict[juan_num]:
                    juan_num2data_dict[juan_num][seq_num] = ''
                juan_num2data_dict[juan_num][seq_num] = pmsg
        if entered_han_sec and han_section in l: # entering new juan - 'han_sec' => han dynasty section of the book
            if prev_line_raw:
                if add_stanza_break:
                    poem_content.append('')
                    add_stanza_break = False
                poem_content.append(prev_line_raw.strip())
            #
            # Process last poem from previous JUAN
            if poet_name and poem_name and poem_content:
                LU_poem.set_data(poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, current_juan)
                if lu_test:
                    print(LU_poem.get_print_msg())
                seq_num += 1
                poem_large_commentary = ''
                poem_name = ''
                poem_content = []
                prev_line_raw = ''
                prev_line = ''

                juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                pmsg = LU_poem.get_storage_file_msg()
                if juan_num not in juan_num2data_dict:
                    juan_num2data_dict[juan_num] = {}
                if seq_num not in juan_num2data_dict[juan_num]:
                    juan_num2data_dict[juan_num][seq_num] = ''
                juan_num2data_dict[juan_num][seq_num] = pmsg

            current_juan = l.strip()
            seq_num = 0 # this number resets with each juan
            if add_stanza_break:
                poem_content.append('')
                add_stanza_break = False
            poem_content.append(prev_line_raw.strip())
            if is_verbose:
                print(l)
            outer_prev_line = l
            continue
        if entered_han_sec:
            if not does_juan_contain_poet_names(current_juan): # TEMPORARY
                continue
            if not l.strip():
                outer_prev_line = ''
                continue # don't need to process blank lines, unless it's a line separating stanzas
            raw_l = l.strip()
            l = remove_comment_from_line(l)
            l = remove_references_from_line(l)
            if raw_l and raw_l.strip()[0] == '〖': # if this is a large commentary line
                poem_large_commentary = raw_l
                if is_verbose:
                    print('POEM LARGE COMMENTARY: ' + poem_large_commentary)
            if l.strip():
                if '〈' in l: # if '〈' in this line, then the previous line is a poet's name,
                              #    so, all of the data from the previous poem has been put into variables
                    # assign data to poem object
                    if poet_name and poem_name and poem_content:
                        LU_poem.set_data(poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, current_juan)
                        if lu_test:
                            print(LU_poem.get_print_msg())
                        seq_num += 1
                        poem_large_commentary = ''
                        poem_name = ''
                        poem_content = []
                        prev_line_raw = ''
                        prev_line = ''

                        juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                        if is_verbose:
                            print('POEM Sequence number: ' + str(juan_num) + '.' + str(seq_num))
                        pmsg = LU_poem.get_storage_file_msg()
                        if juan_num not in juan_num2data_dict:
                            juan_num2data_dict[juan_num] = {}
                        if seq_num not in juan_num2data_dict[juan_num]:
                            juan_num2data_dict[juan_num][seq_num] = ''
                        juan_num2data_dict[juan_num][seq_num] = pmsg
                        poem_large_commentary = ''
                        poem_content = []
                        if is_verbose:
                            print('*-'*100)
                    # process data for next poem object
                    prev_poet_name = poet_name
                    poet_name = prev_line
                    current_poet = poet_name
                    if is_verbose:
                        print('POET: ' + poet_name)
                    poet_list.append(poet_name.strip())
                    poet_intro = l
                    author_cnt += 1
                elif l and '【' == l[0]:
                    if '〈' not in prev_line and '【' not in prev_line and '〖' not in prev_line:
                        if add_stanza_break:
                            poem_content.append('')
                            add_stanza_break = False
                        poem_content.append(prev_line_raw.strip())

                        if is_verbose:
                            print('POEM CONTENT: ' + prev_line)
                    prev_line = l.strip()
                    prev_line_raw = raw_l
                    outer_prev_line = l
                    continue
                elif l and '〖' == l[0] and '【' == prev_line.strip()[0]: # new poem
                    #
                    # take care of previous poem data
                    if poet_name and poem_name and poem_content:
                        LU_poem.set_data(poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, current_juan)
                        if lu_test:
                            print(LU_poem.get_print_msg())
                        seq_num += 1
                        poem_name = ''
                        poem_large_commentary = ''
                        poem_content = []
                        juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                        if is_verbose:
                            print('POEM Sequence number: ' + str(juan_num) + '.' + str(seq_num))
                        pmsg = LU_poem.get_storage_file_msg()
                        if juan_num not in juan_num2data_dict:
                            juan_num2data_dict[juan_num] = {}
                        if seq_num not in juan_num2data_dict[juan_num]:
                            juan_num2data_dict[juan_num][seq_num] = ''
                        juan_num2data_dict[juan_num][seq_num] = pmsg
                        poem_large_commentary = ''
                        poem_content = []
                        if is_verbose:
                            print('*-'*100)
                    #
                    # process current poem name
                    prev_poem_name = poem_name
                    poem_name = prev_line_raw
                    if is_verbose:
                        print('POEM NAME: ' + poem_name)
                    poem_name_list.append(remove_tags(prev_line, '【', '】'))
                elif prev_line and l and '【' == prev_line.strip()[0] and '〖' != l[0]: # new poem
                    #
                    # handle previous poem
                    if poet_name and poem_name and poem_content:
                        LU_poem.set_data(poet_name, poet_intro, poem_name, poem_large_commentary, poem_content, current_juan)
                        if lu_test:
                            print(LU_poem.get_print_msg())
                        seq_num += 1
                        poem_name = ''
                        poem_large_commentary = ''
                        poem_content = []
                        juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                        if is_verbose:
                            print('POEM Sequence number: ' + str(juan_num) + '.' + str(seq_num))
                        pmsg = LU_poem.get_storage_file_msg()
                        if juan_num not in juan_num2data_dict:
                            juan_num2data_dict[juan_num] = {}
                        if seq_num not in juan_num2data_dict[juan_num]:
                            juan_num2data_dict[juan_num][seq_num] = ''
                        juan_num2data_dict[juan_num][seq_num] = pmsg
                        poem_large_commentary = ''
                        poem_content = []
                        if is_verbose:
                            print('*-'*100)
                    #
                    # handle current poem
                    prev_poem_name = poem_name
                    poem_name = prev_line_raw
                    if is_verbose:
                        print('POEM NAME: ' + poem_name)
                    #inside_poem = False
                    poem_name_list.append(remove_tags(prev_line, '【', '】'))
                elif prev_line:# and '〈' not in prev_line:
                    if add_stanza_break:
                        poem_content.append('')
                        add_stanza_break = False
                    poem_content.append(prev_line_raw.strip())
                    #inside_poem = True
                    if is_verbose:
                        print('POEM CONTENT: ' + prev_line)
                prev_line = l.strip()
                prev_line_raw = raw_l.strip()
                outer_prev_line = l
    if is_verbose:
        print('POEM CONTENT: ' + prev_line)
    if is_verbose:
        print(str(len(poem_name_list)) + ' number of poem names (' + str(len(set(poem_name_list))) + ' unique).')
        print(str(len(poet_list)) + ' number of poets (' + str(len(list(set(poet_list)))) + ' unique).')
    return poem_name_list

def parse_han_data_from_lu_1983_form_poems_without_poet_names(is_verbose=False):
    funct_name = 'parse_han_data_from_lu_1983_form_poems_without_poet_names()'
    print('Welcome to ' + funct_name + '!')
    global juan_num2data_dict
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    han_section = '全漢詩卷'
    start_tag = '全漢詩卷三'
    stop_tag = '魏詩卷一' # first non-Han section after start of han section
    entered_han_sec = False
    prev_line = ''
    raw_prev_line = ''
    raw_l = ''
    poem_name_list = []
    poet_list = []
    start_cnt = 0
    current_juan = ''
    #new_item = False

    LU_poem = lu_poem_no_poet_name()
    author_cnt = 0
    current_poet = ''
    prev_poem_name = ''
    poem_commentary = ''
    poem_large_commentary = ''
    poem_name = ''
    poem_content = []
    prev_line_raw = ''
    has_poets = False
    outer_prev_line = ''
    print_rolling = False
    seq_num = 0
    n = 3
    rlines = rolling_n_lines(n, print_rolling)
    add_stanza_break = False
    for l in line_list:
        if entered_han_sec:
            if rlines.is_condition_true(outer_prev_line, print_rolling):
                add_stanza_break = True
        if not l.strip():
            outer_prev_line = l
            continue
        if start_tag in l:
            start_cnt += 1
            if start_cnt >= 2:
                entered_han_sec = True
        if stop_tag in l:
            entered_han_sec = False
            if poem_name:
                if not poem_content:
                    if raw_l.strip()[0] == '〖':
                        x = 1
                    if add_stanza_break:
                        poem_content.append('')
                        add_stanza_break = False
                    poem_content.append(raw_l.strip())
                LU_poem.set_data(poem_name, poem_content, poem_large_commentary, current_juan)
                seq_num += 1
                juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                if juan_num not in juan_num2data_dict:
                    juan_num2data_dict[juan_num] = {}
                if seq_num not in juan_num2data_dict[juan_num]:
                    juan_num2data_dict[juan_num][seq_num] = ''
                juan_num2data_dict[juan_num][seq_num] = LU_poem.get_storage_file_msg()
        if entered_han_sec and han_section in l: # entering new juan
            if prev_line_raw:
                if add_stanza_break:
                    poem_content.append('')
                    add_stanza_break = False
                poem_content.append(prev_line_raw.strip())
            #
            # Process last poem from previous JUAN
            if poem_name and poem_content:
                LU_poem.set_data(poem_name, poem_content, poem_large_commentary, current_juan)
                seq_num += 1
                juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                #LU_poem.print()
                #file_seq_num = str(juan_num) + '.' + str(seq_num)
                if juan_num not in juan_num2data_dict:
                    juan_num2data_dict[juan_num] = {}
                if seq_num not in juan_num2data_dict[juan_num]:
                    juan_num2data_dict[juan_num][seq_num] = ''
                juan_num2data_dict[juan_num][seq_num] = LU_poem.get_storage_file_msg()
                #
            # Entering a new JUAN: clear out variables
            current_juan = l.strip()
            seq_num = 0
            prev_poem_name = ''
            poem_commentary = ''
            poem_name = ''
            poem_content = []
            prev_line_raw = ''
            prev_line = ''
            if is_verbose:
                print(l)
            outer_prev_line = l
            continue
        if entered_han_sec:
            if does_juan_contain_poet_names(current_juan):
                continue
            if not l.strip():
                outer_prev_line = ''
                continue # don't need to process blank lines, unless it's a line separating stanzas
            raw_l = l.strip()
            l = remove_references_from_line(l)
            if l.strip():
                if '【' == l[0]:
                    if '【' not in prev_line and '〖' not in prev_line:
                        if prev_line.strip() and prev_line.strip()[0] == '〖':
                            if is_verbose:
                                print('POEM LARGE COMMENTARY: ' + prev_line)
                            poem_large_commentary = prev_line
                        elif prev_line.strip():
                            if is_verbose:
                                print('POEM CONTENT: ' + prev_line)
                            if add_stanza_break:
                                poem_content.append('')
                                add_stanza_break = False
                            poem_content.append(prev_line_raw.strip())
                    prev_line = l.strip()
                    outer_prev_line = l
                    prev_line_raw = raw_l
                    continue
                elif '〖' == l.strip()[0] and '【' == prev_line.strip()[0]: # new poem
                    #
                    # take care of previous poem data
                    if poem_name and poem_content:
                        LU_poem.set_data(poem_name, poem_content, poem_large_commentary, current_juan)
                        seq_num += 1
                        juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                        if juan_num not in juan_num2data_dict:
                            juan_num2data_dict[juan_num] = {}
                        if seq_num not in juan_num2data_dict[juan_num]:
                            juan_num2data_dict[juan_num][seq_num] = ''
                        juan_num2data_dict[juan_num][seq_num] = LU_poem.get_storage_file_msg()
                        #LU_poem.print()
                        poem_large_commentary = ''
                        poem_content = []
                        if is_verbose:
                            print('*-'*100)
                    #
                    # process current poem name
                    prev_poem_name = poem_name
                    poem_name = prev_line_raw
                    if is_verbose:
                        if poem_name.strip():
                            print('POEM NAME: ' + poem_name)
                    poem_name_list.append(remove_tags(prev_line, '【', '】'))
                elif prev_line and '【' == prev_line.strip()[0] and '〖' != l[0]: # new poem
                    #
                    # handle previous poem
                    if poem_name and poem_content:
                        LU_poem.set_data(poem_name, poem_content, poem_large_commentary, current_juan)
                        seq_num += 1
                        juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                        if juan_num not in juan_num2data_dict:
                            juan_num2data_dict[juan_num] = {}
                        if seq_num not in juan_num2data_dict[juan_num]:
                            juan_num2data_dict[juan_num][seq_num] = ''
                        juan_num2data_dict[juan_num][seq_num] = LU_poem.get_storage_file_msg()
                        poem_large_commentary = ''
                        poem_content = []
                        if is_verbose:
                            print('*-'*100)
                    #
                    # handle current poem
                    prev_poem_name = poem_name
                    poem_name = prev_line_raw
                    if is_verbose:
                        if poem_name.strip():
                            print('POEM NAME: ' + poem_name)
                    poem_name_list.append(remove_tags(prev_line, '【', '】'))
                elif l[0] != '〖' and l.strip()[0] == '〖': #only happens for large poem commentary
                    poem_large_commentary = l.strip()
                    if poem_large_commentary.strip():
                        if is_verbose:
                            print('POEM LARGE COMMENTARY: ' + poem_large_commentary)
                elif prev_line:# and '〈' not in prev_line:
                    prev_line = prev_line.strip()
                    if prev_line and prev_line[0] == '〖':
                        poem_large_commentary = prev_line
                        if is_verbose:
                            print('POEM LARGE COMMENTARY:' + prev_line)
                    elif prev_line:
                        if add_stanza_break:
                            poem_content.append('')
                            add_stanza_break = False
                        poem_content.append(prev_line.strip())
                        if is_verbose:
                            print('POEM CONTENT: ' + prev_line)
                prev_line = l.strip()
                outer_prev_line = l
                prev_line_raw = raw_l.strip()
    if is_verbose:
        print('POEM CONTENT: ' + prev_line)
    if is_verbose:
        print(str(len(poem_name_list)) + ' number of poem names (' + str(len(set(poem_name_list))) + ' unique).')
        print(str(len(poet_list)) + ' number of poets (' + str(len(list(set(poet_list)))) + ' unique).')
    return poem_name_list

juan_w_poet_name = [1, 2, 5, 6, 7]
def does_juan_contain_poet_names(juan):
    retval = False
    juan = juan.replace('全漢詩卷', '').strip()
    num = zh2arabic_num_dict[juan]
    if num in juan_w_poet_name:
        retval = True
    return retval

class recent_lines:
    def __init__(self, max_num_lines):
        self.line_list = []
        self.max_num_lines = max_num_lines
    def add_line(self, line2add):
        self.line_list.append(line2add)
        if len(self.line_list) > self.max_num_lines:
            self.line_list.pop(0)

def get_list_of_poem_names_from_lu_1983_2():
    funct_name = 'get_list_of_poem_names_from_lu_1983_2()'
    print('Welcome!')
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    juan = '卷'
    han_section = '全漢詩卷'
    start_tag = '全漢詩卷一'
    stop_tag = '魏詩卷一' # first non-Han section after start of han section
    entered_han_sec = False
    start_looking_tag = '我國自秦漢迄于隋末'
    start_looking = False
    test_char = '【'
    prev_line_has_test_char = False
    double_cnt = 0
    prev_line = ''
    printed_current_line = False
    for l in line_list:
        if not l.strip():
            continue
        if start_looking_tag in l:
            start_looking = True
        if not start_looking:
            continue
        if start_tag in l:
            entered_han_sec = True
        if stop_tag in l:
            entered_han_sec = False
        if han_section in l:
            continue
        if entered_han_sec:
            l = l.strip()
            if not l:
                continue # don't need to process blank lines

            if '【' in l:
                print(l)
                prev_line = l
            if '〖' == l[0] and '【' in prev_line.strip()[0]:
                print(prev_line.strip())

def get_list_of_author_names_from_lu_1983(is_verbose=False):
    funct_name = 'get_list_of_author_names_from_lu_1983()'
    print('Welcome!')
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'raw', 'han-authors-in-lu.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    poet_list = []
    removed_cnt = 0
    for poet in line_list:
        poet = remove_part_of_line(poet, '#')
        if not poet.strip():
            removed_cnt += 1
            continue
        if is_verbose:
            print(poet)
        poet_list.append(poet)
    if is_verbose:
        print(str(len(poet_list)) + ' poets (' + str(removed_cnt) + ' lines removed).')
    return poet_list

def remove_part_of_line(line, start_tag):
    if start_tag not in line:
        return line
    comment = line.split(start_tag)
    try:
        comment = start_tag + comment[1]
    except IndexError as ie:
        x = 1
    return line.replace(comment, '')

def remove_references_from_line(line):
    return remove_part_of_line(line, '（')

def remove_comment_from_line(line):
    return remove_part_of_line(line, '〖')

vessel_categories = ['饪食器铭文', '酒器铭文', '水器铭文', '乐器铭文', '兵器铭文', '度量衡器铭文', '车马器具', '杂器铭文', '钱币铭文', '铅券', '镇墓文']
type_dict = {'饪食器铭文':False,
             '酒器铭文':False,
             '水器铭文':False,
             '乐器铭文':False,
             '兵器铭文':False,
             '度量衡器铭文':False,
             '车马器具':False,
             '杂器铭文':False,
             '钱币铭文':False,
             '铅券':False,
             '镇墓文':False}

def clean_up_mou_n_zhong_2016_data():
    funct_name = 'clean_up_mou_n_zhong_2016_data()'
    readin_bronze_type_dict()
    max_bronze_name_size = 8
    min_bronze_name_size = 2
    bronze_dir = filename_storage.get_received_bronzes_dir()
    input_file = os.path.join(bronze_dir, 'raw', 'Abbyy', ' Mou H and Zhong G 2016 漢金文輯校.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid file:' + input_file)
        return
    cat_dict = {'饪食器铭文': False,
                 '酒器铭文': False,
                 '水器铭文': False,
                 '乐器铭文': False,
                 '兵器铭文': False,
                 '度量衡器铭文': False,
                 '车马器具': False,
                 '杂器铭文': False,
                 '钱币铭文': False,
                 '铅券': False,
                 '镇墓文': False}

    line_list = readlines_of_utf8_file(input_file)
    stop_here = '主要参考文献'
    start_here = '饪食器铭文'
    started = False
    current_category = '饪食器铭文'
    current_type = ''
    next_type = ''
    prev_line = ''
    name_list = []
    num_current_type = 0
    cat2type2cnt_dict = {}
    cat2type2data_dict = {}
    for l in line_list:
        if stop_here in l:
            break
        elif not started:
            if start_here == l:
                started = True
        if started:
            # if there are any vessel_categories in this line...
            #x = btype_dict[current_category]
            if any(v_cat == l for v_cat in vessel_categories):
                current_category = l.strip()
                current_type = ''
                print('CATEGORY: ' + current_category)
                if current_category not in cat2type2cnt_dict:
                    cat2type2cnt_dict[current_category] = {}
                if current_category not in cat2type2data_dict:
                    cat2type2data_dict[current_category] = {}

                if not cat_dict[current_category]:
                    cat_dict[current_category] = True
            elif current_category != '车马器具' and l in btype_dict[current_category]:
                current_type = l
                if current_type not in cat2type2cnt_dict[current_category]:
                    cat2type2cnt_dict[current_category][current_type] = 0
                if current_type not in cat2type2data_dict[current_category]:
                    cat2type2data_dict[current_category][current_type] = []
                print('TYPE: ' + l)
            else:
                if current_category == '车马器具':
                    break
                # if this fits the basic description of a bronze name (but may not be)
                bronze_name = l.strip()
                # NOTE: Use 'l' for testing, use name for printing/storing
                if '（' in l:
                    l = l.split('（')[0].strip()
                if len(l.strip()) <= max_bronze_name_size and len(l.strip()) >= min_bronze_name_size:
                    if l[1] == '）' or l == '-鉴' or l[0] == '(' or l == '三）' or l == '下）' or l == '\\': # this is a special case
                        continue
                    if l.strip().isdigit() or not l.strip() or '。' in l or l[0] == '〈':  # single numbers are page numbers
                        prev_line = l
                        continue
                    #
                    # TO DO:
                    #  - need to test each line to see if it's a bronze name
                    #    Use the btype_dict
                    if current_type in bronze_name: # this only works pre-铜轸（补）
                        try:
                            cat2type2data_dict[current_category][current_type].append(bronze_name)
                        except KeyError as ke:
                            x = 1
                        print(bronze_name)
                        try:
                            cat2type2cnt_dict[current_category][current_type] += 1
                        except KeyError as ke:
                            x = 1
    category = '饪食器铭文'
    btype = '鼎'
    print('for category = ' + category)
    for bronze_name in cat2type2data_dict[category][btype]:
        print(bronze_name)
    print(str(len(cat2type2data_dict[category][btype])) + ' bronze names.')

btype_dict = {}
def readin_bronze_type_dict(verbose=False):
    funct_name = 'readin_bronze_type_dict()'
    global btype_dict
    if btype_dict:
        return
    bronzes_dir = filename_storage.get_received_bronzes_dir()
    input_file = os.path.join(bronzes_dir, 'raw', 'Abbyy', 'indexing-data.txt')
    line_list = readlines_of_utf8_file(input_file)
    bronze_category_pos = 0
    bronze_type_pos = 1
    for l in line_list:
        if not l.strip():
            continue
        l = l.split('\t')
        if l[bronze_category_pos] not in btype_dict:
            btype_dict[l[bronze_category_pos]] = []
        try:
            btype_dict[l[bronze_category_pos]].append(l[bronze_type_pos])
        except IndexError as ie:
            x = 1
    if verbose:
        for k in btype_dict:
            print('btype_dict[' + k + '] = ' + ', '.join(btype_dict[k]))


#NOTE: the sinopy.gbk2big5() does not convert between the gbk and big5 encodings. It converts utf8 trad characters to utf8 simp characters
def simp2trad(simp):
    return sinopy.gbk2big5(simp)# NOTE: 'gbk' = SIMP. It is not related to encoding; big5 = TRAD. It is not related to encoding.

#NOTE: the sinopy.big52gbk() does not convert between the big5 and gbk encodings. It converts utf8 simp characters to utf8 trad characters
def trad2simp(trad):
    return sinopy.big52gbk(trad)# NOTE: 'gbk' = SIMP. It is not related to encoding; big5 = TRAD. It is not related to encoding.

def test_trad_to_simp_conversion_and_vice_verse():
    funct_name = 'test_trad_to_simp_conversion_and_vice_verse()'
    print(funct_name + ' Welcome!')
    simp = '你的话是这样'
    trad = '你的話是這樣'
    print('trad2simp(' + trad + ') = ' + trad2simp(trad))
    print('simp2trad(' + simp + ') = ' + simp2trad(simp))

def compare_poem_names_between_lu_1983_and_raw_han_csv_dumbly():
    funct_name = 'compare_poem_names_between_lu_1983_and_raw_han_csv_dumbly()'
    print(funct_name + ' welcome!')
    lu_poem_names = parse_han_data_from_lu_1983()
    raw_han_names = readin_raw_han_poetry()

def compare_poem_names_between_lu_1983_and_raw_han_csv():
    funct_name = 'compare_poem_names_between_lu_1983_and_raw_han_csv()'
    print(funct_name + ' welcome!')
    lu_poem_names = parse_han_data_from_lu_1983()
    raw_han_names = readin_raw_han_poetry()
    intersec = get_the_intersection_of_two_lists(lu_poem_names, raw_han_names)
    diff = get_the_difference_of_two_lists(lu_poem_names, raw_han_names)
    print(str(len(lu_poem_names)) + ' poems from 逯欽立 1983 (' + str(len(set(lu_poem_names))) + ' unique).')
    print(str(len(raw_han_names)) + ' poems from the \'raw han\' csv file (' + str(len(set(raw_han_names))) + ' unique).')
    print(str(len(intersec)) + ' poems between the two lists are the same.')
    print(str(len(diff)) + ' poems are different between the two lists.')
    lu_short = get_the_elements_in_a_that_are_not_in_b(lu_poem_names, raw_han_names)
    raw_han_short = get_the_elements_in_a_that_are_not_in_b(raw_han_names, lu_poem_names)
    #lu_short = list(numpy.array(lu_poem_names) - numpy.array(intersec)) # lu_short = lu_poem_names minus the poems
                                                                        #   common with the raw_han_names data set.
    print(str(len(lu_short)) + ' poems in lu_short.')
    print(str(len(raw_han_short)) + ' poems in raw_han_short.')
    print('-*'*50)
    print('For each poem name in the Raw Han short list, calculate it\'s correlation to the Lu data short list.')
    print('\tPrinting out values for ratios over 0.5:')
    for rh in raw_han_short:
        for ls in lu_short:
            r = cydifflib.SequenceMatcher(None, rh, ls).ratio()
            if r > 0.49999999:
                print('(ratio: ' + str(r) + ') raw han: ' + rh + '<-> Lu:' + ls)

def get_the_intersection_of_two_lists(list_a, list_b):
    retval = []
    if len(list_a) >= len(list_b): # If list_a is longer or the same...
        set_a = set(list_a)
        retval = list(set_a.intersection(set(list_b)))
    else:
        set_b = set(list_b)
        retval = list(set_b.intersection(set(list_a)))
    return retval

def get_the_difference_of_two_lists(list_a, list_b):
    retval = []
    if len(list_a) >= len(list_b): # If list_a is longer or the same...
        set_a = set(list_a)
        retval = list(set_a.symmetric_difference(set(list_b)))
    else:
        set_b = set(list_b)
        retval = list(set_b.symmetric_difference(set(list_a)))
    return retval
def get_the_elements_in_a_that_are_not_in_b(list_a, list_b):
    return list(set(list_a).difference(set(list_b)))

def test_get_the_intersection_of_two_lists():
    funct_name = 'test_get_the_intersection_of_two_lists()'
    list_b = ['a', 'a', 'a', 'b', 'd']
    list_a = ['b', 'b', 'e']
    results = get_the_intersection_of_two_lists(list_a, list_b)
    print('List_a = ' + ', '.join(list_a))
    print('List_b = ' + ', '.join(list_b))
    print('Intersection = ' + ', '.join(results))

def test_get_the_difference_of_two_lists():
    funct_name = 'test_get_the_difference_of_two_lists()'
    list_a = ['a', 'a', 'a', 'b', 'd']
    list_b = ['b', 'b', 'e']
    results = get_the_difference_of_two_lists(list_a, list_b)
    print('List_a = ' + ', '.join(list_a))
    print('List_b = ' + ', '.join(list_b))
    print('Difference = ' + ', '.join(results))
    print('(Here, \'difference\' = the members of the longer set that are not in the shorter set)')

# purpose:
#   trying to find functions that show the correlation ratio between two strings
def cydifflib_test():
    funct_name = 'cydifflib_test()'
    print(funct_name + ' hello!')
    str_a = '羽林郎詩'
    str_b = '羽林郎诗'
    str_c = '羽林郎詩二'
    x = cydifflib.SequenceMatcher(None, str_a, str_b).ratio()
    x2 = cydifflib.SequenceMatcher(None, str_a, str_a).ratio()
    x3 = cydifflib.SequenceMatcher(None, str_a, str_c).ratio()
    x4 = cydifflib.SequenceMatcher(None, str_b, str_c).ratio()
    print('SequenceMatcher(' + str_a + ', ' + str_b + ').ratio() = ' + str(x))
    print('SequenceMatcher(' + str_a + ', ' + str_a + ').ratio() = ' + str(x2))
    print('SequenceMatcher(' + str_a + ', ' + str_c + ').ratio() = ' + str(x3))
    print('SequenceMatcher(' + str_b + ', ' + str_c + ').ratio() = ' + str(x4))

#
# Lu1983 has data from eras other than the Han
# This function only gets the Han era data
def parse_han_data_from_lu_1983():
    funct_name = 'parse_han_data_from_lu_1983()'
    is_verbose = False
    delim = '\t'
    line_return ='\n'
    output_file = os.path.join(filename_storage.get_received_shi_dir(), 'parsed-Lu-1983-先秦漢魏晉南北朝詩.txt')
    # if output file already exists, delete it
    if os.path.isfile(output_file):
        os.remove(output_file)
    # add labels to the output file
    label_list = ['Unique Poem#', 'Juan.Seq#', 'Poem Name', 'Poet\'s Name', 'Poet Intro', 'Poem Refs',
                  'Poem Commentary', 'Poem Content']
    append_line_to_output_file(output_file, delim.join(label_list) + line_return)
    parse_raw_lu_1983_for_has_poet_names(is_verbose)
    parse_han_data_from_lu_1983_form_poems_without_poet_names(is_verbose)
    print(delim.join(label_list))
    num_poems = 0
    for jnum in range(1, 12+1, 1):
        for snum in range(1, len(juan_num2data_dict[jnum])+1, 1):
            num_poems += 1
            #x = juan_num2data_dict[jnum][snum]
            line = 'Lu1983.' + f"{num_poems:03}" + delim + str(jnum) + '.' + str(snum) + delim + juan_num2data_dict[jnum][snum]
            print(line)
            append_line_to_output_file(output_file, line)
    print(str(num_poems) + ' poems processed.')

lu1983_dict = {}
lu1983_labels = []
#
# Purpose:
#   -read in Lu 1983 data from pre-processed file
#   -put data into a dictionary where:
#     key = poem's unique ID
#     value = poem
#   -the dictionary is global, and is called 'lu1983_dict'
def readin_lu_1983_data(is_verbose=False):
    funct_name = 'readin_lu_1983_data()'
    global lu1983_dict
    global lu1983_labels
    #if lu1983_dict:
    #    return lu1983_dict # was lu1983_labels
    input_file = os.path.join(filename_storage.get_received_shi_dir(), 'parsed-Lu-1983-先秦漢魏晉南北朝詩.txt')
    if not is_file_valid(input_file, funct_name):
        return []
    uniqid2poem_dict = {}
    line_list = readlines_of_utf8_file(input_file)
    lu1983_labels = line_list[0][:]
    LU_poem = lu1983_poem()
    LU_poem.set_data_labels(lu1983_labels)
    uniqid2poem_dict = {}

    line_list = line_list[1:len(line_list)]
    for l in line_list:
        if is_verbose:
            print(l)
        l = l.split('\t')
        unique_id = l[0]
        l = l[1:len(l)]
        lu1983_dict[unique_id] = '\t'.join(l)
        LU_poem.set_data_with_line_from_file(unique_id, lu1983_dict[unique_id])
        if unique_id not in uniqid2poem_dict:
            uniqid2poem_dict[unique_id] = ''
        uniqid2poem_dict[unique_id] = deepcopy(LU_poem)
    return uniqid2poem_dict

def is_file_valid(file, calling_function):
    retval = False
    is_verbose = True
    if not os.path.isfile(file):
        message2user(calling_function + ' ERROR: Input file INVALID! ', is_verbose)
        message2user('\t' + file, is_verbose)
    else:
        retval = True
    return retval

schuessler = ''

def explore_rhyme_structure_of_han_dynasty_poems():
    funct_name = 'explore_rhyme_structure_of_han_dynasty_poems()'
    schuessler = sch_glyph2phonology()
    readin_lu_1983_data()
    lu_poem = lu1983_poem()
    lu_poem.set_data_labels(lu1983_labels)
    uniqid2poem_dict = {}
    test_poem = ['橘柚垂華實。乃在深山側。聞君好我甘。竅獨自雕飾。委身玉盤中。歷年冀見食。芳菲不相投。青黃忽改色。人儻欲我知。因君為羽翼。',
                 '十五從軍征。八十始得歸。道逢鄉里人。家中有阿誰。遙望是君家。松柏冢累累。兔從狗竇入。雉從樑上飛。中庭生旅谷。井上生旅葵。\
                 烹谷持作飯。采葵持作羹。羹飯一時熟。不知貽阿誰。出門東向望。淚落沾我衣。',
                 '新樹蘭蕙葩。雜用杜蘅草。終朝采其華。日暮不盈抱。采之欲遺誰。所思在遠道。馨香易銷歇。繁華會枯槁。悵望欲何言。臨風送懷抱。']
    test_poem = ['藁砧今何在。山上復有山。何當大刀頭。破鏡飛上天。',
                 '',
                 '日暮秋雲陰。江水清且深。保用通音信。蓮花玳瑁簪。',
                 '',
                 '菟絲從長風。根莖無斷絕。無情尚不離。有情安可別。',
                 '',
                 '南山一樹桂。上有雙鴛鴦。千年長交頸。歡慶不相忘。']
    test_poem = ['莫莫高山。深谷逶迤。曄曄紫芝。可以療飢。唐虞世遠。吾將何歸。駟馬高蓋。其憂甚大、富貴之畏人兮。不若貧賤之肆志。']
    test_poem = ['行行重行行。與君生別離。相去萬餘里。各在天一涯。道路阻且長。會面安可知。胡馬依北風。越鳥巢南枝。相去日已遠。衣帶日已緩。浮雲蔽白日。遊子不顧返。思君令人老。歲月忽已晚。棄捐勿復道。努力加餐飯。']
    for stanza in test_poem:
        stanza = stanza.split('。')
        for s in stanza:
            if s:
                last_char = s[len(s)-1]
                lc_late_han = schuessler.get_late_han(last_char)
                print(s + '(' + lc_late_han + ')。')

# purpose:
#   Determine the basic line length
def characterize_stanza_structure(stanza, is_verbose=False):
    funct_name = 'characterize_stanza_structure()'
    retval = -1
    if '。' not in stanza:
        print(funct_name + ' poem not punctuated with 「。」')
        print('stanza=' + stanza)
        return retval
    len2num_occ_dict = {}#{1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 17:0}
    stanza = stanza.split('。')
    for line in stanza:
        if not line.strip():
            continue
        if len(line) not in len2num_occ_dict:
            len2num_occ_dict[len(line)] = 1
        else:
            len2num_occ_dict[len(line)] += 1
    most_common_len = 0
    largest_num_occ = 0
    for l in len2num_occ_dict:
        if len2num_occ_dict[l] > 0 and is_verbose:
            print('line length = ' + str(l) + ', # occ = ' + str(len2num_occ_dict[l]))
        if len2num_occ_dict[l] > largest_num_occ:
            largest_num_occ = len2num_occ_dict[l]
            most_common_len = l
    if is_verbose:
        print('\tMost common length = ' + str(most_common_len))
    return most_common_len

def get_kmss2015_rhyme_words_naively(inscription, unique_id, ignore_unpunctuated=True):
    funct_name = 'get_rhyme_words_naively()'
    retval = {}
    stanza = inscription
    if ignore_unpunctuated and '。' not in inscription and '，' not in inscription:
        print(funct_name + ' poem not punctuated with 「。」')
        print('stanza=' + stanza)
        return retval
    stanza = stanza.split('。')
    line_inc = 0
    rw2line_dict = {}
    for line in stanza:
        if not line.strip():
            continue
        line_inc += 1
        # if line_inc is a multiple of 2
        if not line_inc % 2:
            line_id = unique_id + '.' + str(line_inc)
            if '兮' == line[len(line)-1]: # remove '兮' if it appears as last character in line
                line = line[0:len(line)-1]
            zi = line[len(line) - 1]
            if zi == '□' or zi == '…' or zi == '・':
                continue
            if zi not in rw2line_dict:
                rw2line_dict[zi] = []
            rw2line_dict[zi].append((line,line_id))
    return rw2line_dict

def get_rhyme_words_naively(stanza, line_length, unique_id, rw_type='Lu1983'):
    funct_name = 'get_rhyme_words_naively()'
    retval = {}
    if rw_type == 'Lu1983':
        if '。' not in stanza:
            print(funct_name + ' poem not punctuated with 「。」')
            print('stanza=' + stanza)
            return retval
        stanza = stanza.split('。')
        line_inc = 0
        rw2line_dict = {}
        for line in stanza:
            if not line.strip():
                continue
            line_inc += 1
            # if line_inc is a multiple of 2
            if not line_inc % 2:
                line_id = unique_id + '.' + str(line_inc)
                if '兮' == line[len(line)-1]: # remove '兮' if it appears as last character in line
                    line = line[0:len(line)-1]
                zi = line[len(line) - 1]
                zi_pos = len(line) - 1
                if zi == '□' or zi == '…' or zi == '・':
                    continue
                if zi not in rw2line_dict:
                    rw2line_dict[zi] = []
                rw2line_dict[zi].append((line,line_id))
    return rw2line_dict

def get_rhyme_words_naively2(stanza, line_length, unique_id, rw_type='Lu1983'):
    funct_name = 'get_rhyme_words_naively2()'
    retval = []
    if rw_type == 'Lu1983':
        if '。' not in stanza:
            print(funct_name + ' poem not punctuated with 「。」')
            print('stanza=' + stanza)
            return retval
        stanza = stanza.split('。')
        line_inc = 0
        rw2line_dict = {}
        rw_list = []
        for line in stanza:
            if not line.strip():
                continue
            line_inc += 1
            line_id = unique_id + '.' + str(line_inc)
            # if line_inc is a multiple of 2
            if not line_inc % 2:
                if '兮' == line[len(line)-1]: # remove '兮' if it appears as last character in line
                    line = line[0:len(line)-1]
                zi = line[len(line) - 1]
                zi_pos = len(line) - 1
                if zi == '□' or zi == '…' or zi == '・':
                    rw_list.append(('', -1, line, line_id))
                    continue
                #if zi not in rw2line_dict:
                #    rw2line_dict[zi] = []
                #rw2line_dict[zi].append((line,line_id))
                rw_list.append((zi, zi_pos, line, line_id))
            else:
                rw_list.append(('',-1, line, line_id))
    return rw_list #rw2line_dict

def get_rhyme_words_from_stanza(stanza_str, stanza_id, data_type, every_line_rhymes=False):
    funct_name = 'get_rhyme_words_from_stanza()'
    rw_list = []
    #exception_chars = ['之', '兮', '乎', '也', '矣']
    if not stanza_str.strip():
        return rw_list
    # There is some weirdness with mirror punctuation for a minority of mirrors.
    # These need to be handled differently
    if data_type == 'mirrors' and if_special_mirror_punctuation(stanza_str):
        return get_rhyme_words_for_kmss2015_mirror_inscription(stanza_id, stanza_str)
    stanza = stanza_str.split('。')
    line_inc = 0
    modulo = 2
    if every_line_rhymes:
        modulo = 1
    for line in stanza:
        if not line.strip():
            continue
        line_inc += 1
        line_id = stanza_id + '.' + str(line_inc)
        # if this is a rhyming line...
        if not line_inc % modulo:
            zi = line[len(line) - 1] # get the rhyming word
            zi_pos = len(line) - 1 # get the rhyming word's position
            if zi == '々':  # get the character preceding 々
                zi = line[len(line) - 2]
                zi_pos -= 1
            if zi == '□' or zi == '…' or zi == '・' or zi == '}' or zi == '{':
                rw_list.append(('', -1, line, line_id))
                continue
            if any(exception_char in zi for exception_char in exception_chars):
                zi = line[len(line) - 2]
                zi_pos -= 1
            if zi == '》':
                zi = line[len(line) - 3]
                zi_pos -= 1

            rw_list.append((zi, zi_pos, line, line_id))
        else:
            rw_list.append(('', -1, line, line_id))
    return rw_list  # rw2line_dict


#
# NOTE: This was the code used for the Vienna conference 2022 April
def naively_annotate_han_dynasty_poems():
    funct_name = 'naively_annotate_han_dynasty_poems()'
    readin_lu_1983_data()
    LU_poem = lu1983_poem()
    LU_poem.set_data_labels(lu1983_labels)
    uniqid2poem_dict = {}
    rhyme_net = rnetwork('rhyme_net')
    testing_code = False
    test_set = []
    s2rhyme_list = {}
    # Command line flags can be added as a string to Infomap
    im = Infomap("--two-level")
    unwanted = ['〗', '）', '}', '：', '々']
    visualization_type = 'nx'
    if visualization_type == 'nx':
        lu1983_graph = nx.Graph()


    if testing_code:
        test_set = ['.001', '.010', '.027', '.044', '.047', '.087', '.133', '.525']
    # for testing purposes only
        s2rhyme_list = {'Lu1983.001.1':[], 'Lu1983.010.1':['河', '平', '日', '遊', '外', '人', '緩'],
                        'Lu1983.010.2':['難', '屬', '水', '來'], 'Lu1983.027.1':['韋', '旗', '荒', '商', '光', '同', '邦',
                        '逸', '室', '衛', '隊', '城', '生', '耕', '寧', '京', '征', '平', '楚', '輔', '壹', '弼', '後'],
                        'Lu1983.027.2':['永', '臣', '王', '冰', '廢', '繇', '獸', '匱', '德', '恢', '夫', '祖', '夜', '子',
                        '司', '近', '鑒', '失', '霜', '顛', '發', '徂', '子', '何'], 'Lu1983.044.1':['一', '失', '壹'],
                        'Lu1983.047.1':['口', '后', '雨', '釜', '斗', '黍'],'Lu1983.087.1':[''],'Lu1983.087.2':[''],
                        'Lu1983.133.1':['蓋', '濭', '位', '醉', '祥', '觴', '光', '央', '合', '國', '輿', '蛇', '歸', '衰'],
                        'Lu1983.133.2':[''],'Lu1983.133.3':[''],
                        'Lu1983.525.1':['河', '瑕', '娛'],'Lu1983.525.2':['民','口'], 'Lu1983.525.3':['方', '公', '觴', '央'],
                        'Lu1983.525.4':['驚', '牲', '傾'], 'Lu1983.525.5':['喈', '西', '粲', '見', '獻'],
                        'Lu1983.525.6':['芬', '錢'], 'Lu1983.525.7':['方', '旁', '重', '僮'], 'Lu1983.525.8':['畔', '爛', '遍']}
    for k in lu1983_dict:
        if testing_code and k.replace('Lu1983','') not in test_set:
            continue
        LU_poem.set_data_with_line_from_file(k, lu1983_dict[k])
        uniqid2poem_dict[k] = ''
        uniqid2poem_dict[k] = deepcopy(LU_poem)
    for k in uniqid2poem_dict:#lu1983_poem
        print('-'*50)
        poem = uniqid2poem_dict[k].get_poem_content_as_str()
        print(k + ': ' + poem)
        stanza_list = poem.split('\n')
        st_inc = 0
        #
        # The naive annotator assumes:
        # - that all words in a single stanza that appear in a rhyming position rhyme together
        # - the last character of every other line (starting on line 2) rhyme
        for stanza in stanza_list:
            if not stanza.strip():
                continue
            st_inc += 1
            unique_id = uniqid2poem_dict[k].get_poem_id() + '.' + str(st_inc)
            most_common_line_length = characterize_stanza_structure(stanza)
            if most_common_line_length < 0:
                continue
            rw2line_dict = get_rhyme_words_naively(stanza, most_common_line_length, unique_id)
            # print stanza, show rhyme chars
            #for l in stanza:
            if len(rw2line_dict) > 1:
                print(unique_id + ': ' + stanza)
                print('Rhyme list = \'' + '\', \''.join(rw2line_dict.keys()) + '\'')
                #
                # Add Nodes to the rhyme network
                for rhyme_word in rw2line_dict:
                    tup = rw2line_dict[rhyme_word][0]
                    rhyme_net.add_node(rhyme_word, tup[1], tup[0])
                    if 1 and visualization_type == 'nx':
                        weight = rhyme_net.get_node_weight(rhyme_word)
                        if any(unw in rhyme_word for unw in unwanted):
                            continue
                        lu1983_graph.add_node(rhyme_word, weight=weight)
                #
                # Add Edges to the rhyme network
                rw_list = [*rw2line_dict] #'.keys()[:]
                if testing_code:
                    list_b = s2rhyme_list[unique_id]
                    diff = get_the_difference_of_two_lists(rw_list, list_b)
                    if len(diff) == 0:
                        print('Rhyme words for ' + unique_id + ' MATCHES theoretical!')
                    else:
                        print('Rhyme words for ' + unique_id + ' does NOT match theoretical!')
                        print('THEORETICAL: ' + ','.join(list_b))
                        print('ACTUAL: ' + ','.join(rw_list))
                        print('DIFF: ' + ','.join(diff))
                num_rhymes_in_stanza = len(rw_list)#len(stanza_list)
                for left_inc in range(0, num_rhymes_in_stanza, 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, num_rhymes_in_stanza, 1):
                        rhyme_num = unique_id
                        msg += unique_id + ': '
                        msg += rw_list[left_inc] + ':' + rw_list[right_inc] + ', num_rhymes_same_type = '
                        msg += str(num_rhymes_in_stanza) + ', poem_stanza_num = ' + rhyme_num
                        #if print_debug_msg:
                        #print(msg) # debug only
                        msg = ''
                        if any(unw in rw_list[left_inc] for unw in unwanted):
                            continue
                        if any(unw in rw_list[right_inc] for unw in unwanted):
                            continue

                        rhyme_net.add_edge(rw_list[left_inc], rw_list[right_inc], num_rhymes_in_stanza, rhyme_num)
                        #im.add_link(rw_list[left_inc], rw_list[right_inc])
                        edge_weight = rhyme_net.get_edge_weight(rw_list[left_inc], rw_list[right_inc])
                        if 1 and visualization_type == 'nx':
                            left = rw_list[left_inc]
                            right = rw_list[right_inc]
                            lu1983_graph.add_edge(rw_list[left_inc], rw_list[right_inc], weight=edge_weight)
    rhyme_net.get_infomap_linked_list_of_rhyme_network()

    if 1 and visualization_type == 'nx':
        alt.data_transformers.disable_max_rows()
        pos = nx.spring_layout(lu1983_graph)
        # Add attributes to each node.
        for n in lu1983_graph.nodes():
            lu1983_graph.nodes[n]['name'] = n
    #
    # INFOMAP stuff
    # Run the Infomap search algorithm to find optimal modules
    if 1:
        mapping = im.add_networkx_graph(lu1983_graph)
        print('<lu1983>')
        print(mapping.values())
        print('</lu1983')
        im.run()
        output_file = 'lu1983_infomap_output' + get_timestamp_for_filename() + '.txt'
        cluster_dict = {}
        if os.path.isfile(output_file):
            os.remove(output_file)
        cluster2zi_dict = {}
        for node in im.nodes:
            print(node.node_id, node.module_id, node.flow, mapping[node.node_id])
            if node.module_id not in cluster2zi_dict:
                cluster2zi_dict[node.module_id] = []
            cluster2zi_dict[node.module_id].append(mapping[node.node_id])
            output = str(node.node_id) + '\t' + str(node.module_id) + '\t' + str(node.flow) + '\t' + mapping[node.node_id]
            append_line_to_utf8_file('node_id2cluster_no.txt', str(node.node_id) + '\t' + str(node.module_id))
            cluster_dict[node.node_id] = node.module_id
            append_line_to_utf8_file(output_file, output)

        nx.set_node_attributes(lu1983_graph, cluster_dict, name='group')
        viz = nxa.draw_networkx(G=lu1983_graph, pos=pos, node_color='group',
                                node_label='name')  # note: , with_labels=True is for networkx, not nx_altair
        viz = viz.properties(height=700, width=700)

        viz.save('my_viz_test.html')
        alt_view.show(viz)
        graph = viz.interactive()
        for cluster_id in cluster2zi_dict:
            print(str(cluster_id) + ':')
            print('\t' + ''.join(cluster2zi_dict[cluster_id]))

def message2user(msg, is_verbose=False):
    if is_verbose:
        print(msg)

def test_multi_dataset_processor():
    funct_name = 'test_multi_dataset_processor()'
    is_verbose = True
    print_debug_msgs = True
    message2user('Starting multi_dataset_processor()...', is_verbose)
    processor = multi_dataset_processor(is_verbose)#, delete_old_data)
    message2user('Done.', is_verbose)
    run_lu1983_data = False
    run_mirror_data = True
    run_stelae_data = False
    run_combined_data = False

    is_verbose = False
    run_test = False

    pre_com_det_processing = True # False: post com det processing

    if run_lu1983_data:
        message2user('Running Received Shi Data...', is_verbose)
        if pre_com_det_processing:
            processor.overwrite_old_data()
            message2user('\tProcessing Received Shi Data', is_verbose)
            processor.pre_com_det_processing('received_shi', is_verbose, print_debug_msgs)
            message2user('\tDone.', is_verbose)
            message2user('\tOutputting data to file...', is_verbose)
            processor.output_received_shi_network_to_file()
            rnet_filename = filename_storage.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
            received_net = processor.get_network_object('network', 'naive', 'received_shi')
            received_net.output_rnetwork_to_file(rnet_filename)
            message2user('\tDone.', is_verbose)
            message2user('\tRunning Community Detection...', is_verbose)
            processor.run_community_detection_for_lu1983()
            message2user('\tDone.', is_verbose)
            message2user('\tCreating pyvis network graph...', is_verbose)
            processor.create_pyvis_network_graph_for_received_shi_com_detected_data()
            message2user('\tDone.', is_verbose)
            processor.create_pyvis_network_graph_for_pre_com_det_received_shi()
        else: # run com det processing
            processor.do_not_reprocess_old_data()
            message2user('\tCreating network with detected communities for received shi (from previous run)...',
                         is_verbose)
            processor.create_network_for_received_shi_with_com_det_annotator()
            message2user('\tDone.', is_verbose)
        message2user('Done.', is_verbose)

    if run_mirror_data:
        message2user('Running Mirror data...', is_verbose)
        if pre_com_det_processing:
            processor.overwrite_old_data()
            message2user('\tProcessing Mirror data...', is_verbose)
            processor.pre_com_det_processing('mirrors', is_verbose, print_debug_msgs)
            message2user('\tDone.', is_verbose)
            message2user('\tOutputting data to file...', is_verbose)
            processor.output_mirror_network_to_file()
            message2user('\tDone.', is_verbose)
            message2user('\tRunning Community Detection...', is_verbose)
            processor.run_community_detection_for_mirrors()
            message2user('\tDone.', is_verbose)
            message2user('\tCreating pyvis network graph...', is_verbose)
            processor.create_pyvis_network_graph_for_mirrors_com_detected_data()
            message2user('\tDone.', is_verbose)
        else: # run com det processing
            processor.do_not_reprocess_old_data()
            message2user('\tCreating network with detected communities for mirrors (from previous run)...',
                         is_verbose)
            processor.create_network_for_mirrors_with_com_det_annotator()
            message2user('\tDone.', is_verbose)
        message2user('Done.', is_verbose)
    if run_stelae_data:
        message2user('Running Stelae data...', is_verbose)
        if pre_com_det_processing:
            processor.overwrite_old_data()
            message2user('\tProcessing Stelae data...', is_verbose)
            processor.pre_com_det_processing('stelae', is_verbose, print_debug_msgs)
            message2user('\tDone.', is_verbose)
            message2user('\tOutputting data to file...', is_verbose)
            processor.output_stelae_network_to_file()
            message2user('\tDone.', is_verbose)
            message2user('\tRunning Community Detection...', is_verbose)
            processor.run_community_detection_for_stelae()
            message2user('\tDone.', is_verbose)
            message2user('\tCreating pyvis network graph...', is_verbose)
            processor.create_pyvis_network_graph_for_stelae_com_detected_data()
            message2user('\tDone.', is_verbose)
        else:# run com det processing
            processor.do_not_reprocess_old_data()
            message2user('\tCreating network with detected communities for stelae (from previous run)...',
                         is_verbose)
            processor.create_network_for_stelae_with_com_det_annotator()
            message2user('\tDone.', is_verbose)
        message2user('Done.', is_verbose)
    if run_combined_data:
        message2user('Running combined data...', is_verbose)
        if pre_com_det_processing:
            processor.do_not_reprocess_old_data()
            message2user('\tOutputting data to file...', is_verbose)
            processor.output_combined_data_network_to_file()
            message2user('\tDone.', is_verbose)
            message2user('\tRunning Community Detection...', is_verbose)
            processor.run_community_detection_for_combined_data()
            message2user('\tDone.', is_verbose)
            message2user('\tCreating pyvis network graph...', is_verbose)
            processor.create_pyvis_network_graph_for_combined_com_detected_data()
            message2user('\tDone.', is_verbose)
            message2user('\tCreating pyvis network graph for combined Schuessler...', is_verbose)
            processor.create_pyvis_network_graph_for_schuessler_combo_data()
            message2user('\tCreating pyvis network graph for pre-com det combined data...', is_verbose)
            processor.create_pyvis_network_graph_for_pre_com_det_combined_data()
            message2user('\tDone.', is_verbose)
            add_com_det = False
        else:# run com det processing
            processor.do_not_reprocess_old_data()
            add_com_det = True
            if run_lu1983_data:
                filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
                processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
            if run_mirror_data:
                filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'mirrors')
                processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
            if run_stelae_data:
                filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'stelae')
                processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
        message2user('Done.', is_verbose)
    if pre_com_det_processing:
        processor.get_list_of_nodes_missing_schuessler_data()

class multi_dataset_processor:
    def __init__(self, is_verbose=False):
        self.class_name = 'multi_dataset_processor'
        self.filename_storage = filename_storage # just a pointer to the global filename_storage
        self.reprocess_old_data = False
        self.is_verbose = is_verbose
        self.networks = {}
        self.initialize_network_array()
        self.print('Creating ' + self.class_name + '...')
        self.unwanted = ['〗', '）', '}', '：', '々']
        self.run_naive_annotator = True
        self.run_schuessler_annotator = True
        self.print('\tDone.')

    def initialize_network_array(self):
        if self.networks:
            return
        network_types = ['network', 'graph', 'pyvis']
        annotator_types = ['naive', 'schuessler', 'com_det']
        data_types = ['received_shi', 'stelae', 'mirrors', 'combo']
        for nt in network_types:
            self.networks[nt] = {}
            for at in annotator_types:
                self.networks[nt][at] = {}
                for dt in data_types:
                    self.networks[nt][at][dt] = None

    def get_network_object(self, network_type, annotator_type, data_type):
        funct_name = 'get_network_object()'
        retval = None
        net_obj_name = network_type + '_' + annotator_type + '_' + data_type
        if self.networks[network_type][annotator_type][data_type] == None:
            if network_type == 'network':
                self.networks[network_type][annotator_type][data_type] = rnetwork(self.class_name + '::' + net_obj_name)
            elif network_type == 'graph':
                self.networks[network_type][annotator_type][data_type] = nx.Graph()
            elif network_type == 'pyvis':
                self.networks[network_type][annotator_type][data_type] = Network('1000px', '1000px',
                                                                                 heading=net_obj_name, font_color="white")
                options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
                self.networks[network_type][annotator_type][data_type].set_options(options)
            else:
                msg = funct_name + 'ERROR: Requested network object type: \'' + network_type + '\' + \''
                msg += annotator_type + '\' + \'' + data_type + '\' NOT supported!'
                print(msg)
                return None
        return self.networks[network_type][annotator_type][data_type]

    def fill_rhyme_net_with_preprocessed_data(self):
        funct_name = 'fill_rhyme_net_with_preprocessed_data()'
        #naive_annotated_received_shi_network_data.txt
        received_shi_file = self.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
        mirrors_file = self.get_filename_for_annotated_network_data('network', 'naive', 'mirrors')
        stelae_file = self.get_filename_for_annotated_network_data('network', 'naive', 'stelae')
        self.readin_graph_data_from_file()

    def test_readin_graph_data(self):
        funct_name = 'test_readin_graph_data()'
        filename = self.get_filename_for_annotated_network_data('graph', 'naive', 'received_shi')
        self.readin_graph_data_from_file(filename)

    def readin_graph_data_from_file(self, filename):
        funct_name = 'readin_graph_data_from_file()'
        if not if_file_exists(filename, funct_name):
            return
        file_lines = readlines_of_utf8_file(filename)
        for fl in file_lines:
            print(fl)

    def test_readin_network_data(self):
        funct_name = 'test_readin_network_data()'
        filename = self.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
        self.readin_rnetwork_data_from_file(filename, 'rhyme_net')

    #
    # reads in network data (which was written out by an instantiation of this class)
    #   and writes the data into the specified network
    def readin_rnetwork_data_from_file(self, filename, network_name, is_verbose=False):
        funct_name = 'readin_rnetwork_data_from_file()'
        if not if_file_exists(filename, funct_name):
            print(funct_name + ' ERROR: filename = ' + filename + ' is INVALID! Aborting.')
            return
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
        my_networks = {
            'rhyme_net' : rhyme_net,
            's_rhyme_net' : s_rhyme_net
        }
        net = my_networks[network_name]
        delim = '\t'
        file_lines = readlines_of_utf8_file(filename)
        num_nodes = 0
        num_edges = 0
        nodes = []
        #
        # make one pass to add all nodes...
        for fl in file_lines:
            print(fl)
            fl = fl.split(delim)
            if len(fl) > 1:
                if is_hanzi(fl[1]): # Edge
                    if 0: # only adding nodes
                        left_char = fl[0]
                        right_char = fl[1]
                        try:
                            num_rhymes = fl[2]
                        except:
                            num_rhymes = -1
                        try:
                            rhyme_id = fl[3]
                        except:
                            rhyme_id = ''
                        if is_verbose:
                            print('EDGE: ' + left_char + delim + right_char + delim + str(num_rhymes) + delim + rhyme_id)
                        #if not net.is_node_already_in_network(left_char):
                        #    x = 1
                        net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                        num_edges += 1
                else: # Node
                    node = fl[0]
                    try:
                        stanza_inc = fl[1]
                    except:
                        stanza_inc = -1
                    try:
                        orig_line = fl[2]
                    except:
                        orig_line = ''
                    if is_verbose:
                        print('NODE: ' + node + delim + str(stanza_inc) + delim + orig_line)
                    net.add_node(node, stanza_inc, orig_line)
                    if node not in nodes:
                        nodes.append(node)
                        num_nodes += 1
        #
        # make second pass to add all edges
        for fl in file_lines:
            print(fl)
            fl = fl.split(delim)
            if len(fl) > 1:
                if is_hanzi(fl[1]): # Edge
                    left_char = fl[0]
                    right_char = fl[1]
                    try:
                        num_rhymes = fl[2]
                    except:
                        num_rhymes = -1
                    try:
                        rhyme_id = fl[3]
                    except:
                        rhyme_id = ''
                    if is_verbose:
                        print('EDGE: ' + left_char + delim + right_char + delim + str(num_rhymes) + delim + rhyme_id)
                    #if not net.is_node_already_in_network(left_char):
                    #    x = 1
                    net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                    num_edges += 1
                else: # Node
                    if 0: # only adding edges
                        node = fl[0]
                        try:
                            stanza_inc = fl[1]
                        except:
                            stanza_inc = -1
                        try:
                            orig_line = fl[2]
                        except:
                            orig_line = ''
                        if is_verbose:
                            print('NODE: ' + node + delim + str(stanza_inc) + delim + orig_line)
                        net.add_node(node, stanza_inc, orig_line)
                        if node not in nodes:
                            nodes.append(node)
                            num_nodes += 1

        print(str(len(file_lines)) + ' lines in the file. ' + str(num_nodes) + ' nodes and ' + str(num_edges) + ' edges.')

    def do_not_reprocess_old_data(self):
        self.reprocess_old_data = False

    def overwrite_old_data(self):
        self.reprocess_old_data = True

    def if_reprocess_old_data(self):
        return self.reprocess_old_data

    def delete_processed_annotated_network_data_files(self):
        funct_name = 'delete_processed_annotated_network_data_files()'
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'schuessler', 'combo'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'schuessler', 'combo'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', 'combo'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', 'combo'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', 'received_shi'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', 'received_shi'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'schuessler', 'received_shi'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'schuessler', 'received_shi'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', 'stelae'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', 'stelae'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'schuessler', 'stelae'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'schuessler', 'stelae'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'schuessler', 'mirrors'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', 'mirrors'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', 'mirrors'))
        delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'schuessler', 'mirrors'))

    def get_filename_for_annotated_network_data(self, network_type, annotator_type, data_type):
        funct_name = 'get_filename_for_annotated_network_data()'
        return self.filename_storage.get_filename_for_annotated_network_data(network_type, annotator_type, data_type)

    def parse_filename_for_annotated_network_data(self, filename):
        funct_name = 'parse_filename_for_annotated_network_data()'
        # Ex. naive_annotated_received_shi_network_data.txt
        annotator_type = 'naive'
        if 'com_det' in filename:
            annotator_type = 'com_det'
        elif 'schuessler' in filename:
            annotator_type = 'schuessler'
        data_type = 'received_shi'
        if 'stelae' in filename:
            data_type = 'stelae'
        elif 'mirrors' in filename:
            data_type = 'mirrors'
        if 'network' in filename:
            network_type = 'network'
        elif 'graph' in filename:
            network_type = 'graph'
        return annotator_type, data_type, network_type

    def create_pyvis_network_graph_for_pre_com_det_combined_data(self):
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        rhyme_net.create_pyvis_network_graph('Combined Data Pre-Com Det')

    def create_pyvis_network_graph_for_pre_com_det_received_shi(self):
        received_net = self.get_network_object('network', 'naive', 'received_shi')
        received_net.create_pyvis_network_graph('Received Shi Pre-Com Det')

    def output_received_shi_network_to_file(self):
        funct_name = 'output_network_to_file()'
        filename_base = 'annotated_received_shi_pre_com_det'
        print2file = True
        received_net = self.get_network_object('network', 'naive', 'received_shi')
        received_net.get_infomap_linked_list_of_rhyme_network(filename_base, print2file)

    def output_combined_data_network_to_file(self):
        funct_name = 'output_combined_data_network_to_file()'
        filename_base = 'annotated_combined_data_pre_com_det'
        print2file = True
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        rhyme_net.get_infomap_linked_list_of_rhyme_network(filename_base, print2file)

    def output_mirror_network_to_file(self):
        funct_name = 'output_mirror_network_to_file()'
        filename_base = 'annotated_mirrors_pre_com_det'
        print2file = True
        mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
        mirror_rnet.get_infomap_linked_list_of_rhyme_network(filename_base, print2file)

    def output_stelae_network_to_file(self):
        funct_name = 'output_stelae_network_to_file()'
        filename_base = 'annotated_stelae_pre_com_det'
        print2file = True
        stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
        stelae_rnet.get_infomap_linked_list_of_rhyme_network(filename_base, print2file)

    def create_pyvis_network_graph_for_mirrors_com_detected_data(self):
        funct_name = 'create_pyvis_network_graph_for_mirrors_com_detected_data()'
        print('Begin ' + funct_name)
        #com_det_file = os.path.join(filename_storage.get_hanproj_dir(), 'hanproject', 'com_detection_kyomeishusei2015_mirror_data_output.txt')
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        desired_groups = []
        mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
        mirror_rnet.create_pyvis_network_by_coloring_pre_com_det_data_w_com_det_groups('Pre-Com Det Mirror Data with Coloring', com_det_file, desired_groups)
        print('\tDone.')

    def create_pyvis_network_graph_for_schuessler_combo_data(self, add_weight=True):
        pyvis_schuessler_combo = self.get_network_object('pyvis', 'schuessler', 'combo')
        nlist = pyvis_schuessler_combo.get_nodes()
        elist = pyvis_schuessler_combo.get_edges()

        r2c = rhyme2color()
        pyvis_sch_net = Network('1000px', '1000px', heading='Schuessler for Combo Data', font_color="white")
        options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
        pyvis_sch_net.set_options(options)
        s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
        for n in nlist:
            # grab rhyme
            try:
                rhyme = n.split('(')[1]
            except IndexError as ie:
                x = 1
            rhyme = rhyme.replace(')','')
            rw = n.split(' (')[0]
            r2c.add_rhyme(rhyme)
            color = r2c.given_rhyme_get_color(rhyme)
            if add_weight:
                node_weight = s_rhyme_net.get_node_weight(n)
                pyvis_sch_net.add_node(n, label=n, title=rhyme, color=color, shape='circle',
                                      value=node_weight)  # title = popup
            else:
                pyvis_sch_net.add_node(n, label=n, title=rhyme, color=color, shape='circle')
        for e in elist:
            if add_weight:
                edge_weight = s_rhyme_net.get_edge_weight(e['from'], e['to'])
                pyvis_sch_net.add_edge(e['from'], e['to'], value=edge_weight)
            else:
                pyvis_sch_net.add_edge(e['from'], e['to'])
        pyvis_sch_net.show('Schuessler_combo_data.html')

    def create_pyvis_network_graph_for_received_shi_com_detected_data(self):
        funct_name = 'create_pyvis_network_graph_for_received_shi_com_detected_data()'
        #com_det_file = os.path.join(get_hanproj_dir(), 'hanproject', 'com_detection_lu1983_received_shi_data_output.txt')
        #com_det_file = os.path.join(filename_storage.get_hanproj_dir(), 'hanproject', 'com_det_annotated_received-shi_graph_data.txt')
        #com_det_file = self.filename_storage.get_filename_for_com_det_network_data('graph', 'com_det', 'received_shi')
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        desired_groups = []
        received_net = self.get_network_object('network', 'naive', 'received_shi')
        received_net.create_pyvis_network_by_coloring_pre_com_det_data_w_com_det_groups('Pre-Com Det Received Shi Data with Coloring', com_det_file, desired_groups)

    def create_pyvis_network_graph_for_stelae_com_detected_data(self):
        funct_name = 'create_pyvis_network_graph_for_stelae_com_detected_data()'
        #com_det_file = os.path.join(get_hanproj_dir(), 'hanproject',
        #                            'com_detection_mao_2008_stelae_data_output.txt')
        #com_det_file = os.path.join(filename_storage.get_hanproj_dir(), 'stelae', 'com_det_annotated_stelae_graph_data.txt')
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        desired_groups = []
        stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
        stelae_rnet.create_pyvis_network_by_coloring_pre_com_det_data_w_com_det_groups('Pre-Com Det Stelae Data with Coloring',
                                                                           com_det_file, desired_groups)

    def create_pyvis_network_graph_for_combined_com_detected_data(self):
        funct_name = 'create_pyvis_network_graph_for_combined_com_detected_data()'
        #com_det_file = filename_storage.get_filename_for_combined_data_community_detection()
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        desired_groups = []
        rhyme_net = rhyme_net = self.get_network_object('network', 'naive', 'combo')
        rhyme_net.create_pyvis_network_by_coloring_pre_com_det_data_w_com_det_groups('Pre-Com Det Combo Data with Coloring',
                                                                                com_det_file, desired_groups)
        #create_pyvis_network_by_coloring_pre_com_det_data_w_com_det_groups
        #NOTE:
        # this function just prints out the data in its current state
        # -> this state may change at different levels of processing
        # RECOMMENDED: have the state name in 'filename_base' (like: naive, schuessler, etc.)

    # NOTE:
    # This function isn't currently being used. It can be greatly simplified.
    def print_nodes_n_edges2file(self, network_type, filename_base):
        if network_type == 'combo':
            rhyme_net = self.get_network_object('network', 'naive', 'combo')
            rhyme_net.get_infomap_linked_list_of_rhyme_network('combined_' + filename_base)
            if self.is_schuessler_annotator_on():
                s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
                s_rhyme_net.get_infomap_linked_list_of_rhyme_network('schuessler_combined_' + filename_base)
        elif network_type == 'stelae':
            stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
            stelae_rnet.get_infomap_linked_list_of_rhyme_network('stelae_' + filename_base)
            if self.is_schuessler_annotator_on():
                s_stelae_rnet = self.get_network_object('network', 'schuessler', 'stelae')
                s_stelae_rnet.get_infomap_linked_list_of_rhyme_network('schuessler_stelae_' + filename_base)
        elif network_type == 'mirrors':
            mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
            mirror_rnet.get_infomap_linked_list_of_rhyme_network('mirrors_' + filename_base)
            if self.is_schuessler_annotator_on():
                s_mirror_rnet = self.get_network_object('network', 'schuessler', 'mirrors')
                s_mirror_rnet.get_infomap_linked_list_of_rhyme_network('schuessler_mirrors_' + filename_base)
        elif network_type == 'received_shi':
            received_net = self.get_network_object('network', 'naive', 'received_shi')
            received_net.get_infomap_linked_list_of_rhyme_network('received_shi_' + filename_base)
            if self.is_schuessler_annotator_on():
                s_received_net = self.get_network_object('network', 'schuessler', 'received_shi')
                s_received_net.get_infomap_linked_list_of_rhyme_network('schuessler_received_shi_' + filename_base)
        elif network_type == 'all':
            rhyme_net = self.get_network_object('network', 'naive', 'combo')
            rhyme_net.get_infomap_linked_list_of_rhyme_network('combined_' + filename_base)
            stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
            stelae_rnet.get_infomap_linked_list_of_rhyme_network('stelae_' + filename_base)
            mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
            mirror_rnet.get_infomap_linked_list_of_rhyme_network('mirrors_' + filename_base)
            received_net = self.get_network_object('network', 'naive', 'received_shi')
            received_net.get_infomap_linked_list_of_rhyme_network('received_shi_' + filename_base)
            if self.is_schuessler_annotator_on():
                s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
                s_rhyme_net.get_infomap_linked_list_of_rhyme_network('schuessler_combined_' + filename_base)
                s_stelae_rnet = self.get_network_object('network', 'schuessler', 'stelae')
                s_stelae_rnet.get_infomap_linked_list_of_vierhyme_network('schuessler_stelae_' + filename_base)
                s_mirror_rnet = self.get_network_object('network', 'schuessler', 'mirrors')
                s_mirror_rnet.get_infomap_linked_list_of_rhyme_network('schuessler_mirrors_' + filename_base)
                s_received_net = self.get_network_object('network', 'schuessler', 'received_shi')
                s_received_net.get_infomap_linked_list_of_rhyme_network('schuessler_received_shi_' + filename_base)

    def is_schuessler_annotator_on(self):
        return self.run_schuessler_annotator

    def is_naive_annotator_on(self):
        return self.run_naive_annotator

    def turn_on_schuessler_annotator(self):
        self.run_schuessler_annotator = True

    def turn_off_schuessler_annotator(self):
        self.run_schuessler_annotator = False

    def turn_on_naive_annotator(self):
        self.run_naive_annotator = True

    def turn_off_naive_annotator(self):
        self.run_naive_annotator = False

    def print(self, msg):
        if self.is_verbose:
            print(msg)

    def get_overall_node_list(self):
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        return rhyme_net.get_node_list()

    def get_list_of_nodes_missing_schuessler_data(self):
        node_list = self.get_overall_node_list()
        schuessler = schuessler_n_bentley()
        without_list = []
        for nl in node_list:
            late_han = schuessler.get_late_han(nl)
            if not late_han:
                without_list.append(nl)
        print('Nodes missing Schuessler Late Han data (' + str(len(without_list)) + '):')
        print('\t' + ''.join(without_list))

    def print_all_nodes_n_edges(self):
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        rhyme_net.print_all_nodes_n_edges(True)

    def plot_results(self):
        self.print('Plotting results...')
        graph = self.get_network_object('graph', 'naive', 'combo')
        nx.draw(graph, with_labels=True,
                bbox=dict(facecolor="skyblue", edgecolor='black', boxstyle='round,pad=0.2'),
                font_family='HanaMinA')
        plt.show()#bbox=dict(facecolor="skyblue", edgecolor='black', boxstyle='round,pad=0.2')
        self.print('\tDone.')

    def test_mao_2008_stelae_code(self):
        funct_name = 'test_mao_2008_stelae_code(self)):'
        self.print('Naively adding Mao 2008 data...')
        print('Parsing Mao 2008 stelase data...')
        s_data = parse_mao_2008_stelae_data(is_verbose=True)
        print('\tDone.')
        uniq2data_dict = s_data.get_uniq2data_dict()
        msg_out = ''
        rmarker = rhyme_marker()
        for s_id in uniq2data_dict:
            msg_out += s_id + ': '
            poem = uniq2data_dict[s_id].get_poem_content()
            rw_words = get_numbered_rhyme_words_from_stele_inscription(s_id, poem)
            print(s_id + ': ' + '\n'.join(poem))

    def naively_get_rhyme_words(self):
        funct_name = 'naively_get_rhyme_words()'
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        for s_id in self.uniq2data_dict:
            poem = self.uniq2data_dict[s_id].get_poem_content()
            inc = 0
            rw_words = get_rhyme_words_from_stele_inscription(s_id, poem)
            if rw_words: # if there are any rhyme words...
                #
                # add Nodes
                for rhyme_word in rw_words:
                    rhyme_net.add_node(rhyme_word, '1', '\n'.join(poem))
                    weight = rhyme_net.get_node_weight(rhyme_word)
                #
                # add Edges
                for left_inc in range(0, len(rw_words), 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, len(rw_words), 1):
                        rhyme_num = s_id
                        msg += s_id + ': '
                        msg += rw_words[left_inc] + ':' + rw_words[right_inc] + ', num_rhymes_same_type = '
                        msg += str(len(rw_words)) + ', poem_stanza_num = ' + rhyme_num
                        msg = ''
                        rhyme_net.add_edge(rw_words[left_inc], rw_words[right_inc], len(rw_words), rhyme_num)
                        edge_weight = rhyme_net.get_edge_weight(rw_words[left_inc], rw_words[right_inc])

    def are_there_lu1983_rhyme_words(self, line2rw_list):
        funct_name = 'are_there_lu1983_rhyme_words()'
        retval = False
        for tup in line2rw_list:
            if tup[0] != '':
                retval = True
                break
        return retval

    def create_network_for_combo_data_with_com_det_annotator(self):
        funct_name = 'create_network_for_combo_data_with_com_det_annotator()'
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        #com_det_file = get_com_det_group_descriptions_for_combo_data()
        if not os.path.isfile(com_det_file):
            print_debug_message(funct_name + ' ERROR: Community Detection Results file does NOT exist.',True)
            print_debug_message('\tRun combo community detection before running this function.')
            return
        desired_groups = []
        rw2group_dict, group2rw_list = readin_community_detection_group_descriptions(com_det_file, desired_groups)
        g2c = group2color()
        received_shi = self.create_network_for_received_shi_with_com_det_annotator()
        mirrors = self.create_network_for_mirrors_with_com_det_annotator()
        stelae = self.create_network_for_stelae_with_com_det_annotator()
        combo = self.initialize_pyvis_network('Combo Data with Com Det Annotator')
        rs_nodes = received_shi.get_nodes()
        received_net = self.get_network_object('network', 'naive', 'received_shi')
        for n in rs_nodes:
            if n in rw2group_dict:
                group_info = rw2group_dict[n][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)
            n_weight = received_net.get_node_weight(n)
            combo.add_node(n, label=n, color=color, shape='circle', value=n_weight) #add_node(n, label=n, title=rhyme, color=color)
        m_nodes = mirrors.get_nodes()
        mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
        for n in m_nodes:
            if n in rw2group_dict:
                group_info = rw2group_dict[n][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)
            n_weight = mirror_rnet.get_node_weight(n)
            combo.add_node(n, label=n, color=color, shape='circle', value=n_weight) #add_node(n, label=n, title=rhyme, color=color)
        s_nodes = stelae.get_nodes()
        stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
        for n in s_nodes:
            if n in rw2group_dict:
                group_info = rw2group_dict[n][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)

            n_weight = stelae_rnet.get_node_weight(n)
            combo.add_node(n, label=n, color=color, shape='circle', value=n_weight) #add_node(n, label=n, title=rhyme, color=color)
        rs_edges = received_shi.get_edges()
        received_net = self.get_network_object('network', 'naive', 'received_shi')
        for e in rs_edges:
            if e['from'] in rw2group_dict:
                group_info = rw2group_dict[e['from']][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)
            e_weight = received_net.get_edge_weight(e['from'], e['to'])
            combo.add_edge(e['from'], e['to'], color=color, value=e_weight)
        m_edges = mirrors.get_edges()
        for e in m_edges:
            if e['from'] in rw2group_dict:
                group_info = rw2group_dict[e['from']][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)
            e_weight = mirror_rnet.get_edge_weight(e['from'], e['to'])
            combo.add_edge(e['from'], e['to'], color=color, value=e_weight)
        s_edges = stelae.get_edges()
        for e in s_edges:
            if e['from'] in rw2group_dict:
                group_info = rw2group_dict[e['from']][0]
                g_num = group_info[0]
            else:
                g_num = 5000
            color = g2c.given_group_num_get_color(g_num)
            e_weight = stelae_rnet.get_edge_weight(e['from'], e['to'])
            combo.add_edge(e['from'], e['to'], color=color, value=e_weight)
        combo.show('combo_data_with_com_det_annotator.html')

    def create_network_for_received_shi_with_com_det_annotator(self):
        return self.create_network_with_com_det_annotator('received_shi')

    def create_network_for_mirrors_with_com_det_annotator(self):
        return self.create_network_with_com_det_annotator('mirrors')

    def create_network_for_stelae_with_com_det_annotator(self):
        return self.create_network_with_com_det_annotator('stelae')

    def create_network_with_com_det_annotator(self, data_type, desired_groups=[]):
        funct_name = 'create_network_with_com_det_annotator()'
        title = 'Com Det Network for ' + data_type.replace('_',' ').capitalize()
        network_type = 'graph' # this is the type of network data in the input file; not the type of network that
                               # will be created with this function
        annotator_type = 'com_det'
        pyvis_net = self.initialize_pyvis_network(title)
        #com_det_file = filename_storage.get_filename_for_com_det_network_data(network_type, annotator_type, data_type)
        com_det_file = filename_storage.get_filename_for_combo_com_det_network_data()
        #get_filename_for_combo_com_det_network_data
        #com_det_file = get_com_det_group_descriptions_for_combo_data()
        if not os.path.isfile(com_det_file):
            print_debug_message(funct_name + ' ERROR: Community Detection Results file does NOT exist.',True)
            print_debug_message('\tRun combo community detection before running this function.')
            return
        rw2group_dict, group2rw_list = readin_community_detection_group_descriptions(com_det_file, desired_groups)
        stanza_proc = stanza_processor(data_type)
        #
        # annotate Lu1983 poems with community detection
        print_debug_msgs = True
        every_line_rhymes = False # False: every other line rhymes, True: every line rhymes
        #if data_type == 'received_shi' or data_type == 'mirrors':
        #    every_line_rhymes = False

        #
        # Readin input data
        uniqid2poem_dict = {}
        output_file = self.filename_storage.get_output_filename_for_annotated_poems(annotator_type, data_type)
        html_file = output_file.replace('.txt', '.html')
        #
        # Readin input data
        uniqid2poem_dict = self.readin_preparsed_data(data_type)

        delete_file_if_it_exists(output_file)
        #
        # Process each poem individually
        poem = ''
        g2c = group2color()
        already_output = []
        line_inc = 0
        for k in uniqid2poem_dict:  # lu1983_poem -- for each unique poem ID...
            if data_type == 'received_shi':
                try:
                    poem = uniqid2poem_dict[k].get_poem_content_as_str()
                except TypeError as te:
                    x = 1
            elif data_type == 'mirrors':
                poem = uniqid2poem_dict[k]
                line_inc = 0
            elif data_type == 'stelae':
                poem = uniqid2poem_dict[k].get_poem_content_as_str()
                line_inc = 0

            print_debug_message(k + ': ' + poem, print_debug_msgs)
            stanza_list = poem.split('\n') # '\n' doesn't denote a stanza, only "extra" blank lines do

            #
            # Process a single stanza
            st_inc = 0
            line_out = ''
            len_slist = len(stanza_list)
            for stanza in stanza_list:
                if not stanza.strip():
                    continue
                #if '……' in stanza:
                #    x = 1
                st_inc += 1  # 1 <= st_inc <= N (here: use first, then increment)
                try:
                    if data_type == 'received_shi':
                        stanza_id = uniqid2poem_dict[k].get_poem_id() + '.' + str(st_inc)
                    elif data_type == 'stelae':
                        stanza_id = k + '.' + str(st_inc)
                    elif data_type == 'mirrors':
                        stanza_id = k
                except KeyError as ke:
                    x = 1

                stanza = convert_punctuation(stanza, data_type)
                stanza_proc.input_stanza(stanza, stanza_id, every_line_rhymes)

                if stanza.count(' ') > 0: # this is a sign that the original poem wasn't punctuated (and therefore
                                          #   should be skipped)
                    cd_annotated_stanza = []
                    rw_list = []
                else:
                    cd_annotated_stanza, rw_list = stanza_proc.annotate_with_combo_community_detection()
                if not cd_annotated_stanza: # if there are no rhymes in the stanza...
                    smsg = stanza_id
                    if data_type != 'stelae':
                         smsg += '.1'
                    smsg += '： ' + stanza
                    append_line_to_output_file(output_file, smsg)
                    continue


                #cd_annotated_stanza, rw_list = stanza_proc.annotate_with_combo_community_detection()
                #
                # Write annotations out to file
                if data_type == 'received_shi':
                    line_inc = 0
                    for cd_as in cd_annotated_stanza:
                        line_inc += 1
                        try:
                            line_out = k + '.' + str(st_inc) + '.' + str(line_inc) + '： ' + cd_as + '。'
                        except TypeError as te:
                            x = 1
                        append_line_to_utf8_file(output_file, line_out)
                else: # for stelae, mirrors
                    if cd_annotated_stanza:
                        for cd_as in cd_annotated_stanza:
                            line_inc += 1
                            #line_out += cd_as + '。'
                            line_out = k + '.1.' + str(line_inc) + '： ' + cd_as + '。'
                            if line_out not in already_output:
                                already_output.append(line_out)
                                append_line_to_utf8_file(output_file, line_out)
                    else: # if there are no rhyme words...
                        if not line_out:
                            line_out = k + '.1： ' + stanza # this doesn't need to remove last \n
                        else:
                            line_out += ' ' + stanza
                        if st_inc == len_slist:
                            if line_out not in already_output: # write this out on last line
                                already_output.append(line_out)
                                append_line_to_utf8_file(output_file, line_out)
                #
                # Create network
                group_num2simple_rw_list = {}
                for t in rw_list:
                    rw = t[0]
                    if not rw:
                        continue
                    if rw in rw2group_dict:
                        group_info = rw2group_dict[rw][0]
                        group_num = group_info[0]
                        if group_num not in group_num2simple_rw_list:
                            group_num2simple_rw_list[group_num] = []
                        group_num2simple_rw_list[group_num].append(rw)
                        node_weight = group_info[1]
                        color = g2c.given_group_num_get_color(group_num)
                        #
                        # Add Node
                        pyvis_net.add_node(rw, label=rw, color=color, shape='circle', value=node_weight)
                for g_num in group_num2simple_rw_list:
                    rwords = group_num2simple_rw_list[g_num]
                    edge_list = given_rhyme_group_return_list_of_edges(rwords, stanza_id)
                    if edge_list:
                        for el in edge_list:
                            left = el[0]
                            right = el[1]
                            weight = el[2]
                            if left in rw2group_dict:
                                group_info = rw2group_dict[left][0]
                                group_num = group_info[0]
                            color = g2c.given_group_num_get_color(group_num)
                            pyvis_net.add_edge(left, right, weight=weight, color=color, value=weight)
        pyvis_net.show(html_file)
        return pyvis_net

    # community detection is only run on naively annotated data
    def run_community_detection(self, graph, data_type):
        im = Infomap("--two-level")
        annotator_type = 'com_det'
        network_type = 'graph'
        if 1:
            alt.data_transformers.disable_max_rows()
            pos = nx.spring_layout(graph)
            # Add attributes to each node.
            for n in graph.nodes():
                #G.nodes[n]['weight'] = np.random.randn()
                graph.nodes[n]['name'] = n

        mapping = im.add_networkx_graph(graph)
        print('<' + data_type + '>')
        print(mapping.values())
        print('</' + data_type + '>')
        im.run()
        # or get_filename_for_combined_data_community_detection()
        output_file = self.filename_storage.get_filename_for_com_det_network_data(network_type, annotator_type, data_type)
        #get_filename_for_annotated_network_data-
        #output_file = 'com_detection_' + data_type + '_output.txt'
        cluster_dict = {}
        delete_file_if_it_exists(output_file)
        cluster2zi_dict = {}
        n2c_output_file = self.filename_storage.get_filename_for_node_id2cluster_no()
        for node in im.nodes:
            print(node.node_id, node.module_id, node.flow, mapping[node.node_id])
            if node.module_id not in cluster2zi_dict:
                cluster2zi_dict[node.module_id] = []
            cluster2zi_dict[node.module_id].append(mapping[node.node_id])
            output = str(node.node_id) + '\t' + str(node.module_id) + '\t' + str(node.flow) + '\t' + mapping[node.node_id]
            append_line_to_utf8_file(n2c_output_file, str(node.node_id) + '\t' + str(node.module_id))
            cluster_dict[node.node_id] = node.module_id
            append_line_to_utf8_file(output_file, output)

    def run_community_detection_for_lu1983(self):
        funct_name = 'run_community_detection_for_lu1983()'
        received_graph = self.get_network_object('graph', 'naive', 'received_shi')
        if not received_graph:
            print(funct_name + ' ERROR: call self.pre_com_det_processing() BEFORE calling this function!')
            return
        self.run_community_detection(received_graph, 'received_shi') # was: lu1983_received_shi_data

    def run_community_detection_for_mirrors(self):
        funct_name = 'run_community_detection_for_mirrors()'
        print('Beginning ' + funct_name)
        mirror_graph = self.get_network_object('graph', 'naive', 'mirrors')
        if not mirror_graph:
            print(funct_name + ' ERROR: call self.pre_com_det_processing() BEFORE calling this function!')
            print('\tDone.')
            return
        self.run_community_detection(mirror_graph, 'mirrors') # was: kyomeishusei2015_mirror_data
        print('\tDone.')

#process_mao_2008_stelae_data
    def run_community_detection_for_stelae(self):
        funct_name = 'run_community_detection_for_stelae()'
        stelae_graph = self.get_network_object('graph', 'naive', 'stelae')
        if not stelae_graph:
            print(funct_name + ' ERROR: call self.pre_com_det_processing() BEFORE calling this function!')
            return
        self.run_community_detection(stelae_graph, 'stelae') # was: mao_2008_stelae_data

    def run_community_detection_for_combined_data(self):
        funct_name = 'run_community_detection_for_combined_data()'
        graph = self.get_network_object('graph', 'naive', 'combo')
        if not graph:
            print(funct_name + ' ERROR: call process_..._data() for each type of data you want to run BEFORE calling this function!')
            return
        self.run_community_detection(graph, 'combo')

    def initialize_pyvis_network(self, title):
        pyvis_net = Network('1000px', '1000px', heading=title, font_color='white')
        options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
        pyvis_net.set_options(options)
        return pyvis_net
    # def get_filename_for_annotated_network_data(self, network_type, annotator_type, data_type):

    def append_edge_data_to_file(self, annotator_type, data_type, left_char, right_char, num_rhymes_or_weight=-1, rhyme_id=''):
        funct_name = 'append_edge_data_to_file()'
        network_type = 'network'
        delim = '\t'
        output = left_char + delim + right_char
        if not rhyme_id: # if network type is 'graph'
            network_type = 'graph'
            if num_rhymes_or_weight > -1:
                output += delim + str(num_rhymes_or_weight)
        else: # otherwise, it's 'network'
            #network_type = 'network' # left_char, right_char, num_rhymes, rhyme_id
            output += delim + str(num_rhymes_or_weight) + delim + rhyme_id
        output_file = self.get_filename_for_annotated_network_data(network_type, annotator_type, data_type)
        append_line_to_utf8_file(output_file, output)

    def add_edge(self, left_char, right_char, num_rhymes, rhyme_id, annotator_type, data_type):
        test_left_char = ''
        test_right_char = ''
        if annotator_type == 'naive':
            test_left_char = left_char
            test_right_char = right_char
        elif annotator_type == 'schuessler':
            test_left_char = self.strip_lhan_from_rhyme_word(left_char)
            test_right_char = self.strip_lhan_from_rhyme_word(right_char)
        if any(unw in test_left_char for unw in self.unwanted):  # can be outside function, use when
                                                                 # evaluating the list of edges
            return
        if any(unw in test_right_char for unw in self.unwanted):
            return
        if not let_this_char_become_node(test_left_char):
            return
        if not let_this_char_become_node(test_right_char):
            return
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        edge_weight = rhyme_net.get_edge_weight(left_char, right_char)
        s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
        s_edge_weight = s_rhyme_net.get_edge_weight(left_char, right_char)
        #
        # The code below can be greatly simplified
        # to something like:
        #    net = self.get_network_object('network', annotator_type, data_type)
        #    net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
        #    graph = self.get_network_object('graph', annotator_type, data_type)
        #    graph.add_edge(left_char, right_char, weight=edge_weight)

        if annotator_type == 'naive' and self.is_naive_annotator_on():
            pyvis_naive_combo = self.get_network_object('pyvis', annotator_type, 'combo')
            pyvis_naive_combo.add_edge(left_char, right_char, value=edge_weight)
            rhyme_net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
            graph = self.get_network_object('graph', annotator_type, 'combo')
            graph.add_edge(left_char, right_char, weight=edge_weight)
            self.append_edge_data_to_file(annotator_type, data_type, left_char, right_char, num_rhymes, rhyme_id) # Network
            self.append_edge_data_to_file(annotator_type, data_type, left_char, right_char, edge_weight) # Graph
        elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
            pyvis_schuessler_combo = self.get_network_object('pyvis', annotator_type, 'combo')
            pyvis_schuessler_combo.add_edge(left_char, right_char, value=s_edge_weight)
            s_rhyme_net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
            self.append_edge_data_to_file(annotator_type, data_type, left_char, right_char, num_rhymes, rhyme_id)  # Network
        if data_type == 'received_shi':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                received_net = self.get_network_object('network', annotator_type, data_type)
                received_net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                received_graph = self.get_network_object('graph', annotator_type, data_type)
                received_graph.add_edge(left_char, right_char, weight=edge_weight)
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_received_net = self.get_network_object('network', annotator_type, data_type)
                s_received_net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
        elif data_type == 'stelae':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                stelae_rnet = self.get_network_object('network', annotator_type, data_type)
                stelae_rnet.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                stelae_graph = self.get_network_object('graph', annotator_type, data_type)
                stelae_graph.add_edge(left_char, right_char, weight=edge_weight)
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_stelae_rnet = self.get_network_object('network', annotator_type, data_type)
                s_stelae_rnet.add_edge(left_char, right_char, num_rhymes, rhyme_id)
        elif data_type == 'mirrors':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                mirror_rnet = self.get_network_object('network', annotator_type, data_type)
                mirror_rnet.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                mirror_graph = self.get_network_object('graph', annotator_type, data_type)
                mirror_graph.add_edge(left_char, right_char, weight=edge_weight)
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_mirror_rnet = self.get_network_object('network', annotator_type, data_type)
                s_mirror_rnet.add_edge(left_char, right_char, num_rhymes, rhyme_id)
    #
    # TO DO:
    # create another function for 'graph' types

    def create_network_from_file_data(self, network_type, annotator_type, data_type):
        funct_name = 'create_network_from_file_data()' # class.name = multi_dataset_processor
        input_file = self.get_filename_for_annotated_network_data(network_type, annotator_type, data_type)
        if not if_file_exists(input_file, funct_name):
            return
        rhyme_net = rnetwork(self.class_name + '::create_network_from_file_data')
        #
        # set up visualization network
        annotator_type, data_type, network_type = self.parse_filename_for_annotated_network_data(input_file)
        heading = annotator_type + ' Annotator for ' + data_type
        pyvis_net = Network('1000px', '1000px', heading=heading, font_color='white')
        options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
        pyvis_net.set_options(options)
        #
        # readin file data
        file_data = readlines_of_utf8_file(input_file)

        #
        # Add data to rnetwork() network (need this to get correct node weights)
        for fd in file_data:
            fd = fd.split('\t')
            print('\t'.join(fd))
            if is_hanzi(fd[1]): # is EDGE: if second item is a hanzi; Ex. 皇	堂	3	Lu1983.020.1
                left_char = fd[0]
                right_char = fd[1]
                num_rhymes = fd[2]
                weight = calculate_edge_weight_given_num_rhymes(num_rhymes)
                rhyme_id = fd[3]
                rhyme_net.add_edge(left_char, right_char, num_rhymes, rhyme_id)
            elif fd[1].isdigit(): # is NODE: Ex. 下	1	知我好道公來下兮
                node = fd[0]
                st_inc = fd[1]
                orig_line = fd[2]
                rhyme_net.add_node(node, str(st_inc), orig_line)
        #
        # Now add data to visualization network
        for fd in file_data:
            fd = fd.split('\t')
            print('\t'.join(fd))
            if is_hanzi(fd[1]): # is EDGE: if second item is a hanzi; Ex. 皇	堂	3	Lu1983.020.1
                left_char = fd[0]
                right_char = fd[1]
                num_rhymes = fd[2]
                weight = calculate_edge_weight_given_num_rhymes(num_rhymes)
                #rhyme_id = fd[3]
                pyvis_net.add_edge(left_char, right_char, value=weight)
            elif fd[1].isdigit(): # is NODE: Ex. 下	1	知我好道公來下兮
                node = fd[0]
                #st_inc = fd[1]
                #orig_line = fd[2]
                weight = rhyme_net.get_node_weight(node)
                pyvis_net.add_node(node, label=node, value=weight, shape='circle')
        pyvis_net.show(heading + '.html')

    def append_node_data_to_file(self, annotator_type, data_type, rhyme_word, st_inc_or_weight, orig_line='', lhan=''):
        funct_name = 'append_node_data_to_file()'
        # 'network' => add_node(rhyme_word, str(st_inc), orig_line) OR add_node(rhyme_word, str(st_inc), orig_line, lhan)
        # 'graph' => add_node(rhyme_word, weight=weight)
        output = rhyme_word
        network_type = 'network'
        delim = '\t'
        if not orig_line:
            network_type = 'graph'
            if st_inc_or_weight:
                output += delim + str(st_inc_or_weight)
        else: # if 'network' type
            output += delim + str(st_inc_or_weight) + delim + orig_line
            if lhan:
                output += delim + lhan
        output_file = self.get_filename_for_annotated_network_data(network_type, annotator_type, data_type)
        append_line_to_utf8_file(output_file, output)

    def add_node(self, rhyme_word, st_inc, orig_line, annotator_type, data_type):
        if any(unw in rhyme_word for unw in self.unwanted):
            return
        rhyme_net = self.get_network_object('network', 'naive', 'combo')
        weight = rhyme_net.get_node_weight(rhyme_word)
        s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
        s_weight = s_rhyme_net.get_node_weight(rhyme_word)
        #
        # The code below can be greatly simplified. See note under 'add_edge()'
        if annotator_type == 'naive' and self.is_naive_annotator_on():
            pyvis_naive_combo = self.get_network_object('pyvis', 'naive', 'combo')
            pyvis_naive_combo.add_node(rhyme_word, label=rhyme_word, shape='circle', value=weight)#weight
            rhyme_net.add_node(rhyme_word, str(st_inc), orig_line)  # (zi, poem_stanza_num, raw_line)
            graph = self.get_network_object('graph', 'naive', 'combo')
            graph.add_node(rhyme_word, weight=weight)  # common data
            #
            # record network data
            self.append_node_data_to_file(annotator_type, data_type, rhyme_word, str(st_inc), orig_line) # network
            self.append_node_data_to_file(annotator_type, 'combo', rhyme_word, str(st_inc), orig_line) # network
            #
            # record graph data
            self.append_node_data_to_file(annotator_type, data_type, rhyme_word, str(weight))  # graph
            self.append_node_data_to_file(annotator_type, 'combo', rhyme_word, str(weight))  # graph
        elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
            pyvis_schuessler_combo = self.get_network_object('pyvis', 'schuessler', 'combo')
            pyvis_schuessler_combo.add_node(rhyme_word, title=self.strip_lhan_from_rhyme_word(rhyme_word),
                                                label=rhyme_word, shape='circle', value=s_weight)
            lhan = self.grab_lhan_from_rhyme_word(rhyme_word)
            rhyme_word = self.strip_lhan_from_rhyme_word(rhyme_word)
            self.append_node_data_to_file(annotator_type, data_type, rhyme_word, str(st_inc), orig_line, lhan)
            self.append_node_data_to_file(annotator_type, 'combo', rhyme_word, str(st_inc), orig_line, lhan)

        if data_type == 'received_shi':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                received_net = self.get_network_object('network', 'naive', 'received_shi')
                received_net.add_node(rhyme_word, str(st_inc), orig_line)
                received_graph = self.get_network_object('graph', 'naive', 'received_shi')
                received_graph.add_node(rhyme_word, weight=weight)  # received data only
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
                s_rhyme_net.add_node(rhyme_word, str(st_inc), orig_line, lhan)
                s_received_net = self.get_network_object('network', 'schuessler', 'received_shi')
                s_received_net.add_node(rhyme_word,str(st_inc), orig_line, lhan)
        elif data_type == 'stelae':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                stelae_rnet = self.get_network_object('network', 'naive', 'stelae')
                stelae_rnet.add_node(rhyme_word, str(st_inc), orig_line)  # stelae only data
                stelae_graph = self.get_network_object('graph', 'naive', 'stelae')
                stelae_graph.add_node(rhyme_word, weight=weight)  # stelae only data
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
                s_rhyme_net.add_node(rhyme_word, str(st_inc), orig_line, lhan)
                s_stelae_rnet = self.get_network_object('network', 'schuessler', 'stelae')
                s_stelae_rnet.add_node(rhyme_word, str(st_inc), orig_line, lhan)
        elif data_type == 'mirrors':
            if annotator_type == 'naive' and self.is_naive_annotator_on():
                mirror_rnet = self.get_network_object('network', 'naive', 'mirrors')
                mirror_rnet.add_node(rhyme_word, str(st_inc), orig_line)  # mirror only data
                mirror_graph = self.get_network_object('graph', 'naive', 'mirrors')
                mirror_graph.add_node(rhyme_word, weight=weight)  # mirror only data
            elif annotator_type == 'schuessler' and self.is_schuessler_annotator_on():
                s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
                s_rhyme_net.add_node(rhyme_word, str(st_inc), orig_line, lhan)  # common data
                s_mirror_rnet = self.get_network_object('network', 'schuessler', 'mirrors')
                s_mirror_rnet.add_node(rhyme_word, str(st_inc), orig_line, lhan)  # mirror only data

    # ASSUMES input as: '{zi} ({lhan})'
    def grab_lhan_from_rhyme_word(self, rw):
        if '(' in rw:
            rw = rw.split('(')[1]
            rw = rw.replace(')','')
        return rw

    # ASSUMES input as: '{zi} ({lhan})'
    def strip_lhan_from_rhyme_word(self, rw):
        if '(' in rw:
            rw = rw.split('(')[0].strip()
        return rw

    def annotate_char_with_rhyme(self, zi, rhyme):
        retval = zi
        if rhyme.strip():
            retval = zi + ' (' + rhyme + ')'
        return retval

    def delete_old_data_files(self, data_type):
        if self.if_reprocess_old_data():
            if self.is_naive_annotator_on():
                delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', data_type))
                delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', data_type))
                delete_file_if_it_exists(self.get_filename_for_annotated_network_data('network', 'naive', 'combo'))
                delete_file_if_it_exists(self.get_filename_for_annotated_network_data('graph', 'naive', 'combo'))

            if self.is_schuessler_annotator_on():
                delete_file_if_it_exists(
                    self.get_filename_for_annotated_network_data('network', 'schuessler', data_type))
                delete_file_if_it_exists(
                    self.get_filename_for_annotated_network_data('graph', 'schuessler', data_type))
                delete_file_if_it_exists(
                    self.get_filename_for_annotated_network_data('network', 'schuessler', 'combo'))
                delete_file_if_it_exists(
                    self.get_filename_for_annotated_network_data('graph', 'schuessler', 'combo'))

    # INPUTS:
    #   is_verbose
    #   print_debug_msgs
    #   data_type
    #   annotator_type
    # OUTPUTS:
    #   naive pyvis network
    #   schuessler pyvis network
    #   naive annotated file
    #   schuessler annotated file
    def readin_preparsed_data(self, data_type):
        if data_type == 'received_shi':
            uniqid2poem_dict = readin_lu_1983_data()
            #every_line_rhymes = False
        elif data_type == 'stelae':
            s_data = parse_mao_2008_stelae_data(is_verbose=True)
            uniqid2poem_dict = s_data.get_uniq2data_dict()
        elif data_type == 'mirrors':
            uniqid2poem_dict = readin_kyomeishusei2015_han_mirror_data()
        return uniqid2poem_dict

    # INPUTS:
    #   is_verbose
    #   print_debug_msgs
    #   data_type
    # OUTPUTS:
    #   naive pyvis network
    #   schuessler pyvis network
    #   naive annotated file
    #   schuessler annotated file
    def pre_com_det_processing(self, data_type, is_verbose=False, print_debug_msgs=False):
        funct_name = 'pre_com_det_processing(' + data_type + ')'  # class multi_dataset_processor
        self.print('Processing ' + data_type + ' data...')
        x = self.class_name
        test_mode = False
        if self.if_reprocess_old_data() and not test_mode:
            self.delete_old_data_files(data_type)
        # self.class_name: multi_dataset_processor
        naive_output = ''
        schuessler_output = ''
        naive_rw_skipped = []
        s_annotator = schuessler_stanza_annotator()
        color_store = rhyme_color_tracker()
        pyvis_s_net = Network('1000px', '1000px', heading='Schuessler Annotator for ' + data_type, font_color='white')
        pyvis_n_net = Network('1000px', '1000px', heading='Pre-Com Det Naive Annotator for ' + data_type,
                             font_color='white')
        options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
        pyvis_s_net.set_options(options)
        pyvis_n_net.set_options(options)

        if self.is_naive_annotator_on():
            naive_output = filename_storage.get_output_filename_for_poem_marking_annotation(data_type, 'naive', test_mode)
            #if data_type == 'received_shi':
            #    naive_output = os.path.join(get_received_shi_dir(), 'naively_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')
            delete_file_if_it_exists(naive_output)
        if self.is_schuessler_annotator_on():
            schuessler_output = filename_storage.get_output_filename_for_poem_marking_annotation(data_type, 'schuessler', test_mode)
            #if data_type == 'recieved_shi':
            #    schuessler_output = os.path.join(get_received_shi_dir(), 'schuessler_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')
            delete_file_if_it_exists(schuessler_output)
            schuessler = schuessler_n_bentley()

        s_annotator.reset()

        every_line_rhymes = False  # False -> assumed to rhyme every other line, starting with the second line
                                  # True -> every line rhymes, starting with the first line
        #if data_type == 'received_shi' or data_type == 'mirrors':
        #    every_line_rhymes = False

        #
        # Readin input data
        uniqid2poem_dict = self.readin_preparsed_data(data_type)

        stanza_proc = stanza_processor(data_type)

        #
        # Process each poem individually
        for k in uniqid2poem_dict:  # lu1983_poem -- for each unique poem ID...
            poem_num = int(k.split('.')[1]) # debug only
            if poem_num <= 0: # debug only - was 181
                continue# debug only
            if is_verbose:
                print('-' * 50)
            if 'Lu1983.226' in k:  # these poems choke the fayin path optimizier
                x = 1
                continue
            if 'Lu1983.428' in k:
                x = 1
                continue
            if 'Lu1983.154' in k or 'Lu1983.478' in k:
                x = 1
            if 0:
                if 'Mou2008.045' in k:
                    continue

                if 'Mou2008.060' in k:
                    continue

                if 'Mou2008.067' in k:
                    continue

                if 'Mou2008.133' in k: # this one caused my IDE to run out of memory
                    continue

            if data_type == 'received_shi' or data_type == 'stelae':
                poem = uniqid2poem_dict[k].get_poem_content_as_str()
            elif data_type == 'mirrors':
                poem = uniqid2poem_dict[k]
            else:
                print(funct_name + ' ERROR: unsupported data type: ' + data_type)
                print('\tAborting.')
                return
            print_debug_message(k + ': ' + poem, print_debug_msgs)
            stanza_list = poem.split('\n')

            st_inc = 0
            #
            # The naive annotator assumes:
            # - that all words in a single stanza that appear in a rhyming position rhyme together
            # - For 'received_shi', that's the last character of every other line (starting on line 2) rhyme
            # - for 'mirrors' and 'stelae', that's the last character of every line
            #  -> this is set by the 'every_line_rhymes' variable
            # Process a single stanza
            for stanza in stanza_list:
                if not stanza.strip():
                    continue

                s_annotator.reset()  # should be reset in between stanzas
                st_inc += 1
                try:
                    if data_type == 'mirrors':
                        poem_id = k
                    else:
                        poem_id = uniqid2poem_dict[k].get_poem_id()
                    stanza_id = poem_id + '.' + str(st_inc)
                except KeyError as ke:
                    x = 1
                # rhyme words (rw) on per stanza basis
                #
                # Do actual annotation (place markers in poems, write to file)
                #    and add Nodes
                stanza = convert_punctuation(stanza, data_type)
                stanza_proc.input_stanza(stanza, stanza_id, every_line_rhymes)
                #
                #   For Naive Annotator
                temp_file = filename_storage.get_filename_for_temp_naively_annotated_data(data_type)
                if stanza.count(' ') > 0: # this is a sign that the original poem wasn't punctuated (and therefore
                                          #   should be skipped)
                    annotated_stan = []
                    rijm_lijst = []
                else:
                    annotated_stan, rijm_lijst = stanza_proc.naively_annotate(temp_file)
                #
                if not annotated_stan: # if there are no rhymes in the stanza...
                    append_line_to_output_file(naive_output, stanza_id + '： ' + stanza)
                    append_line_to_output_file(schuessler_output, stanza_id + '： ' + stanza)
                    continue

                linc = 0
                rw_list = []
                received_net = self.get_network_object('network', 'naive', 'received_shi')
                for lijn in rijm_lijst:
                    rijm = lijn[0].strip()
                    line_id = lijn[3]
                    orig_line = lijn[2]
                    #
                    # Annotate
                    try:
                        annotated_line = line_id + '： ' + annotated_stan[linc] + '。'
                    except IndexError as ie:
                        x = 1
                    append_line_to_utf8_file(naive_output, annotated_line)
                    if rijm:  # Add node
                        self.add_node(rijm, st_inc, orig_line, 'naive', data_type)
                        n_weight = received_net.get_node_weight(rijm)
                        pyvis_n_net.add_node(rijm, label=rijm, shape='circle', value=n_weight)
                        rw_list.append(rijm)
                    linc += 1
                #
                # Add Edges for Naive Annotator
                edge_list = given_rhyme_group_return_list_of_edges(rw_list, stanza_id)
                rhyme_num = stanza_id  # = poem_id + '.' + str(stanza_num)
                #received_net = self.get_network_object('network', 'naive', 'received_shi')
                for edge in edge_list:
                    left_char = edge[0]
                    right_char = edge[1]
                    num_rhymes = edge[2]
                    rhyme_id = edge[3]
                    edge_weight = received_net.get_edge_weight(left_char, right_char)
                    pyvis_n_net.add_edge(left_char, right_char, value=edge_weight)
                    self.add_edge(left_char, right_char, num_rhymes, rhyme_id, 'naive', data_type)

                #
                #   For Schuessler Annotator
                s_annotated_stan, s_rijm_lijst, rw2lhan_dict, rhyme2rw_list = stanza_proc.schuessler_annotate(k)
                s_linc = 0
                s_received_net = self.get_network_object('network', 'schuessler', 'received_shi')
                for s_lijn in s_rijm_lijst:
                    line_id = s_lijn[3]
                    orig_line = s_lijn[2]
                    rw_pos = s_lijn[1]
                    s_rijm = s_lijn[0].strip()
                    #
                    # Annotate
                    s_annotated_line = line_id + '： ' + s_annotated_stan[s_linc] + '。'
                    append_line_to_utf8_file(schuessler_output, s_annotated_line)

                    if s_rijm:  # Add node
                        if '寤' in s_rijm:
                            x = 1
                        lhan = rw2lhan_dict[s_rijm]
                        rhyme = get_rhyme_from_schuessler_late_han_syllable(lhan)
                        plain_rw = s_rijm
                        s_rijm = self.annotate_char_with_rhyme(s_rijm, rhyme)
                        self.add_node(s_rijm, st_inc, orig_line, 'schuessler', data_type)
                        n_weight = s_received_net.get_node_weight(plain_rw)
                        pyvis_s_net.add_node(s_rijm, title=plain_rw, label=s_rijm, shape='circle', value=n_weight)
                        s_annotator.add_rhyme_word(plain_rw, rw_pos, orig_line, line_id)
                        color_store.add_rhyme_word(plain_rw)

                    s_linc += 1
                #
                # Add Schuessler Edges
                #s_received_net = self.get_network_object('network', 'schuessler', 'received_shi')
                for r in rhyme2rw_list:
                    rw_list = rhyme2rw_list[r]
                    edge_list = given_rhyme_group_return_list_of_edges(rw_list, stanza_id)
                    for edge in edge_list:
                        left_char = edge[0]
                        right_char = edge[1]
                        num_rhymes = edge[2]
                        rhyme_id = edge[3]
                        l_lhan = rw2lhan_dict[left_char]
                        r_lhan = rw2lhan_dict[right_char]
                        l_rhyme = get_rhyme_from_schuessler_late_han_syllable(l_lhan)
                        r_rhyme = get_rhyme_from_schuessler_late_han_syllable(r_lhan)
                        left_char = self.annotate_char_with_rhyme(left_char, l_rhyme)
                        right_char = self.annotate_char_with_rhyme(right_char, r_rhyme)
                        if l_rhyme != r_rhyme:
                            print('Rhymes do NOT match! ' + left_char + ' : ' + right_char)
                            print('\tSkipping!')
                            continue
                        s_edge_weight = s_received_net.get_edge_weight(left_char, right_char)
                        pyvis_s_net.add_edge(left_char, right_char, value=s_edge_weight)
                        self.add_edge(left_char, right_char, num_rhymes, rhyme_id, 'schuessler', data_type)
        self.print('\tDone.')
        if self.is_schuessler_annotator_on():
            s_rhyme_net = self.get_network_object('network', 'schuessler', 'combo')
            nlist = s_rhyme_net.get_node_list()
            elist = s_rhyme_net.get_unique_edge_list()
            r2c = rhyme2color()
            pyvis_sch_net = Network('1000px', '1000px', heading='Schuessler ' + data_type, font_color='white')
            pyvis_sch_net.set_options(options)
        if self.is_naive_annotator_on():
            pyvis_n_net.show('pre_com_det_' + data_type + '.html')

def given_rhyme_group_return_list_of_edges(rw_list, rhyme_id):
    funct_name = 'given_rhyme_group_return_list_of_edges()'
    num_rhymes = len(rw_list)
    edge_list = []
    for left_inc in range(0, num_rhymes, 1):
        for right_inc in range(left_inc + 1, num_rhymes, 1):
            edge_list.append((rw_list[left_inc], rw_list[right_inc], num_rhymes, rhyme_id))
    return edge_list

def test_visualize_infomap_output():
    funct_name = 'test_visualize_infomap_output()'
    filename = 'lu1983_infomap_output.txt'
    visualize_infomap_output(filename)

def visualize_infomap_output(filename):
    funct_name = 'visualize_infomap_output()'
    line_list = readlines_of_utf8_file(filename)
    for ll in line_list:
        print(ll)

# 'saveas' must be a filename ending in .html
def use_networkx_n_altair_visualization(nx_graph, saveas=''):
    funct_name = 'use_networkx_n_altair_visualization()'
    print('Entering ' + funct_name + '...')
    alt.data_transformers.disable_max_rows()
    pos = nx.spring_layout(nx_graph)
    # Add attributes to each node.
    for n in nx_graph.nodes():
        nx_graph.nodes[n]['name'] = n

    viz = nxa.draw_networkx(G=nx_graph, pos=pos, node_label='name')# note: , with_labels=True is for networkx, not nx_altair
    viz = viz.properties(height = 700, width = 700)
#plt.show()
    if saveas:
        viz.save(saveas)
    alt_view.show(viz)
    print('\tDone.')
    viz.interactive()

def print_lu1983_dict():
    if not lu1983_dict:
        readin_lu_1983_data()
    for k in lu1983_dict:
        print(k + ': ' + lu1983_dict[k])

def remove_dupes(data):
    try:
        data = data.split(' ')
    except AttributeError:
        x = 1 # if this error happpens, then 'data' is a list
    if len(data) > 1:
        x = 1
    data = list(set(data))
    retval = ' '.join(data)
    return retval

#'donᴮ/ᶜ duɑnᴮ/ᶜᴬ'
def handle_a_slash_c(line):
    return handle_x_slash_y(line, 'ᴬ', 'ᶜ')

def handle_b_slash_c(line):
    return handle_x_slash_y(line,'ᴮ', 'ᶜ')

def handle_x_slash_y(line, x, y):
    line = line.split(' ')
    retval = ''
    for e in line:
        if x + '/' + y in e:
            base = e.replace(x + '/' + y, '')
            retval += base + x + ' ' + base + y + ' '
        else:
            retval += e + ' '
    return retval.strip()

# (ᶜ)(ᴮ)
def handle_paren_b(line):
    return handle_paren_x(line, '(ᴮ)')

def handle_paren_c(line):
    return handle_paren_x(line, '(ᶜ)')

def handle_paren_x(line, x):
    line = line.split(' ')
    retval = ''
    for e in line:
        if x in e:
            base = e.replace(x, '')
            xp = x.replace('(','')
            xp = xp.replace(')', '')
            retval += base + ' ' + base + xp + ' '
        else:
            retval += e + ''
    return retval.strip()

def get_schuessler_late_han_addendum_data(is_verbose=False):
    funct_name = 'get_schuessler_late_han_addendum_data()'
    input_file = os.path.join(filename_storage.get_phonological_data_dir(), 'missing_schuessler_char_list3.txt')
    if not if_file_exists(input_file, funct_name):
        return
    line_list = readlines_of_utf8_file(input_file)
    retval = {}
    for ll in line_list:
        ll = ll.split('\t')
        entry = ll[0]
        lhan = ll[2]
        if entry not in retval:
            retval[entry] = []
        if lhan.strip() and lhan not in retval[entry]:
            retval[entry].append(lhan)
        if is_verbose:
            print(ll)
    return retval

def test_schuessler_phonological_data():
    funct_name = 'test_schuessler_phonological_data()'
    schuessler = sch_glyph2phonology()
    schuessler.print_all_ocm()

def test_distance_between_tags():
    funct_name = 'test_distance_between_tags()'
    print(funct_name + ' Welcome!')
    test_str = ['篡: *tshrôns *tshrâu-ns)', '夷: *pit *l(ə)i *li', '綴: *trot(s)', '并: *peŋ(h)', '艾: *ŋâ(t)s *ŋa(t)s',
                '耙: *brâ(h)']
    start_tag = '('
    stop_tag = ')'
    for ts in test_str:
        ts = ts.split(': ')[1]
        print('distance_between_tags(' + start_tag + ', ' + stop_tag + ', ' + ts + ') returns:')
        print('\t' + str(distance_between_tags(start_tag, stop_tag, ts)))

def distance_between_tags(start_tag, stop_tag, line):
    spos = line.find(start_tag)
    epos = line.find(stop_tag)
    retval = 0
    if not line.strip():
        return retval
    if spos > 1 and epos > 1:
        retval = epos - spos + 1
    return retval

def test_handle_short_parens():
    funct_name = 'handle_short_parens()'
    print(funct_name + ' Welcome!')
    test_str = ['篡: *tshrôns *tshrâu-ns)', '夷: *pit *l(ə)i *li', '綴: *trot(s)', '并: *peŋ(h)', '艾: *ŋâ(t)s *ŋa(t)s',
                '耙: *brâ(h)']
    for ts in test_str:
        ts = ts.split(': ')[1]
        print('handle_short_parens(' + ts + ') returns \'' + handle_short_parens(ts) + '\'')

def handle_short_parens(data):
    start_tag = '('
    stop_tag = ')'
    retval = []
    if start_tag in data and stop_tag in data:
        data = data.split(' ')
        for d in data:
            if distance_between_tags(start_tag, stop_tag, d) == 3:
                begin_syl = d.split(start_tag)[0]
                middle = d.split(start_tag)[1]
                middle = middle.split(stop_tag)[0]
                end_syl = d.split(stop_tag)[1]
                retval.append(begin_syl+end_syl)
                retval.append(begin_syl+middle+end_syl)
            else:
                retval.append(d)
        retval = list(set(retval))
    else:
        retval.append(data)
    return ' '.join(retval)

class kmss_mirror_data:
    def __init__(self):
        self.line_return = '\n'
        self.delim = '\t'
    def zero_out_data(self):
        self.orig_id = ''
        self.soas_id = ''
        self.insc_name = ''
        self.name_in_source = ''
        self.diam_cm = ''
        self.weight_g = ''
        self.m_value = ''
        self.excav_info = ''
        self.poem = []
        self.commentary = []
    def set_data(self, orig_id, soas_id, insc_name, name_in_source, diam_cm, weight_g, m_value, excav, poem, commentary):
        self.orig_id = orig_id
        self.soas_id = soas_id
        self.insc_name = insc_name
        self.name_in_source = name_in_source
        self.diam_cm = diam_cm
        self.weight_g = weight_g
        self.m_value = m_value
        self.excav_info = excav # unprocessed:, just the < ... > data
        self.poem = poem[:]
        self.commentary = commentary[:]

    def get_print_str(self):
        msg = ''
        msg += 'SOAS_id = ' + self.soas_id + ',\norig_ID = ' + self.orig_id + ',\ninscription name = ' + self.insc_name
        msg += ',\nname_in_source = ' + self.name_in_source + ',\ndiam (cm) = ' + self.diam_cm + ',\nweight (g) = '
        msg += + self.weight_g + ',\nexcavation info = ' + self.excav_info + ',\nPOEM: ' + '\n\t'.join(self.poem)
        msg += '\ncommentary = ' + '\n\t'.join(self.commentary)
        return msg

    def print(self):
        print(self.get_print_str())


def edit_kyomeishusei2015_han_mirror_data():
    funct_name = 'edit_kyomeishusei2015_han_mirror_data()'
    mirrors_dir = filename_storage.get_mirrors_dir()
    base_dir = os.path.join(mirrors_dir, 'raw', 'txt')
    src = os.path.join(base_dir, 'kyomeishusei2015_03.txt')
    dst = os.path.join(base_dir, 'kyomeishusei2015_03.old.txt')

    if not os.path.isfile(dst):
        os.rename(src, dst)
    input_file = dst
    output_file = src
    line_list = readlines_of_utf8_file_for_mirror_data(input_file)
    for ll in line_list:
        if '◆〔' in ll:
            ll = ll.replace('◆〔', '◆\n〔')
        append_line_to_utf8_file(output_file, ll)

# Known errors in the raw mirror data:
# 00192: there's an extra 、 in 「長保二親、。」
# 00485: an extra ＊ in 「上辟彔＊。」
# NOTE: this function should actually be called parse_kyomeishusei2015_han_mirror_data()
def readin_kyomeishusei2015_han_mirror_data():
    funct_name = 'readin_kyomeishusei2015_han_mirror_data()'
    known_errors = ['◎華氏作竟冝矦王。家當大富樂未央。子孫備具居前行。長保二親、。辟邪含和除凶。所未得。仙人王僑赤松子。食兮。']
    mirrors_dir = filename_storage.get_mirrors_dir()

    base_dir = os.path.join(mirrors_dir, 'raw', 'txt')
    output_file = os.path.join(mirrors_dir, 'parsed_kyomeishusei2015_03.txt')
    if os.path.isfile(output_file):
        os.remove(output_file)
    # note: the data file is 03
    input_file = os.path.join(base_dir, 'kyomeishusei2015_03.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid file: ' + input_file)
        return []
    output_labels = ['SOAS ID', 'Original Poem#', 'Inscription Name', 'Insc. Name in Source', 'Data Source',
                     'Physical Info','Inscription','Commentary']
    append_line_to_utf8_file(output_file, '\t'.join(output_labels))
    line_list = readlines_of_utf8_file_for_mirror_data(input_file)
    start_tag = '《漢三國西晉鏡銘集成 00001》'
    start_looking = False
    unique_id = ''
    orig_id = ''
    id2inscription = {}
    current_id = ''
    commentary = ''
    delim = '\t'
    for ll in line_list:
        if ll.strip().isdigit():
            continue # ignore page numbers
        ll = ll.strip()
        if start_tag in ll:
            start_looking = True
        if start_looking:
            if '《漢三國西晉鏡銘集成 ' in ll:
                ll = ll.split('》')
                orig_id = ll[0] + '》'
                unique_id = ll[0].replace('《漢三國西晉鏡銘集成 ', 'kyomeishusei2015.')
                data_source = '◆' + ll[1].replace('◆', '').strip() + '◆'
            elif '《Ⅱ漢三國西晉鏡銘集成 ' in ll:
                ll = ll.split('》')
                unique_id = ll[0].replace('《Ⅱ漢三國西晉鏡銘集成 ', 'kyomeishusei2015.')
            elif ll and '〔' == ll[0]:
                inscription_name = ll.split('〕[')[0] + '〕'
                if '對置式神獸鏡' in inscription_name:
                    x = 1
                try:
                    name_in_source = '[' + ll.split('〕[')[1].split('］')[0] + ']'
                    physical_info = (ll.split('〕[')[1].split('］')[1]).strip()
                    physical_info.replace('\t', ' ')
                except IndexError as ie:
                    #print(unique_id + ' has some irregularities. Skipping.')
                    #continue
                    x = 1
            elif ll and '◎' in ll:
                orig_ll = ll
                try:
                    inscription = ll.split('◎')[1].strip()
                    inscription = inscription.split('（')  # get rid of commentary like （註）異體字銘帶 鏡Ⅱ式では「精」につくり，
                    if len(inscription) > 1:
                        commentary = '（' + inscription[1]
                    else:
                        commentary = ''
                    inscription = inscription[0]
                except IndexError as ie:
                    x = 1
                inscription = remove_num_from_end_of_str_if_there_is_one(inscription)
                # replace all ・ with □
                inscription = inscription.replace('・', '□')
                if '(註)' in inscription:
                    inscription = inscription.split('(註)')[0]
                if '；' in inscription:
                    inscription = inscription.split('；')[0]
                if '，｢半圓方形帶」' in inscription:
                    inscription = inscription.split('，｢半圓方形帶」')[0] + '。'
                if any_kana_in_string(inscription):
                    continue

                #
                # Remove unusual characters (most of these are due to the mirror data)
                # Need to write a function that removes stuff between different types of parens
                character_oddities = ['「', '」', '[', ']', '(榜題)', '＜', '>', '【缺】', '【下缺】','【不明】', '【魚文】',
                                      ' e ', ' e', 'Ⅱ', '〔不明）', '〔延年益壽〕', '(？)', '［後漢鏡銘集釋七三四〕',
                                      '［後漢鏡銘集釋六〇九〕', '〔陳介祺藏古拓本選編	銅鏡卷 094〕', '〔方格 4 字×4 方格。〕']
                if any(c in inscription for c in character_oddities):
                    for oddity in character_oddities:
                        inscription = inscription.replace(oddity, '')

                if unique_id not in id2inscription:
                    id2inscription[unique_id] = ''

                id2inscription[unique_id] = inscription

                #if len(id2inscription[unique_id]) > 1:
                #    x = 1
                line_out = unique_id + delim + orig_id + delim + inscription_name + delim + name_in_source + delim
                line_out += data_source + delim + physical_info + delim + inscription + delim + commentary
                append_line_to_utf8_file(output_file, line_out)
                #if '00136' in unique_id:
                #    x = 1
                unique_id = ''
                orig_id = ''
                inscription_name = ''
                data_source = ''
                name_in_source = ''
                physical_info = ''
                inscription = ''
                if 0 and inscription.count('。') == 5:
                    print(unique_id + ' (' + str(inscription.count('。')) + ')' + add_late_han_before_each_period(inscription))
    return id2inscription

def any_kana_in_string(line):
    retval = False
    for l in line:
        if is_kana_letter(l):
            retval = True
            break
    return retval

def add_late_han_before_each_period(line):
    if '。' not in line:
        return line
    line = line.split('。')
    retval = ''
    for s in line:
        if not s.strip():
            continue
        last_char = s[len(s)-1]
        if last_char in ['兮','也']:
            exp_char = last_char
            last_char = s[len(s)-2]
            s = s[0:len(s)-1]
            late_han = get_schuessler_late_han_for_glyph(last_char)
            retval = s + '(' + late_han + ')' + exp_char + '。'
            continue
        late_han = get_schuessler_late_han_for_glyph(last_char)
        retval += s + '(' + late_han + ')。'
    return retval

def remove_num_from_end_of_str_if_there_is_one(line):
    if not line.strip():
        return line
    pos = line.rfind('。')
    # if last 。 is the end of the string, then 沒事!
    if pos == len(line)-1:
        return line
    rightmost_part = line.split('。')
    rightmost_part = rightmost_part[len(rightmost_part)-1]
    get_rid_of_this_part = False
    for c in rightmost_part:
        if c.isdigit():
            get_rid_of_this_part = True
            line = line.split('。')
            line = '。'.join(line[0:len(line)-1])
            break
    return line

# purpose:
#   - to convert the Chinese numbers as they appear in '毛遠明 《漢魏六朝碑刻校注》第一冊.txt' and  '毛遠明 《漢魏六朝碑刻校注》第二冊.txt'
#   WILL NOT WORK FOR ALL Chinese numbers!!!
zh2ara_dict = {'〇':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':1}
def convert_zh_num2ara_num(zh_num, num_digits='03'):
    funct_name = 'convert_zh_num2ara_num'
    retval = ''
    for inc in range(0, len(zh_num), 1):
        #print(str(inc) + ' : ' + zh_num[inc])
        retval += str(zh2ara_dict[zh_num[inc]])
    retval = f"{int(retval):{num_digits}}"
    return retval

class single_stele:
    def __init(self):
        self.zero_out_data()
    def add_entry(self, unique_id, stele_name, zh_date, western_year, page_num):
        funct_name = 'add_entry()'
        self.zero_out_data()
        self.unique_id = unique_id
        self.stele_name = stele_name
        self.zh_date = zh_date
        self.western_year = western_year
        self.page_num = page_num

    def zero_out_data(self):
        self.unique_id = ''
        self.stele_name = ''
        self.zh_date = ''
        self.western_year = ''
        self.page_num = ''
        self.delim = '\t'
        self.poem_content = []

    def get_poem_id(self):
        return self.unique_id

    def add_poem_content(self, line):
        self.poem_content.append(line)

    def get_display_str(self):
        delim = self.delim
        msg = self.unique_id + delim + self.stele_name + delim + self.zh_date + delim + self.western_year
        msg += delim + self.page_num + delim + '\n'.join(self.poem_content)
        return msg

    def get_output_str_for_parsed_data_file(self):
        delim = self.delim
        msg = self.unique_id + delim + self.stele_name + delim + self.zh_date + delim + self.western_year
        msg += delim + self.page_num + delim + ' backslash_n '.join(self.poem_content)
        return msg

    def get_poem_content(self):
        return self.poem_content[:]

    def get_poem_content_as_str(self):
        #use_old = False
        #if use_old:
        #    joiner = ' '
        #    if '。' in ''.join(self.poem_content):
        #        joiner = '。'
        #    return joiner.join(self.poem_content)
        #else:
        joiner = ' '
        x = self.poem_content
        if '。' in ''.join(self.poem_content): # this is a sign that the poem is not punctuated
            joiner = ''
        return joiner.join(self.poem_content)

    def remove_last_line_of_poem_if_blank(self):
        while not self.poem_content[len(self.poem_content)-1].strip():
            self.poem_content.pop()

class stelae_data:
    def __init__(self):
        self.uniq2data_dict = {}
        self.n_rhyme_words = []
        self.rhyme_net = rnetwork('stelae_data::rhyme_net')

    def get_uniq2data_dict(self):
        return self.uniq2data_dict

    def remove_last_poem_line_if_blank(self, unique_id):
        if unique_id in self.uniq2data_dict:
            self.uniq2data_dict[unique_id].remove_last_line_of_poem_if_blank()

    def add_stele(self, unique_id, stele_name, zh_date, western_year, page_num):
        if unique_id not in self.uniq2data_dict:
            self.uniq2data_dict[unique_id] = single_stele()
        self.uniq2data_dict[unique_id].add_entry(unique_id, stele_name, zh_date, western_year, page_num)

    def add_poem_content(self, unique_id, line):
        if unique_id not in self.uniq2data_dict:
            print('stelae_data::add_poem_content() ERROR: ' + unique_id + ' not recognized!')
            return
        self.uniq2data_dict[unique_id].add_poem_content(line)

    def get_output_str_for_parsed_data_file_for_single_stele(self, unique_id):
        if unique_id not in self.uniq2data_dict:
            print('stelae_data::get_display_str_for_single_stele() ERROR: ' + unique_id + ' not recognized!')
            return ''
        return self.uniq2data_dict[unique_id].get_output_str_for_parsed_data_file()

    def get_display_str_for_single_stele(self, unique_id):
        if unique_id not in self.uniq2data_dict:
            print('stelae_data::get_display_str_for_single_stele() ERROR: ' + unique_id + ' not recognized!')
            return ''
        return self.uniq2data_dict[unique_id].get_display_str()

    def print_all_stelae(self):
        for s_id in self.uniq2data_dict:
            print(self.get_display_str_for_single_stele(s_id))

    # rhyme assumption:
    # - all words before a 。 rhyme
    def naively_get_rhyme_words(self):
        funct_name = 'naively_get_rhyme_words()'
        for s_id in self.uniq2data_dict:
            poem = self.uniq2data_dict[s_id].get_poem_content()
            rw_words = get_rhyme_words_from_stele_inscription(s_id, poem)
            if rw_words: # if there are any rhyme words...
                #
                # add Nodes
                for rhyme_word in rw_words:
                    self.rhyme_net.add_node(rhyme_word, '1', '\n'.join(poem))
                    weight = self.rhyme_net.get_node_weight(rhyme_word)
                #
                # add Edges
                for left_inc in range(0, len(rw_words), 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, len(rw_words), 1):
                        rhyme_num = s_id
                        msg += s_id + ': '
                        msg += rw_words[left_inc] + ':' + rw_words[right_inc] + ', num_rhymes_same_type = '
                        msg += str(len(rw_words)) + ', poem_stanza_num = ' + rhyme_num
                        msg = ''
                        self.rhyme_net.add_edge(rw_words[left_inc], rw_words[right_inc], len(rw_words), rhyme_num)
                        edge_weight = self.rhyme_net.get_edge_weight(rw_words[left_inc], rw_words[right_inc])

# this is based on the naive assumption that each line rhymes (i.e., last word before 。)
def get_rhyme_words_from_stele_inscription(unique_id, line_list, use_unpunctuated=False):
    funct_name = 'get_rhyme_words_from_stele_inscription()'
    punct_list = ['。', '，']
    retval = []
    for line in line_list: # this line_list represents an entire inscription
        if '；' in line:
            line = line.replace('；', '。') # treat ; just like 。
        if use_unpunctuated and '，' not in line and '。' not in line: # handle unpunctuated case
            return retval
        elif 0 and '，' in line: # handle ...，...，...。 case
            if line.count('。') > 1:
                print(funct_name + ' UNUSUAL situation. ' + unique_id + ' has both 「，」、「。」 AND ')
                print('\tmore than one 「。」')
                return retval
            line = line.replace('。', '')
            line = line.split('，')
            for i in line:
                last_char = grab_last_character_in_line(i)
                if '・' in last_char or '…' in last_char or '□' in last_char:
                    continue
                if last_char.strip() and last_char not in retval:
                    retval.append(last_char)
        elif '。' in line: # handle ...。...。...。 case
            line = line.split('。')
            for i in line:
                last_char = grab_last_character_in_line(i)
                if '・' in last_char or '…' in last_char or '□' in last_char:
                    continue
                if last_char.strip() and last_char not in retval:
                    retval.append(last_char)
    if len(retval) == 1:
        retval = [] # can't have just one rhyme word
    return retval

# this is based on the naive assumption that each line rhymes (i.e., last word before 。)
def get_numbered_rhyme_words_from_stele_inscription(unique_id, line_list, use_unpunctuated=False):
    funct_name = 'get_numbered_rhyme_words_from_stele_inscription()'
    punct_list = ['。', '，']
    is_verbose = False
    retval = {}
    rw_cnt = 0
    msg = ''
    line_cnt = -1
    for line in line_list: # this line_list represents an entire inscription
        msg = 'For line: \'' + line + '\', the rhymes are \n'
        last_char = ''
        char_pos = ''
        line_cnt += 1
        if not line.strip():
            continue
        if '；' in line:
            line = line.replace('；', '。') # treat ; just like 。
        if use_unpunctuated and '，' not in line and '。' not in line: # handle unpunctuated case
            return retval
        elif '。' in line: # handle ...。...。...。 case
            line = line.split('。')
            line.pop()  # get rid of '' artifact
            for sub_line in line: # for each section that ends with '。'
                if not sub_line.strip():
                    if line_cnt not in retval:
                        retval[line_cnt] = {}
                    if rw_cnt not in retval[line_cnt]:
                        retval[line_cnt][rw_cnt] = []
                    retval[line_cnt][rw_cnt].append(('', -1, sub_line))
                    rw_cnt += 1
                    msg += '\t' + sub_line + '( No rhyme )\n'
                    continue
                try:
                    last_char, char_pos = grab_last_character_in_line(sub_line)
                except ValueError as ve:
                    x = 1
                if '・' in last_char or '…' in last_char or '□' in last_char:
                    if line_cnt not in retval:
                        retval[line_cnt] = {}
                    if rw_cnt not in retval[line_cnt]:
                        retval[line_cnt][rw_cnt] = []
                    retval[line_cnt][rw_cnt].append(('', -1, sub_line))
                    rw_cnt += 1
                    last_char = ''
                    char_pos = ''
                    msg += '\t' + sub_line + '( No rhyme )\n'
                    continue
                if last_char.strip() and last_char not in retval:
                    if line_cnt not in retval:
                        retval[line_cnt] = {}
                    if rw_cnt not in retval[line_cnt]:
                        retval[line_cnt][rw_cnt] = []
                    retval[line_cnt][rw_cnt].append((last_char, char_pos, sub_line))
                    rw_cnt += 1
                    msg += '\t' + sub_line + ' (' + last_char + ', ' + str(char_pos) + ')\n'
        if is_verbose:
            print(msg)
    if len(retval) == 1:
        try:
            if len(retval[0]) == 1:
                retval = {} # can't have just one rhyme word
        except:
            x = 1
    return retval

def process_mao_2008_stelae_data(is_verbose=False):
    funct_name = 'process_mao_2008_stelae_data()'
    # s_data is a stelae_data object
    s_data = parse_mao_2008_stelae_data(is_verbose)
    s_data.naively_get_rhyme_words()
    s_data.output_naive_annotation()

def readin_parsed_mao_2008_stelae_data():
    funct_name = 'readin_parsed_mao_2008_stelae_data()'
    input_file = filename_storage.get_parsed_mao_2008_stelae_data_file()
    retval = {}
    if not if_file_exists(input_file, funct_name):
        message2user(funct_name + ' ERROR: Input file does NOT exist: ' + input_file)
        return []
    data = readlines_of_utf8_file(input_file)
    labels = data[0]
    data = data[2:len(data)] # remove labels and comment
    poem_pos = 5
    id_pos = 0
    for d in data:
        d = d.split('\t')
        poem_id = d[id_pos]
        poem = d[poem_pos].replace(' backslash_n ', '\n')
        if poem_id not in retval:
            retval[poem_id] = ''
        retval[poem_id] = poem
    return retval
#
# Rhyme assumption for the stelae data:
# each line rhymes
def parse_mao_2008_stelae_data(use_test_data=False, is_verbose=False):
    funct_name = 'parse_mao_2008_stelae_data()'
    labels = ['Soas-Unique-ID', 'Stele-Name', 'Chinese-Date', 'Western-Year', 'Page-#', 'Poem']
    base_num_list = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if not use_test_data:
        input_file1 = filename_storage.get_mao_2008_stelae_data_input_file1()
        input_file2 = filename_storage.get_mao_2008_stelae_data_input_file2()

        if not os.path.isfile(input_file1):
            print(funct_name + ' ERROR: Invalid file: ' + input_file1)
            return []
        if not os.path.isfile(input_file2):
            print(funct_name + ' ERROR: Invalid file: ' + input_file2)
            return []
        output_file = os.path.join(filename_storage.get_stelae_dir(), 'parsed_毛遠明 《漢魏六朝碑刻校注》.txt')
    else: # for TESTING
        output_file = os.path.join(filename_storage.get_stelae_dir(), 'testing_parsed_毛遠明 《漢魏六朝碑刻校注》.txt')
        input_file = os.path.join(filename_storage.get_stelae_dir(), 'test_data.txt')

    if os.path.isfile(output_file):
        os.remove(output_file)
    append_line_to_utf8_file(output_file, '\t'.join(labels))
    append_line_to_utf8_file(output_file, '# IMPORTANT: Convert \' backslash_n \' to \'\\n\' or \'\\r\\n\' depending on your system.' )
    if not use_test_data:
        line_list1 = readlines_of_utf8_file(input_file1)
        line_list2 = readlines_of_utf8_file(input_file2)
        line_list = line_list1 + line_list2
    else: # For Testing
        line_list = readlines_of_utf8_file(input_file)
    mou_unique = ''
    delim = '\t'
    start_new_poem = False
    poem_content = []
    pos = -1
    line_list_len = len(line_list)
    stele_dict = stelae_data()
    stop_reading_tag = '三国·魏'

    comment_indicator = '#'
    for ll in line_list:
        if ll.strip() and ll.strip()[0] == comment_indicator:
            continue # skip over comments
        pos += 1
        if stop_reading_tag in ll:
            break
        if '：' in ll: # new entry
            ll = ll.split('：')
            # if the beginning of a poem section
            if any(zh_num in ll[0] for zh_num in base_num_list):
                # if previous poem exists, print it
                if poem_content:
                    for l in poem_content:
                        if is_verbose:
                            print(l)
                if mou_unique:
                    stele_dict.remove_last_poem_line_if_blank(mou_unique)
                start_new_poem = True
                poem_content = []
                zh_num = ll[0].strip()
                if '《' in ll[1]: # type A parsing
                    stele_name = ll[1].split('》')[0] + '》'
                    date_data = ll[1].split('，')
                    try:
                        page_num = date_data[2].lower()
                    except IndexError as ie:
                        page_num = ''
                    try:
                        date_data = date_data[1]
                    except IndexError as ie:
                        x = 1
                    zh_date_year = date_data.split('（')[0]
                    western_year = date_data.split('（')[1]
                    western_year = western_year.split('）')[0]
                    zh_date_month = date_data.split('）')[1]
                else: # type B parsing
                    page_num = ''
                    right_side_data = ll[1].split('　')
                    stele_name = '《' + right_side_data[0] + '》'
                    try:
                        date_data = right_side_data[1]
                    except:
                        date_data = ''
                    if '（' in date_data:
                        date_data = date_data.split('（')
                        zh_date_year = date_data[0]
                        western_year = date_data[1].split('）')[0]
                        zh_date_month = date_data[1].split('）')[1]
                ara_num = convert_zh_num2ara_num(zh_num) # arabic number
                mou_unique = 'Mou2008.' + ara_num
                msg = mou_unique + delim + zh_num + '：' + stele_name + '，' + zh_date_year + '（' + western_year
                msg += '）' + zh_date_month
                stele_dict.add_stele(mou_unique, stele_name, zh_date_year + zh_date_month, western_year, page_num)
                if page_num:
                    msg += '，' + page_num
                if is_verbose:
                    print(msg)
                start_new_poem = False
            else:
                poem_content.append('X'.join(ll))
                stele_dict.add_poem_content(mou_unique,'：'.join(ll))
        else:
            if ll:
                poem_content.append(ll)
                stele_dict.add_poem_content(mou_unique,ll)
            else:
                if ll == '':
                    if poem_content and poem_content[len(poem_content)-1] != '': # don't add two empty lines in a row
                        poem_content.append(ll)
                        stele_dict.add_poem_content(mou_unique, ll)
    # print out last poem
    for l in poem_content:
        if is_verbose:
            print(l)
        if stop_reading_tag not in ll:
            stele_dict.add_poem_content(mou_unique, ll)
    uniq2data_dict = stele_dict.get_uniq2data_dict()
    for k in uniq2data_dict:
        output_msg = stele_dict.get_output_str_for_parsed_data_file_for_single_stele(k)
        append_line_to_utf8_file(output_file, output_msg)
        print(output_msg)
    return stele_dict

def test_get_schuessler_late_han_for_glyph(glyph_list):
    for glyph in glyph_list:
        retval = get_schuessler_late_han_for_glyph(glyph)
        print(glyph + ': ' + retval)

def test_is_hanzi():
    test_chars = ['a', '今', 'は', '𪛂', '1']
    for tc in test_chars:
        if is_hanzi(tc):
            print(tc + ' IS a hanzi!')
        else:
            print(tc + ' is NOT a hanzi!')

def is_multibyte_unicode(test_ord):
    retval = False
    if test_ord >= '\U00020000' and test_ord <= '\U0002a6d6':
        retval = True
    # U+2F800..U+2FA1D : CJK Compatibility Supplement
    elif test_ord >= '\U0002f800' and test_ord <= '\U0002fa1d':
        retval = True
    elif test_ord >= '\U0001f200' and test_ord <= '\U0001f2ff':
        retval = True
    return retval

def get_raw_bentley_2015_filename():
    return os.path.join(filename_storage.get_soas_code_dir(),'hanproj','phonological_data', 'raw','bentley_2015.txt')

def get_parsed_bentley_2015_late_han_data():
    funct_name = 'get_parsed_bentley_2015_late_han_data()'
    input_file = os.path.join(filename_storage.get_soas_code_dir(),'hanproj','phonological_data','parsed_bentley_2015_late_han_data.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file: ' + input_file)
        print('\tAborting.')
        return {}
    line_list = readlines_of_utf8_file(input_file)
    retval = {}
    for ll in line_list:
        ll = ll.split('\t')
        if ll[0] not in retval:
            retval[ll[0]] = ''
        retval[ll[0]] = ll[1]
    return retval

def parse_bentley_2015(is_verbose=False):
    funct_name = 'parse_bentley_2015()'
    start_tag ='geographical list of provinces, districts, and villages, often with'
    input_file = get_raw_bentley_2015_filename()
    output_file = os.path.join(filename_storage.get_soas_code_dir(),'hanproj','phonological_data','parsed_bentley_2015_late_han_data.txt')
    if os.path.isfile(output_file):
        os.remove(output_file)
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file:')
        print('\t' + input_file)
        print('\tAborting.')
        return {}
    start_reading = False
    line_list = readlines_of_utf8_file(input_file)
    retval = {}
    hanzi = ''
    late_han = ''
    included_chars = []
    exceptions = ['kah MC: kɛ: GO: ke KN: ka', 'kah MC: kɛ: GO: kai KN: ka', 'śas MC: śjäih GO: se KN: sei'
        , 'ŋɑ MC: ŋɔ GO: gu KN: go']
    for ll in line_list:
        if not ll.strip():
            continue
        if start_tag in ll:
            start_reading = True
            if is_verbose:
                print('start reading')
        if start_reading:
            potential_hanzi = ll.strip()
            if is_hanzi(potential_hanzi) and len(potential_hanzi) == 1:
                hanzi = potential_hanzi
                if hanzi not in retval:
                    retval[hanzi] = []
                continue
            if 'LH: ' in ll and hanzi:
                late_han = ll.split('LH: ')[1]
                if '*kie > ' in late_han:
                    late_han = late_han.replace('*kie > ', '')
                if 'EMC' in late_han:
                    late_han = late_han.split('EMC')[0]
                else:
                    late_han = late_han.split('MC')[0]
                late_han = late_han.replace('NA','')
                late_han = late_han.replace(' or ', ' ')
                late_han = late_han.replace(',','')
                late_han = late_han.replace(' > ', ' ')
                late_han = late_han.replace(' < ', ' ')
                late_han = late_han.replace(' / ', ' ')
                late_han = late_han.replace('~', ' ')
                late_han = late_han.replace('th', 'tʰ')
                late_han = late_han.replace('ph', 'pʰ')
                if '(' in late_han:
                    root = late_han.split('(')[0]
                    ending = late_han.split('(')[1]
                    ending = ending.replace(')','')
                    if 'h/ʔ' not in ending:
                        late_han = root + ' ' + root + ending
                    else:
                        late_han = root + ' ' + root + 'h ' + root + 'ʔ'
                if late_han == 'NA' or not late_han.strip():
                    late_han = ''
                if hanzi and late_han:
                    if ' ' in late_han:
                        for lh in late_han.split(' '):
                            if lh.strip() and lh.strip() not in retval[hanzi]:
                                retval[hanzi].append(lh.strip())
                    else:
                        if late_han and late_han not in retval[hanzi]:
                            retval[hanzi].append(late_han.strip())
                    hanzi = ''
                    late_han = ''
    for hz in retval:
        if len(retval[hz]) > 1:
            hz_set = list(set(retval[hz])) # get rid of dupes
            if len(hz_set) < len(retval[hz]):
                retval[hz] = []
                retval[hz] = hz_set[:]
    has_late_han = []
    no_late_han = []
    for hz in retval:
        msg_out = hz + '\t' + ' '.join(retval[hz])
        append_line_to_utf8_file(output_file, msg_out)
        if ''.join(retval[hz]).strip():
            if hz not in has_late_han:
                has_late_han.append(hz)
        else:
            if hz not in no_late_han:
                no_late_han.append(hz)
        if is_verbose:
            print(hz + ': ' + ', '.join(retval[hz]))
    if is_verbose:
        print(str(len(retval)) + ' total entries in Bentley 2015.')
        print('\t' + str(len(has_late_han)) + ' of them have Han data.')
        print('\t' + str(len(no_late_han)) + ' of them do NOT have Han data.')
    if '埃' in retval:
        retval['埃'] = 'ʔə'
    return retval

def readin_preparsed_schuessler_late_han_data():
    funct_name = 'readin_preparsed_schuessler_late_han_data()'
    input_file = os.path.join(filename_storage.get_hanproj_dir(), 'phonological_data', 'parsed_schuessler_2007_data.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file: ' + input_file)
        print('\tAborting.')
        return {}
    retval = {}
    line_list = readlines_of_utf8_file(input_file)
    line_list = line_list[1:len(line_list)] # skip over the labels
    for ll in line_list:
        if '#' in ll:
            ll = ll.split('#')[0]
            if not ll.strip():
                continue # skip over comment line
        entry = ll.split('\t')[0]
        data = ll.replace(entry + '\t','').split('NEW_ENTRY')
        if entry not in retval:
            retval[entry] = []
        for d in data:
            retval[entry].append(d)
    return retval

def create_schuessler_late_han_data_file():
    funct_name = 'create_schuessler_late_han_data_file()'
    schuessler = get_schuessler_late_han_data()
    output_file = os.path.join(filename_storage.get_hanproj_dir(), 'phonological_data', 'parsed_schuessler_2007_data.txt')
    data_str = ''
    if os.path.isfile(output_file): # if the output file already exists, delete it
        os.remove(output_file)
    label_list = ['wf_graph','wf_pinyin', 'QY_IPA', 'LH_IPA', 'OCM_IPA']
    note = '#important: data types (pinyin, qy_ipa, etc.) are tab (\\t) separated.'
    note += '\'NEW_ENTRY\' separates different sets of pronunciation for the same character.'
    append_line_to_utf8_file(output_file, '\t'.join(label_list))
    append_line_to_utf8_file(output_file, note)
    if 1:
        for s in schuessler:
            data_str = ''
            for e in schuessler[s]:
                data_str += e + 'NEW_ENTRY'
            data_str = data_str[0:len(data_str)-len('NEW_ENTRY')] # get rid of last space
            append_line_to_utf8_file(output_file, s + '\t' + data_str)

def test_get_schuessler_plus_bentley_2015():
    print('Get Schuessler data...')
    schuessler = get_schuessler_late_han_data()
    print('\tDone.')
    print('Get Bentley data...')
    bentley = parse_bentley_2015()
    print('\tDone.')
    print('Get Schuessler plus...')
    schuessler_plus = get_schuessler_plus_bentley_2015()
    print('\tDone.')
    print('len(schuessler) = ' + str(len(schuessler)) + ', len(bentley) = ' + str(len(bentley)))
    print('\tlen(schuessler_plus) = ' + str(len(schuessler_plus)))

def get_schuessler_plus_bentley_2015():
    funct_name = 'get_schuessler_plus_bentley_2015()'
    schuessler = get_schuessler_late_han_data()
    bentley = parse_bentley_2015()
    retval = []
    not_in_schuessler = []
    for b in bentley:
        if b not in schuessler:
            if bentley[b] != [] and bentley[b] != ['']:
                schuessler[b] = bentley[b][:]
    return schuessler

def create_schuessler_plus_bentley_2015_file():
    funct_name = 'create_schuessler_plus_bentley_2015_file()'
    schuessler = readin_preparsed_schuessler_late_han_data()#get_schuessler_late_han_data()
    bentley = get_parsed_bentley_2015_late_han_data()#parse_bentley_2015()
    output_file = os.path.join(filename_storage.get_soas_code_dir(), 'hanproj', 'phonological_data', 'combo_schuessler2007_n_bentley2015.txt')
    if os.path.isfile(output_file):
        os.remove(output_file)
    label_list = ['wf_graph','wf_pinyin', 'QY_IPA', 'LH_IPA', 'OCM_IPA']
    note = '#important: data types (pinyin, qy_ipa, etc.) are tab (\\t) separated.'
    note += '\'NEW_ENTRY\' separates different sets of pronunciation for the same character.'
    append_line_to_utf8_file(output_file, '\t'.join(label_list))
    append_line_to_utf8_file(output_file, note)
    retval = []
    not_in_schuessler = []
    for b in bentley:
        if b not in schuessler:
            if bentley[b] != [] and bentley[b] != ['']:
                schuessler[b] = ['\t\t' + bentley[b] + '\t']
    for s in schuessler:
        data_str = 'NEW_ENTRY'.join(schuessler[s])
        append_line_to_utf8_file(output_file, s + '\t' + data_str)
        print(s + ': ' + data_str)
    return schuessler

def readin_schuessler_n_bentley_late_han_data(is_verbose=False):
    funct_name = 'readin_schuessler_n_bentley_late_han_data()'
    raw_data = readin_schuessler2007_n_bentley2015_combo() # this reads in pinyin, OC, MC and LHan
    #raw_data = raw_data[2:len(raw_data)] # skip first two lines of the file
    raw_data.pop('wf_grapʰ')
    lhan_pos = 2
    retval = {}
    for rd in raw_data:
        if '#' in rd:
            continue
        if rd not in retval:
            retval[rd] = []
        entry_data = raw_data[rd][0].split('NEW_ENTRY')
        for ed in entry_data:
            ed = ed.split('\t')
            if ed[lhan_pos].strip():
                if ed[lhan_pos] not in retval[rd]:
                    if 'list' in str(type(ed[lhan_pos])):
                        x = 1
                    retval[rd].append(ed[lhan_pos])
                if is_verbose:
                    print(rd + ': LHan = ' + ed[lhan_pos])
    return retval

def readin_schuessler2007_n_bentley2015_combo():
    funct_name = 'readin_schuessler2007_n_bentley2015_combo()'
    input_file = os.path.join(filename_storage.get_soas_code_dir(), 'hanproj', 'phonological_data', 'combo_schuessler2007_n_bentley2015.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file:' + input_file)
        print('\tAborting.')
        return {}
    retval = {}
    line_list = readlines_of_utf8_file(input_file)
    for ll in line_list:
        entry = ll.split('\t')[0]
        data = ll.replace(entry + '\t', '')
        if entry not in retval:
            retval[entry] = []
        retval[entry].append(data)
    return retval

def compare_schuessler_to_bentley_2015():
    funct_name = 'compare_schuessler_to_bentley_2015()'
    schuessler = get_schuessler_late_han_data()
    bentley = parse_bentley_2015()
    in_b_not_in_s = []
    for b in bentley:
        print(b + ': ' + ' '.join(bentley[b]))
        if b.strip() and b not in schuessler:
            if b not in in_b_not_in_s:
                in_b_not_in_s.append(b)
    print(str(len(in_b_not_in_s)) + ' entries in Bentley, but not in Schuessler.')

class schuessler_n_bentley:
    def __init__(self):
        self.raw_dict = {}#readin_schuessler2007_n_bentley2015_combo()
        self.raw_dict2 = readin_most_complete_schuessler_data()
        self.lhan_dict = {}
        self.lhan_dict2 = {}
        #self.fill_lhan_dict()
        self.fill_lhan_dict2()
        self.class_name = 'schuessler_n_bentley'

    def fill_lhan_dict2(self, is_verbose=False):
        funct_name = 'fill_lhan_dict2()'
        if not self.raw_dict2:
            print(self.class_name + '::' + funct_name + ' ERROR!')
            msg = '\tMust first run ' + self.class_name + '::'
            msg += 'readin_most_complete_schuessler_data()'
            print('\t' + msg)
            return
        for e in self.raw_dict2:
            if e not in self.lhan_dict2:
                self.lhan_dict2[e] = []
            pron = self.raw_dict2[e]
            for subpron in pron:
                subpron = subpron.split(' ')
                for p in subpron:
                    if p not in self.lhan_dict2[e]:
                        self.lhan_dict2[e].append(p)

    def fill_lhan_dict(self, is_verbose=False):
        funct_name = 'fill_lhan_dict()'
        if not self.raw_dict:
            print(self.class_name + '::' + funct_name + ' ERROR!')
            msg = '\tMust first run ' + self.class_name + '::'
            msg += 'readin_schuessler2007_n_bentley2015_combo()'
            print('\t' + msg)
            return
        pron = []
        for e in self.raw_dict:
            if not is_hanzi(e):
                if is_verbose:
                    print('Not a hanzi: ' + e)
                    print('\tSkipping.')
                continue
            edata = self.raw_dict[e][0]
            if 'NEW_ENTRY' in edata:
                edata = edata.split('NEW_ENTRY')
            else:
                edata = [edata]
            for p in edata:
                if is_verbose:
                    print(e + ': ' + p)
                p = p.split('\t')
                if is_verbose:
                    print('\tLHan: ' + p[2])
                if e.strip() and e not in self.lhan_dict:
                    self.lhan_dict[e] = []
                x = p[2]
                if p[2].strip():
                    if ' ' in p[2]:
                        pron = p[2].split(' ')
                    else:
                        pron = [p[2]]
                    for subp in pron:
                        if subp not in self.lhan_dict[e]:
                            self.lhan_dict[e].append(subp)

    def get_late_han(self, zi):
        retval = []
        if zi not in self.lhan_dict2:
            return retval
        return self.lhan_dict2[zi]

    def get_entry_list(self):
        return self.lhan_dict2.keys()

def analyze_schuessler_n_bentley_later_han():
    funct_name = 'analyze_schuessler_n_bentley_later_han()'
    lhan_dict = readin_schuessler2007_n_bentley2015_combo()
    schuessler = schuessler_n_bentley()
    entry_list = schuessler.get_entry_list()
    for e in entry_list:
        lhan = schuessler.get_late_han(e)
        for lh in lhan:
            initial, medial, final, pcoda = parse_schuessler_late_han_syllable(lh)
            msg = initial + '-'
            if medial.strip():
                msg += medial + '-'
            msg += final
            if pcoda.strip():
                msg += '-' + pcoda
            print(e + ': ' + lh + '(' + msg + ')')

def is_this_the_initial(pinitial, reco):
    return pinitial == reco[0:len(pinitial)]

def get_initial_for_schuessler_lhan(reco):
    return parse_schuessler_late_han_syllable(reco)

def insert_rhyme_marker_at_pos(line, rhyme_pos, rhyme_marker):
    if rhyme_pos == -1:
        return line
    try:
        rhyme_char = line[rhyme_pos]
    except IndexError as ie:
        rhyme_char = '・'
    if rhyme_char == '}':# '上辟彔{礻＋羽}'
        retval = ''
        if '{' in line:
            rpos = line.rfind('{')
            retval = line[:rpos] + rhyme_marker + line[rpos:]
            return retval
        else:
            return line
    if '・' in rhyme_char or '…' in rhyme_char or '□' in rhyme_char:
        return line
    if line[len(line)-1] == '）':
        rhyme_pos = line.find('（') - 1
    return line[0:rhyme_pos] + rhyme_marker + line[rhyme_pos:len(line)]

def is_compatibility_char(entry):
    funct_name = 'is_compatibility_char()'
    retval = False
    if not entry.strip():
        return retval
    if len(entry) != 1:
        return retval
    entry = ord(entry)
    if entry >= 0xf900 and entry <= 0xfaff:
        retval = True
    return retval

def get_data_from_pos(string, position, delim):
    try:
        retval = string.split(delim, position + 1)[int(position)]
    except IndexError as ie_err:
        print(ie_err)
        retval = -1
    return retval

def add_missing_schuessler_data_to_most_complete():
    funct_name = 'add_missing_schuessler_data_to_most_complete()'
    addendum = get_schuessler_late_han_addendum_data()
    output_file = os.path.join(filename_storage.get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    for k in addendum:
        msg_out = k + '\t' + ' '.join(addendum[k])
        append_line_to_utf8_file(output_file, msg_out)

def create_need_shengfu_file():
    funct_name = 'create_need_shengfu_file()'
    output_file = os.path.join(filename_storage.get_phonological_data_dir(), 'need_shengfu_file.txt')
    delete_file_if_it_exists(output_file)
    mlist = '埆韻洧鑒澎辻勛神漳驤溏紋喚巇趺痴婿廎毹尫晴鎔樣滓紜衫㲹圢暟炅榷炯皚讖蹤叺湏嬆璘𣧑𥚝鄹昶淇踏駬乕盒轃厘花沄嵗俌傐頁了瘢嗤㜰箏靂廿祑澍卅廂裡箋鄒崎篌璫㐬蒂貎稀斦祤'
    mlist = list(set(mlist))
    for m in mlist:
        append_line_to_utf8_file(output_file, m)

def combine_schuessler_bentley_n_addendum(is_verbose=False):
    funct_name = 'combine_schuessler_bentley_n_addendum()'
    addendum = get_schuessler_late_han_addendum_data()
    output_file = os.path.join(filename_storage.get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    delete_file_if_it_exists(output_file)
    snb = readin_schuessler_n_bentley_late_han_data()
    for k in addendum:
        if k not in snb:
            snb[k] = []
        add_this = ' '.join(addendum[k])
        if add_this.strip():
            snb[k].append(add_this)
    for k in snb:
        k_sub = ' '.join(snb[k])
        if not k_sub.strip():
            continue
        msg_out = k + '\t' + ' '.join(snb[k])
        if is_verbose:
            print(msg_out)
        append_line_to_utf8_file(output_file, msg_out)

def test_are_these_chars_in_most_complete_schuessler():
    funct_name = 'test_are_these_chars_in_most_complete_schuessler()'
    print(funct_name + ' Welcome!')
    char_list = '槐蹊厘濭噫滂尫沰完婿毹蒂鏘喚幬笳勉靑精神福海祥祐悔朙萠朖者節皚洤祝辻楼卅視虜彡樣祉傐湏祑盖盒廉穀㲹叺'
    char_list = list(set(char_list))
    are_these_chars_in_most_complete_schuessler(char_list)

def are_these_chars_in_most_complete_schuessler(char_list):
    funct_name = 'are_these_chars_in_most_complete_schuessler()'
    schuessler = readin_most_complete_schuessler_data()
    not_in_schuessler = []
    for c in char_list:
        if c in schuessler:
            print(c + ': ' + schuessler[c])
        else:
            not_in_schuessler.append(c)
    if not_in_schuessler:
        print(str(len(not_in_schuessler)) + ' chars are still missing Schuessler data:')
        print('\t' + ''.join(not_in_schuessler))

def test_schuessler_syllable_parser():
    fuct_name = ''
    test_data = ['ṇɑᴮ', 'ṇɑᶜ']
    for td in test_data:
        x = 1
        initial, medial, final, pcoda = parse_schuessler_late_han_syllable(td)
        print('parse_schuessler_late han_syllable(\'' + td + '\') returns \'' + final + '\'')
    is_verbose = True

def test_print_out_list_vertically():
    funct_name = 'test_print_out_list_vertically()'
    test_str = '肅肅我祖。國自豕韋。黼衣朱紱。四牡龍旗。彤弓斯征。撫寧遐荒。總齊群邦。以翼大商。迭彼大彭。勛績惟光。至於有周。歷世會同。王赧聽譖。寔絕我邦。我邦既絕。厥政斯逸。賞罰之行。非繇王室。庶尹群后。靡扶靡衛。五服崩離。宗周以隊。我祖斯微。遷於彭城。在予小子。勤誒厥生。阸此嫚秦。耒耜以耕。悠悠嫚秦。上天不寧。迺眷南顧。授漢于京。于赫有漢。四方是征。靡適不懷。萬國逌平。迺命厥弟。建侯于楚。俾我小臣。惟傅是輔。競競元王。恭儉凈壹。惠此黎民。納彼輔弼。饗國漸世。垂烈於後。迺及夷王。XX克奉厥緒。咨命不永。惟王統祀。左右陪臣。此惟皇士。如何我王。不思守保。不惟履冰。以繼祖考。邦事是廢。逸游是娛。犬馬繇繇。是放是驅。務彼鳥獸。忽此稼苗。烝民以匱。我王以偷。所弘非德。所親非俊。唯囿是恢。唯諛是信。睮睮諂夫。咢咢黃發。如何我王。曾不是察。既藐下臣。追欲從逸。嫚彼顯祖。輕茲削黜。嗟嗟我王。漢之睦親。曾不夙夜。以休令聞。穆穆天子。臨爾下土。明明群司。執憲靡顧。正遐繇近。殆其怙茲。嗟嗟我王。曷不此思。非思非鑒。嗣其罔則。瀰瀰其失。岌岌其國。致冰匪霜。致隊靡嫚。瞻惟我王。昔靡不練。興國救顛。孰違悔過。追思黃發。秦繆以霸。歲月其徂。年其逮耇。于昔君子。庶顯於後。我王如何。曾不斯覽。黃發不近。胡不時監。'
    print_out_list_vertically(test_str, '。')

def print_out_list_vertically(data, delim):
    data = data.split(delim)
    inc = 1
    rw_list = []
    for d in data:
        if not inc % 2: # handle cases with rhymes
            rhyme = d[len(d)-1]
            line = d[0:len(d)-1]
            print(line + '[' + rhyme + ']' + delim)
            rw_list.append(rhyme)
        else: # handle the rest
            if d.strip():
                print(d + delim)
        inc += 1
    print(','.join(rw_list))

# description
# the XX in the data below indicate places where '\n' belong, resulting in data like:
# line1: 大孝備矣。休德昭清。高張四縣。樂充宮庭。芬樹羽林。雲景杳冥。金支秀華。庶旄翠旌。七始華始。肅倡和聲。神來晏娭。庶幾是聽。
# line2: 粥粥音送。細齊人情。忽乘青玄。熙事備成。清思眑眑。經緯冥冥。
# line3: 我定曆數。人告其心。敕身齊戒。施教申申。乃立祖廟。敬明尊親。大矣孝熙。四極爰轃。
#
# For this configuation, the test will see how well annotation performs one a line by line basis:
# In another test, it'll be determined how well annotation performs for the entire poem, without taking lines into
# consideration
def schuessler_line_by_line_test():
    funct_name = 'schuessler_line_by_line_test()'
    test_str = '大孝備矣。休德昭清。高張四縣。樂充宮庭。芬樹羽林。雲景杳冥。金支秀華。庶旄翠旌。七始華始。肅倡和聲。神來晏娭。庶幾是聽。XX粥粥音送。細齊人情。忽乘青玄。熙事備成。清思眑眑。經緯冥冥。XX我定曆數。人告其心。敕身齊戒。施教申申。乃立祖廟。敬明尊親。大矣孝熙。四極爰轃。XX王侯秉德。其鄰翼翼。顯明昭式。清明鬯矣。皇帝孝德。竟全大功。撫安四極。XX海內有奸。紛亂東北。詔撫成飾。武臣承德。行樂交逆。簫群慝。肅為濟哉。蓋定燕國。XX大海蕩蕩水所歸。高賢愉愉民所懷。大山崔。百卉殖。民何貴。貴有德。XX安其所。樂終產。樂終產。世繼緒。飛龍秋。游上天。高賢愉。樂民人。XX豐草葽。女羅施。善何如。誰能回。大莫大。成教德。長莫長。被無極。XX雷震震。電耀耀。明德鄉。治本約。治本約。澤弘大。加被寵。咸相保。德施大。世曼壽。XX都荔遂芳。窅{宀瓜}桂華。孝奏天儀。若日月光。乘玄四龍。回馳北行。羽旄殷盛。芬哉芒芒。孝道隨世。我署文章。XX馮馮翼翼。承天之則。吾易久遠。燭明四極。XX慈惠所愛。美若休德。杳杳冥審。克綽永福。XX磑磑即即。師象山則。鳴呼孝哉。案撫戎國。蠻夷竭歡。象來致福。兼臨是愛。終無兵革。XX嘉薦芳矣。告靈饗矣。告靈既饗。德音孔臧。惟德之臧。建侯之常。承保天休。令問不忘。XX皇皇鴻明。盪侯休德。嘉承天和。伊樂厥福。在樂不荒。惟民之則。浚則師德。下民咸殖。XX令問在舊。孔容翼翼。XX孔容之常。承帝之明。下民之樂。子孫保光。承順溫良。受帝之光。嘉薦令芳。壽考不忘。XX承帝明德。師象山則。雲施稱民。永受厥福。承容之常。承帝之明。下民安樂。萬壽無疆。'
    s_annotator = schuessler_stanza_annotator()
    test_lines = test_str.split('XX') #get_rhyme_words_naively2
    linc = 0
    line_length = 0 # # not used anyway
    stanza_id = 'Lu1983.114'
    nonrw_lines_dict = {}
    every_line_rhymes = False
    for line in test_lines:
        print('='*100)
        linc += 1
        rw_words = get_rhyme_words_from_stanza(line, stanza_id, every_line_rhymes)
        s_annotator.reset()
        output_str = ''
        for rw_data in rw_words:
            rw = rw_data[0]
            rw_pos = rw_data[1]
            orig_line = rw_data[2]
            line_id = rw_data[3]
            if rw != -1:
                s_annotator.add_rhyme_word(rw, rw_pos, orig_line, line_id)
            else:
                if line_id not in nonrw_lines_dict:
                    nonrw_lines_dict[line_id] = ''
                nonrw_lines_dict[line_id] = orig_line
        s_annotated_lines = s_annotator.get_annotated_lines()
        for line_inc in s_annotated_lines:
            al = s_annotated_lines[line_inc]
            rw = al[0]
            rw_pos = al[1]
            orig_line = al[2]
            line_id = al[3]
            annotated_line= al[4]
            print(annotated_line)

# description
# the XX in the data below indicate places where '\n' belong, resulting in data like:
# line1: 大孝備矣。休德昭清。高張四縣。樂充宮庭。芬樹羽林。雲景杳冥。金支秀華。庶旄翠旌。七始華始。肅倡和聲。神來晏娭。庶幾是聽。
# line2: 粥粥音送。細齊人情。忽乘青玄。熙事備成。清思眑眑。經緯冥冥。
# line3: 我定曆數。人告其心。敕身齊戒。施教申申。乃立祖廟。敬明尊親。大矣孝熙。四極爰轃。
#
# For this configuation, the test will see how well annotation performs one entire poem basis:
# In another test, it'll be determined how well annotation performs on a line by line basis
#
# TO DO:
#  was trying to get this such that i could do visualization on nodes and edges
#  結果： it's a mess.
def schuessler_full_poem_test():
    funct_name = 'schuessler_full_poem_test()'
    full_test_str = '大孝備矣。休德昭清。高張四縣。樂充宮庭。芬樹羽林。雲景杳冥。金支秀華。庶旄翠旌。七始華始。肅倡和聲。神來晏娭。庶幾是聽。XX粥粥音送。細齊人情。忽乘青玄。熙事備成。清思眑眑。經緯冥冥。XX我定曆數。人告其心。敕身齊戒。施教申申。乃立祖廟。敬明尊親。大矣孝熙。四極爰轃。XX王侯秉德。其鄰翼翼。顯明昭式。清明鬯矣。皇帝孝德。竟全大功。撫安四極。XX海內有奸。紛亂東北。詔撫成飾。武臣承德。行樂交逆。簫群慝。肅為濟哉。蓋定燕國。XX大海蕩蕩水所歸。高賢愉愉民所懷。大山崔。百卉殖。民何貴。貴有德。XX安其所。樂終產。樂終產。世繼緒。飛龍秋。游上天。高賢愉。樂民人。XX豐草葽。女羅施。善何如。誰能回。大莫大。成教德。長莫長。被無極。XX雷震震。電耀耀。明德鄉。治本約。治本約。澤弘大。加被寵。咸相保。德施大。世曼壽。XX都荔遂芳。窅{宀瓜}桂華。孝奏天儀。若日月光。乘玄四龍。回馳北行。羽旄殷盛。芬哉芒芒。孝道隨世。我署文章。XX馮馮翼翼。承天之則。吾易久遠。燭明四極。XX慈惠所愛。美若休德。杳杳冥審。克綽永福。XX磑磑即即。師象山則。鳴呼孝哉。案撫戎國。蠻夷竭歡。象來致福。兼臨是愛。終無兵革。XX嘉薦芳矣。告靈饗矣。告靈既饗。德音孔臧。惟德之臧。建侯之常。承保天休。令問不忘。XX皇皇鴻明。盪侯休德。嘉承天和。伊樂厥福。在樂不荒。惟民之則。浚則師德。下民咸殖。XX令問在舊。孔容翼翼。XX孔容之常。承帝之明。下民之樂。子孫保光。承順溫良。受帝之光。嘉薦令芳。壽考不忘。XX承帝明德。師象山則。雲施稱民。永受厥福。承容之常。承帝之明。下民安樂。萬壽無疆。'
    half_test_str = '大孝備矣。休德昭清。高張四縣。樂充宮庭。芬樹羽林。雲景杳冥。金支秀華。庶旄翠旌。七始華始。肅倡和聲。神來晏娭。庶幾是聽。XX粥粥音送。細齊人情。忽乘青玄。熙事備成。清思眑眑。經緯冥冥。XX我定曆數。人告其心。敕身齊戒。施教申申。乃立祖廟。敬明尊親。大矣孝熙。四極爰轃。XX王侯秉德。其鄰翼翼。顯明昭式。清明鬯矣。皇帝孝德。竟全大功。撫安四極。XX海內有奸。紛亂東北。詔撫成飾。武臣承德。行樂交逆。簫群慝。肅為濟哉。蓋定燕國。XX大海蕩蕩水所歸。高賢愉愉民所懷。大山崔。百卉殖。民何貴。貴有德。XX安其所。樂終產。樂終產。世繼緒。飛龍秋。游上天。高賢愉。樂民人。XX豐草葽。女羅施。善何如。誰能回。大莫大。成教德。長莫長。被無極。'
    test_str = half_test_str # this one saves time if set to 'half_test_str'
    base_stanza_id = 'Lu1983.114'
    s_annotator = schuessler_stanza_annotator()
    test_lines = test_str.split('XX')  # get_rhyme_words_naively2
    print('='*100)
    print(' '*40 + ' INPUT DATA (' + base_stanza_id + ')')
    print('='*100)
    print('\n'.join(test_lines))
    print('='*100)
    linc = 0
    line_length = 0  # # not used anyway
    rmarker = rhyme_marker()
    nonrw_lines_dict = {}
    s_annotator.reset()
    lh_fayin_dict = {}
    every_line_rhymes = False
    rw_words = []
    rnet = new_rhyme_network()
    default_color = '#80B8F0'
    graph = nx.Graph()
    options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
    is_half = 'full'
    heading = 'Schuessler Full Poem Test'
    if test_str == half_test_str:
        heading = 'Schuessler Half Poem Test'
        is_half = 'half'
    pyvis_net = Network('1000px', '1000px', heading=heading, font_color='white')
    pyvis_net.set_options(options)
    #
    # Step 1: Collect Rhyme words
    for line in test_lines:
        linc += 1
        stanza_id = base_stanza_id + '.' + str(linc)
        rw_words += get_rhyme_words_from_stanza(line, stanza_id, every_line_rhymes)
        output_str = ''
    #
    # Step 2: Process Rhyme words
    #      2a: add rhyme words to the Schuessler annotator
    rw_list = []
    rw_data_inc = 0
    for rw_data in rw_words:
        rw_data_inc += 1
        if rw_data_inc == 130:
            x = 1
        rw = rw_data[0]
        rw_pos = rw_data[1]
        orig_line = rw_data[2]
        line_id = rw_data[3]
        s_annotator.add_rhyme_word(rw, rw_pos, orig_line, line_id)
        if rw.strip():
            rnet.add_node(rw, rw_pos, orig_line, line_id)
            graph.add_node(rw,weight=1)#rhyme_word, weight=weight
            rw_list.append(rw)
    lhan = ''
    #
    # add nodes
    rmarker.fill_marker2rhyme_dict(rw_list)
    s_annotator.fill_marker2rhyme_dict(rw_list)
    s_annotated_lines = s_annotator.get_annotated_lines() # needed
    marker2rw_list = s_annotator.get_marker2rw_list() # needed

    for line_inc in s_annotated_lines:
        al = s_annotated_lines[line_inc]
        rw = al[0]
        rw_pos = al[1]
        orig_line = al[2]
        line_id = al[3]
        annotated_line = al[4]
        print(annotated_line)
        #
        # Add Schuessler Edges
        for m in marker2rw_list:
            rw_list = marker2rw_list[m]
            edge_list = given_rhyme_group_return_list_of_edges(rw_list, base_stanza_id)
            for edge in edge_list:
                left_char = edge[0]
                right_char = edge[1]
                num_rhymes = edge[2]
                rhyme_id = edge[3]
                if not let_this_char_become_node(left_char):
                    continue
                if not let_this_char_become_node(right_char):
                    continue
                rnet.add_edge(left_char, right_char, num_rhymes, rhyme_id)
                graph.add_edge(left_char, right_char)#, weight=

                color = s_annotator.get_color_for_marker(m)
                lhan_rhyme = rmarker.get_rhyme_given_marker(m)
                if not color.strip():
                    color = default_color
                l_title = left_char
                r_title = right_char
                if lhan_rhyme:
                    l_title = left_char + '(' + lhan_rhyme + ')'
                    r_title = right_char + '(' + lhan_rhyme + ')'
                pyvis_net.add_node(left_char, title=l_title, label=l_title, color=color, shape='circle')
                pyvis_net.add_node(right_char, title=r_title, label=r_title, color=color, shape='circle')
                pyvis_net.add_edge(left_char, right_char, color=color)
    pyvis_net.show('pyvis_sch_' + is_half + '_poem_test.html')
                    #if not line % 2: # if this is a rhyme line
    for line in test_lines:
        print(line)
    print('='*30)
    rnet.print_out_nodes_n_edges()
    #
    # Vizualization
    alt.data_transformers.disable_max_rows()
    pos = nx.spring_layout(graph, k=0.3, iterations=20)
    # Add attributes to each node.
    for n in graph.nodes():
        graph.nodes[n]['name'] = n

    viz = nxa.draw_networkx(G=graph, pos=pos, node_color='group',
                            node_label='name')  # note: , with_labels=True is for networkx, not nx_altair
    viz = viz.properties(height=700, width=700)
    graph_name = 'schuessler_full_poem'
    viz.save('viz_' + graph_name + '.html')

class new_edge_array:
    def __init__(self):
        self.edge_dict = {}

    def add_edge(self, left_char, right_char, num_rhymes, rhyme_id):
        if left_char not in self.edge_dict:
            self.edge_dict[left_char] = {}
        if right_char not in self.edge_dict[left_char]:
            self.edge_dict[left_char][right_char] = []
        if (num_rhymes, rhyme_id) not in self.edge_dict[left_char][right_char]:
            self.edge_dict[left_char][right_char].append((num_rhymes, rhyme_id))

        if right_char not in self.edge_dict:
            self.edge_dict[right_char] = {}
        if left_char not in self.edge_dict[right_char]:
            self.edge_dict[right_char][left_char] = []
        if (num_rhymes, rhyme_id) not in self.edge_dict[right_char][left_char]:
            self.edge_dict[right_char][left_char].append((num_rhymes, rhyme_id))

    def get_edge_data(self, left_char, right_char):
        retval = []
        if left_char in self.edge_dict:
            if right_char in self.edge_dict[left_char]:
                retval = self.edge_dict[left_char][right_char]
        return retval

    def get_num_edge_occurrences(self, left_char, right_char):
        return len(self.get_edge_data(left_char, right_char))

    def get_num_edges(self):
        return len(self.edge_dict)/2.0

    def print(self):
        done_list = []
        for lc in self.edge_dict:
            for rc in self.edge_dict[lc]:
                if lc + rc not in done_list:
                    done_list.append(lc + rc)
                if rc + lc not in done_list:
                    print(lc + '<->' + rc)
                    for e in self.edge_dict[lc][rc]:
                        print('\t' + str(e))

class new_node: # (rw_word, rw_pos, orig_line, line_id, '')
    def __init__(self, rhyme_word, rw_pos, orig_line, line_id):
        self.rhyme_word = rhyme_word
        self.data = []
        self.data.append((rw_pos, orig_line, line_id))
    def add_occurrence(self, rw_pos, orig_line, line_id):
        if (rw_pos, orig_line, line_id) not in self.data:
            self.data.append((rw_pos, orig_line, line_id))
    def get_occurrence_list(self):
        return self.data
    def get_data(self):
        return self.data
    def print(self):
        for d in self.data:
            print(d)

class new_node_array:
    def __init__(self):
        self.array = {}

    def add_node(self, rhyme_word, rw_pos, orig_line, line_id):
        if rhyme_word not in self.array:
            node = new_node(rhyme_word, rw_pos, orig_line, line_id)
            self.array[rhyme_word] = node
        else:
            self.array[rhyme_word].add_occurrence(rw_pos, orig_line, line_id)

    def add_occurrence(self, rhyme_word, rw_pos, orig_line, line_id):
        self.add_node(rhyme_word, rw_pos, orig_line, line_id)

    def get_node_data(self, rhyme_word):
        retval = new_node('',-1, '','')
        if rhyme_word in self.array:
            retval = self.array[rhyme_word].get_data()
        return retval

    def print(self):
        for rw in self.array:
            node_data = self.array[rw].get_data()
            node_data2 = self.get_node_data(rw)
            for nd in node_data:
                print(rw + ':' + str(nd))

class new_rhyme_network:
    def __init__(self):
        self.node_array = new_node_array()
        self.edge_array = new_edge_array()
    def add_node(self, rhyme_word, rw_pos, orig_line, line_id):
        self.node_array.add_node(rhyme_word, rw_pos, orig_line, line_id)
    def get_node_data(self, rhyme_word):
        if rhyme_word in self.node_array:
            retval = self.node_array.get_node_data(rhyme_word)
    def get_num_nodes(self):
        return len(self.node_array)
    def get_num_edges(self):
        return len(self.edge_array.get_num_edges())
    def add_edge(self, left_char, right_char, num_rhymes, rhyme_id):
        self.edge_array.add_edge(left_char, right_char, num_rhymes, rhyme_id)
    def get_edge_data(self, left_char, right_char):
        return self.edge_array.get_edge_data(left_char, right_char)
    def print_out_nodes_n_edges(self):
        print('NODES:')
        self.node_array.print()
        print('')
        print('EDGES:')
        self.edge_array.print()

class schuessler_stanza_annotator:
    def __init__(self):
        self.rmarker = rhyme_marker()  # internal
        self.schuessler = schuessler_n_bentley()  # internal
        self.reset()
        self.lhan_rhyme2rw_list = {}
        self.rw2lhan_rhyme = {}

    def reset(self):
        self.rmarker.reset_memory()
        self.lh_fayin_dict = {}  # internal
        self.lh_fayin_path = {}
        self.rw2lhan_dict = {}  # internal
        self.rw2rw_data_dict = {}
        self.rw_missing_schuessler = []
        self.rw_inc = 1
        self.marker2rw_list = {}
        self.marker2color_dict = {}
        self.pyvis_net = Network('1000px', '1000px', heading='Schuessler Late Han', font_color='white')

    def reset_longterm_data(self):
        self.reset()
        self.lhan_rhyme2rw_list = {}
        self.rw2lhan_rhyme = {}

    def get_long_term_rhyme_to_rw_list_data(self):
        return self.lhan_rhyme2rw_list

    def get_long_term_rw_to_rhyme_data(self):
        return self.rw2lhan_rhyme

    def add_data_to_long_term_storage(self, lhan_rhyme, rhyme_word):
        if lhan_rhyme not in self.lhan_rhyme2rw_list:
            self.lhan_rhyme2rw_list[lhan_rhyme] = []
        if rhyme_word not in self.lhan_rhyme2rw_list[lhan_rhyme]:
            self.lhan_rhyme2rw_list[lhan_rhyme].append(rhyme_word)
        if rhyme_word not in self.rw2lhan_rhyme:
            self.rw2lhan_rhyme[rhyme_word] = []
        if lhan_rhyme not in self.rw2lhan_rhyme[rhyme_word]:
            self.rw2lhan_rhyme[rhyme_word].append(lhan_rhyme)
            if len(self.rw2lhan_rhyme[rhyme_word]) > 1:
                print(rhyme_word + ' used for more than one rhyme: ' + ', '.join(self.rw2lhan_rhyme[rhyme_word]))

    def fill_marker2rhyme_dict(self, rw_list):
        self.rmarker.fill_marker2rhyme_dict(rw_list)

    def get_marker2rhyme_dict(self):
        return self.rmarker.get_marker2rhyme_dict()

    # get marker given rhyme
    def get_marker(self, rhyme):
        return self.rmarker.get_marker(rhyme)

    def get_default_color(self):
        return '#80B8F0'
    def get_color_for_marker(self, m):
        funct_name = 'get_color_for_marker()'
        self.get_marker2color_dict()
        retval = self.get_default_color()
        if m in self.marker2color_dict:
            retval = self.marker2color_dict[m]
        return retval

    def get_marker2color_dict(self):
        if self.marker2color_dict:
            return self.marker2color_dict

        self.get_marker2rw_list()
        rw_list_len2marker_dict = {}
        for m in self.marker2rw_list:
            x = 1
            mlen = len(self.marker2rw_list[m])
            if mlen not in rw_list_len2marker_dict:
                rw_list_len2marker_dict[mlen] = []
            rw_list_len2marker_dict[mlen].append(m)
        rw_list_lens = list(rw_list_len2marker_dict.keys())
        rw_list_lens.sort(reverse=True)

        color_list = ['#03045E', '#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8']
        color_list = ['#D7D9D7', '#C9C5CB', '#BAACBD', '#B48EAE', '#646E68']
        #marker2color_dict = {}
        c_inc = 0
        for list_len in rw_list_lens:
            m_list = rw_list_len2marker_dict[list_len]
            for m in m_list:
                if m not in self.marker2color_dict:
                    if c_inc <= len(color_list) - 1:
                        self.marker2color_dict[m] = color_list[c_inc]
                        c_inc += 1
        return self.marker2color_dict

    def get_marker2rw_list(self):
        if self.marker2rw_list:
            return self.marker2rw_list
        m2r_dict = self.rmarker.get_marker2rhyme_dict()
        rw_list = self.get_rhyme_word_list()
        self.get_rw2lhan_dict()
        for m in m2r_dict:
            if m not in self.marker2rw_list:
                self.marker2rw_list[m] = []
            r = m2r_dict[m]
            for rw in rw_list:
                lhan = self.rw2lhan_dict[rw]
                rhyme = get_rhyme_from_schuessler_late_han_syllable(lhan)
                if rhyme == r:
                    self.marker2rw_list[m].append(rw)
        return self.marker2rw_list

    # PURPOSE:
    #   to add a rhyme word to self.rw2rw_data_dict
    def add_rhyme_word(self, rw_word, rw_pos, orig_line, line_id):
        if any(punct in rw_word for punct in punctuation):
            if rw_word == '}':  # '上辟彔{礻＋羽}'
                return #NOTE: we can't use {礻＋羽}, because there wont' be any Han data for {礻＋羽}
        if rw_word == '々':
            rw_pos -= 1
            rw_word = orig_line[rw_pos]
        if self.rw_inc not in self.rw2rw_data_dict:
            self.rw2rw_data_dict[self.rw_inc] = ''
        try:
            self.rw2rw_data_dict[self.rw_inc] = (rw_word, rw_pos, orig_line, line_id, '')
            self.rw_inc += 1
        except KeyError as ke:
            x = 1
        if not rw_word.strip():
            return
        lhan = self.schuessler.get_late_han(rw_word)
        if not lhan:
            if rw_word not in self.rw_missing_schuessler:
                self.rw_missing_schuessler.append(rw_word)
        if lhan and rw_word not in self.lh_fayin_dict:
            self.lh_fayin_dict[rw_word] = [] # was: ''
        self.lh_fayin_dict[rw_word] = lhan# was: ' '.join(lhan); 'lhan' is a list

    def get_rhyme_word_list(self):
        return self.lh_fayin_dict.keys()

    def get_late_han_fayin(self, rhyme_word):
        self.get_rw2lhan_dict()
        retval = ''
        if rhyme_word in self.rw2lhan_dict:
            retval = self.rw2lhan_dict[rhyme_word]
        return retval

    #IMPORTANT: call after self.get_annotated_lines()
    # PURPOSE:
    #   calculate the rhyme xs word to Late Han dictionary (self.rw2lhan_dict):
    # Depends on:
    #   - self.lh_fayin_path
    #   - self.lh_fayin_dict
    def get_rw2lhan_dict(self):
        keys2remove = []
        if not self.rw2lhan_dict:
            self.get_late_han_fayin_path()
            kinc = 0
            # create rw2lhan_dict (rhyme_word to late_han dictionary)
            for ck in self.lh_fayin_dict:
                if any(punct in ck for punct in punctuation): # was if ck == '}':
                    if ck not in keys2remove:
                        keys2remove.append(ck)
                if not self.lh_fayin_dict[ck]:
                    self.lh_fayin_dict[ck] = ['not_available']
            for key in keys2remove:
                del self.lh_fayin_dict[key]

            # NOTE:
            #  if self.rw2lhan_dict has N members, then self.lh_fayin_path[kinc] should have a pronunciation path with
            #    N pronunciations
            #  kinc should only go up to len(self.lh_fayin_path) - 1, EXCEPT that it will go to len(...) on its way
            #                                                                out of the loop, but it shouldn't be
            #                                                                referenced that last time
            for ck in self.lh_fayin_dict:
                if ck not in self.rw2lhan_dict:
                    self.rw2lhan_dict[ck] = ''
                try:
                    self.rw2lhan_dict[ck] = self.lh_fayin_path[kinc]
                except IndexError as ie:
                    x = 1
                try:
                    fayin_path = self.lh_fayin_path[kinc]
                except IndexError as ie:
                    x = 1
                rhyme = get_rhyme_from_schuessler_late_han_syllable(fayin_path)
                self.add_data_to_long_term_storage(rhyme, ck)
                kinc += 1
        return
    # PURPOSE:
    #   to calculate the optimal Late Han pronunciation path, i.e., to find one that optimizes rhyming
    # Prereqs:
    #   self.lh_fayin_dict must be filled in before calling this function
    def get_late_han_fayin_path(self):
        if not self.lh_fayin_dict:
            return {}
        root_node = create_tree(self.lh_fayin_dict)
        pad_list = given_root_node_get_list_of_possible_paths(root_node)
        self.lh_fayin_path = find_path_optimized_for_rhyme(pad_list)
        return self.lh_fayin_path

    #NOTE: self.add_rhyme_word() automagically builds self.lh_fayin_dict
    def get_late_han_fayin_dict(self):
        return self.lh_fayin_dict

    def get_late_han_used_in_current_stanza(self, rhyme_word):
        retval = ''
        if rhyme_word in self.rw2lhan_dict:
            retval = self.rw2lhan_dict[rhyme_word]
        return retval

    def get_annotated_lines(self):
        if self.rw2rw_data_dict:
            return self.rw2rw_data_dict
        # calculate which late han readings to use (i.e., the ones that optimize rhyming)
        root_node = create_tree(self.lh_fayin_dict)
        pad_list = given_root_node_get_list_of_possible_paths(root_node)
        lh_fayin_path = find_path_optimized_for_rhyme(pad_list)
        rw_pos = 0
        rw_pos_pos = 1
        orig_line_pos = 2
        line_id_pos = 3
        annotated_line_pos = 4
        kinc = 0
        missing_lhan = []
        # create rw2lhan_dict (rhyme_word to late_han dictionary for a given stanza)
        for ck in self.lh_fayin_dict:
            if ck not in self.rw2lhan_dict:
                self.rw2lhan_dict[ck] = ''
            self.rw2lhan_dict[ck] = lh_fayin_path[kinc]
            kinc += 1
        #
        # cycle back through the rhyme words updating self.rw2rw_data_dict entries
        # self.rw2rw_data_dict[self.rw_inc].append((rw_word, rw_pos, orig_line, line_id, ''))
        # NOTE: the same rhyme word may have multiple occurrences
        for rw_inc in self.rw2rw_data_dict:
            msg_out = ''
            #rw = self.rw2rw_data_dict[rw_inc][rw_pos]
            #if len(self.rw2rw_data_dict[rw_inc]) > 1:
            #    x = 1
            rw_data = self.rw2rw_data_dict[rw_inc]
            rw = rw_data[0]
            # if there is no rhyme word, then just use the original line as the output line
            if not rw.strip():
                orig_line = rw_data[orig_line_pos]
                self.rw2rw_data_dict[rw_inc] = (rw, rw_data[1], orig_line, rw_data[3], orig_line + '。')
                continue
            lhan = self.rw2lhan_dict[rw]
            orig_line = rw_data[orig_line_pos]
            rw_pos = rw_data[rw_pos_pos]
            if lhan:
                rhyme = get_rhyme_from_schuessler_late_han_syllable(lhan)
                marker = self.rmarker.get_marker(rhyme)
                # (rw_pos, orig_line, line_id, '')
                new_line = insert_rhyme_marker_at_pos(orig_line, rw_pos, marker + '(' + rhyme + ')')
                msg_out = new_line + '。'
                self.rw2rw_data_dict[rw_inc] = (rw, rw_pos, orig_line, rw_data[3], msg_out)
            else:  # if there is no LHan data, just write out original line
                missing_lhan.append(rw)
                self.rw2rw_data_dict[rw_inc] = (rw, rw_pos, orig_line, rw_data[3], orig_line + '。')
        if missing_lhan:
            print('Missing Late Han data: ' + ''.join(missing_lhan))
        return self.rw2rw_data_dict

def test_readin_network_in_pajek_format_and_return_pyvis_network():
    funct_name = 'test_readin_network_in_pajek_format_and_return_pyvis_network()'
    input_file = os.path.join(filename_storage.get_hanproj_dir(), 'received-shi', 'nodes_n_edges_annotated_received_shi_pre_com_det.txt')

    heading = 'Pre-Community Detection Received Shi'
    min_node_weight = 1 # don't print nodes with a node weight of less than this
    only_print_these_nodes = []
    readin_network_in_pajek_format_and_return_pyvis_network(input_file, heading, min_node_weight, only_print_these_nodes)

def readin_network_in_pajek_format_and_return_pyvis_network(input_file,
                                                           network_heading,
                                                           min_node_weight,
                                                           color_these_nodes,
                                                           is_verbose=False):
    funct_name = 'readin_network_in_pajek_format_and_return_pyvis_network()'
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: invalid input file: ' + input_file)
        print('\tAborting.')
        return
    line_list = readlines_of_utf8_file(input_file)
    line_list = line_list[1:len(line_list)]  # skip first line
    num_nodes = int(line_list[0].replace('*Vertices in ', ''))
    line_list = line_list[1:len(line_list)]  # skip second line
    node_id2rw_n_weight = {}
    chars2edge_weight = {}
    readin_edges = False
    pyvis_network = generate_pyvis_network(heading=network_heading)
    nodes_not_to_add = []
    for ll in line_list:
        if '*Edges ' in ll:
            num_edges = ll.replace('*Edges ', '')
            num_edges = int(num_edges.replace('.0',''))
            readin_edges = True
            continue
        ll = ll.split(' ')
        #
        # Process NODES
        if not readin_edges:
            node_num = ll[0]
            rhyme_word = ll[1].replace('"', '')
            node_weight = ll[2]
            if node_num not in node_id2rw_n_weight:
                node_id2rw_n_weight[node_num] = (rhyme_word, node_weight)
            if is_verbose:
                print('NODE: ' + node_num + ', ' + rhyme_word + ', ' + node_weight)
        else:
            #
            # Process EDGES
            left_char = ll[0]
            right_char = ll[1]
            edge_weight = ll[2]
            if left_char not in chars2edge_weight:
                chars2edge_weight[left_char] = {}
            if right_char not in chars2edge_weight[left_char]:
                chars2edge_weight[left_char][right_char] = ''
            chars2edge_weight[left_char][right_char] = edge_weight
            if is_verbose:
                print('EDGE: ' + left_char + ', ' + right_char + ', ' + edge_weight)
    #
    # Add NODES to network
    rw_pos = 0
    weight_pos = 1
    for node_id in node_id2rw_n_weight:
        rhyme_char = node_id2rw_n_weight[node_id][rw_pos]
        n_weight = node_id2rw_n_weight[node_id][weight_pos]
        if min_node_weight > 0: # a -1 means "don't use min node weight"
            if int(n_weight) < min_node_weight:
                nodes_not_to_add.append(rhyme_char)
                continue
        print('pyvis_net.add_node(' + rhyme_char + ', label=' + rhyme_char + ', weight = ' +  n_weight)
        if rhyme_char in color_these_nodes:
            color = '#550C18'
        else:
            color = '#80B8F0' # default color
        pyvis_network.add_node(rhyme_char, label=rhyme_char, weight=n_weight, color=color, shape='circle', value=n_weight)
    #
    # Add EDGES to network
    for left_char_id in chars2edge_weight:
        left_char = node_id2rw_n_weight[left_char_id][rw_pos]
        for right_char_id in chars2edge_weight[left_char_id]:
            right_char = node_id2rw_n_weight[right_char_id][rw_pos]
            e_weight = chars2edge_weight[left_char_id][right_char_id]
            if left_char in nodes_not_to_add or right_char in nodes_not_to_add:
                continue
            print('pyvis_net.add_edge(' + left_char + ', ' + right_char + ', weight=' + e_weight)
            pyvis_network.add_edge(left_char, right_char, weight=e_weight)

    network_heading = 'pyvis_' + network_heading.replace(' ', '_') + '.html'
    pyvis_network.show(network_heading)
    print('Num nodes = ' + str(num_nodes) + ', num edges = ' + str(num_edges))

def generate_pyvis_network(heading):
    pyvis_net = Network('1000px', '1000px', heading=heading, font_color='white')
    options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
    pyvis_net.set_options(options)
    return pyvis_net

def test_data_storage_and_redisplay():
    funct_name = 'test_data_storage_and_redisplay()'
    is_verbose = True
    print_debug_msgs = True
    message2user('Starting multi_dataset_processor()...', is_verbose)
    processor = multi_dataset_processor(is_verbose)
    processor.do_not_reprocess_old_data()
    message2user('Done.', is_verbose)
    network_type = 'network' # or 'graph'
    annotator_type = 'naive'
    data_type = 'received_shi'
    processor.create_network_from_file_data(network_type, annotator_type, data_type)

def which_chars_are_missing_lhan_data(chars):
    glyph2late_han = readin_most_complete_schuessler_data()
    retval = []
    for c in chars:
        try:
            lhan = glyph2late_han[c]
        except:
            if c not in retval:
                retval.append(c)
    return retval

def test_list_of_chars_for_lhan_data():
    char_list = '鳳蕭子了爵亞軌蹤繼頌心性術度爾滓厄記遠載騰布職計部上年節操廉中長靡下治擾稷首就舉'
    char_list = list(set(char_list))
    missing = which_chars_are_missing_lhan_data(char_list)
    print('')
    if missing:
        print('These chars are missing LHan data:')
        print('\t' + ''.join(missing))
    else:
        print('No chars in list missing LHan data.')

sinput = ['聲', '生']
#test_get_schuessler_late_han_for_glyph(sinput)
#test_get_schuessler_late_han_for_glyph(['清','名', '生', '盈', '成', '聽'])#['光','明'])#['里','海','何'])#['門','山'])

#
# Purpose:
#   This function does pre-community detection (pre-com det) and post-community detection (post-com det) processing
#   on all data sets:
# Input:
#     received_shi (the Lu1983 data; 逯欽立《先秦漢魏晉南北朝詩》1983)
#     mirrors (the kyomeishusei2015 data; 林裕己《漢三國西晉鏡銘集成》2015)
#     stelae (the mao2008 data; 毛遠明《漢魏六朝碑刻校注》2008)
# Output:
#   I. Various networks are output to the system's default web browser
#     For each data set:
#       pre-com det network (monochrome)
#       pre-com det network (colored using post-com det groups as basis for different colors)
#       post-com det network
#   II. Annotated poems
#     For each data set (output to each data type's directory):
#       Naively annotated poems
#       Schuessler annotated poems
#       Community annotated poems (i.e., annotated using the results of community detection)
#   III. Combined Data (combo data)
#     In addition to the singular data types, there is also a combined data type which is output, basically,
#     all of the input data is put into a single network.
#
# This function is set up to run all data types. However, there are a set of flags which can be set to individually
# select which data to run:
#   run_lu1983_data = True
#   run_mirror_data = True
#   run_stelae_data = True
#   run_combined_data = True
#
#   Setting any of these to False will turn off their respective processing.

def process_all_data_sets():
    funct_name = 'process_all_data_sets()'
    is_verbose = True
    print_debug_msgs = True
    message2user('Starting multi_dataset_processor()...', is_verbose)
    message2user(get_timestamp(), is_verbose)
    processor = multi_dataset_processor(is_verbose)#, delete_old_data)
    message2user('Done.', is_verbose)
    run_lu1983_data = True
    run_mirror_data = True
    run_stelae_data = True
    run_combined_data = True

    #
    # Pre-Com Det processing
    if run_lu1983_data: # PRE-Com Det
        message2user('Running Pre-Com Det processing for Received Shi Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.overwrite_old_data()
        message2user('\tProcessing Received Shi Data', is_verbose)
        processor.pre_com_det_processing('received_shi', is_verbose, print_debug_msgs)
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tOutputting data to file...', is_verbose)
        processor.output_received_shi_network_to_file()
        rnet_filename = filename_storage.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
        received_net = processor.get_network_object('network', 'naive', 'received_shi')
        received_net.output_rnetwork_to_file(rnet_filename)
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tRunning Community Detection...', is_verbose)
        processor.run_community_detection_for_lu1983()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tCreating pyvis network graph with group coloring...', is_verbose)
        processor.create_pyvis_network_graph_for_received_shi_com_detected_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        #processor.create_pyvis_network_graph_for_pre_com_det_received_shi()
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

    if run_mirror_data: # PRE-Com Det
        message2user('Running Pre-Com Det processing for Mirror Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.overwrite_old_data()
        message2user('\tProcessing Mirror data...', is_verbose)
        processor.pre_com_det_processing('mirrors', is_verbose, print_debug_msgs)
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tOutputting data to file...', is_verbose)
        processor.output_mirror_network_to_file()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tRunning Community Detection...', is_verbose)
        processor.run_community_detection_for_mirrors()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tCreating pyvis network graph with group coloring...', is_verbose)
        processor.create_pyvis_network_graph_for_mirrors_com_detected_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

    if run_stelae_data: # PRE-Com Det
        message2user('Running Pre-Com Det processing for Stelae Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.overwrite_old_data()
        message2user('\tProcessing Stelae data...', is_verbose)
        processor.pre_com_det_processing('stelae', is_verbose, print_debug_msgs)
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tOutputting data to file...', is_verbose)
        processor.output_stelae_network_to_file()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tRunning Community Detection...', is_verbose)
        processor.run_community_detection_for_stelae()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tCreating pyvis network graph with group coloring...', is_verbose)
        processor.create_pyvis_network_graph_for_stelae_com_detected_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

    if run_combined_data: # PRE-Com Det
        message2user('Running Pre-Com Det processing for Combined Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.do_not_reprocess_old_data()
        message2user('\tOutputting data to file...', is_verbose)
        processor.output_combined_data_network_to_file()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tRunning Community Detection...', is_verbose)
        processor.run_community_detection_for_combined_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tCreating pyvis network graph with group coloring...', is_verbose)
        processor.create_pyvis_network_graph_for_combined_com_detected_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tCreating pyvis network graph for combined Schuessler...', is_verbose)
        processor.create_pyvis_network_graph_for_schuessler_combo_data()
        message2user('\tCreating pyvis network graph for pre-com det combined data...', is_verbose)
        processor.create_pyvis_network_graph_for_pre_com_det_combined_data()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)
    #
    # POST Com Det processing
    if run_lu1983_data: # POST-Com Det
        message2user('Running Post-Com Det processing for Received Shi Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.do_not_reprocess_old_data()
        message2user('\tCreating network with detected communities for received shi...',
                     is_verbose)
        processor.create_network_for_received_shi_with_com_det_annotator()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)
    if run_mirror_data: # POST-Com Det
        message2user('Running Post-Com Det processing for Mirror Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.do_not_reprocess_old_data()
        message2user('\tCreating network with detected communities for mirrors...',
                     is_verbose)
        processor.create_network_for_mirrors_with_com_det_annotator()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)
    if run_stelae_data: # POST-Com Det
        message2user('Running Post-Com Det processing for Stelae Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.do_not_reprocess_old_data()
        message2user('\tCreating network with detected communities for stelae...',
                     is_verbose)
        processor.create_network_for_stelae_with_com_det_annotator()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)
    if run_combined_data: # POST-Com Det
        message2user('Running Pre-Com Det processing for Combined Data...', is_verbose)
        message2user(get_timestamp(), is_verbose)
        processor.do_not_reprocess_old_data()
        if run_lu1983_data:
            message2user('Creating Post-Com Det network for Received Shi...', is_verbose)
            filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'received_shi')
            processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
            message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)

        if run_mirror_data:
            message2user('Creating Post-Com Det network for Mirrors...', is_verbose)
            filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'mirrors')
            processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
            message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)

        if run_stelae_data:
            message2user('Creating Post-Com Det network for Stelae...', is_verbose)
            filename = processor.get_filename_for_annotated_network_data('network', 'naive', 'stelae')
            processor.readin_rnetwork_data_from_file(filename, 'rhyme_net')
            message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)

        message2user('Creating Post-Com Det network for Combo data...', is_verbose)
        processor.create_network_for_combo_data_with_com_det_annotator()
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

    # compute annotator comparison statistics
    message2user('Computing annotator comparision statistics:', is_verbose)
    message2user('\tFor received shi...', is_verbose)
    compare_annotation_between_different_annotators('received_shi')
    message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
    message2user('\tFor mirrors...', is_verbose)
    compare_annotation_between_different_annotators('mirrors')
    message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
    message2user('\tFor stelae...', is_verbose)
    compare_annotation_between_different_annotators('stelae')
    message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
    message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

def get_timestamp():
    return datetime.datetime.now().strftime("%A, %d %B %Y @ %I:%M%p")

def test_convert_punctuation():
    funct_name = 'test_convert_punctuation()'
    # xxx，xxx，xxx，xxx，xxx，xxx，xxx，xxx。
    # xxx，xxx。xxx，xxx。xxx，xxx。xxx，xxx。

# convert this type of punctuation: xxx，xxx，xxx，xxx，xxx，xxx，xxx，xxx。
#    to this type: xxx，xxx。xxx，xxx。xxx，xxx。xxx，xxx。

#
# Purpose:
# This converts all ， and 、 into 。
# 'data_type' is for in case we want to change punctuation differently for different data types.
def convert_punctuation(line, data_type):
    funct_name = 'convert_punctuation()'
    cnt_straight = line.count('、')
    if data_type == 'mirrors':
        if line.count('、') > 1:
            line = line.replace('、', '。')
    elif data_type == 'stelae':
        if '。' in line:
            line_split = line.split('。')
            retval = []
            for ls in line_split:
                if ls.strip():
                    retval.append(ls)
            line = '。'.join(retval)
        if '，' in line:
            line = line.replace('，', '。')
    return line

def characterize_stelae_punctuation():
    funct_name = 'characterize_stelae_punctuation()'
    filename_storage = filename_depot()
    data_type = 'stelae'
    annotator_type = 'naive'
    filename = filename_storage.get_output_filename_for_poem_marking_annotation(data_type, annotator_type)
    line_list = readlines_of_utf8_file(filename)
    max_com = -1
    for ll in line_list:
        #print(ll)
        num_curly_commas = ll.count('，')
        if num_curly_commas > max_com:
            max_com = num_curly_commas
        num_straight_commas = ll.count('、')
        if num_straight_commas > max_com:
            max_com = num_straight_commas
        num_full_stops = ll.count('。')
        if num_curly_commas > 2:
            print(ll)
        elif num_straight_commas > 2:
            print(ll)


def characterize_mirror_punctuation():
    funct_name = 'characterize_mirror_punctuation()'
    #readin_kyomeishusei2015_han_mirror_data()
    filename_storage = filename_depot()
    data_type = 'mirrors'
    annotator_type = 'naive'
    filename = filename_storage.get_output_filename_for_poem_marking_annotation(data_type, annotator_type)
    line_list = readlines_of_utf8_file(filename)
    output_file = 'for-nathan.txt'
    inc = 0
    current_poem = []
    prev_poem_num = '-1'
    max_com = -1
    for ll in line_list:
        xx = ll.split('： ')[0]
        xx = xx.split('.')
        poem_num = xx[1]
        # if entering a new poem
        if poem_num != prev_poem_num:
            if current_poem and max_com > 0 and len(current_poem) > 2:
                #print(poem_num + ':')
                print('\n\t'.join(current_poem))
                append_line_to_utf8_file(output_file, '\n\t'.join(current_poem))
            max_com = -1
            current_poem = []
            prev_poem_num = poem_num
        current_poem.append(ll)
        inc += 1
        if inc == 4000:
            x = 1
        elif inc == 8000:
            x = 1
        num_curly_commas = ll.count('，')
        if num_curly_commas > max_com:
            max_com = num_curly_commas
        num_straight_commas = ll.count('、')
        if num_straight_commas > max_com:
            max_com = num_straight_commas
        num_full_stops = ll.count('。')
        msg = 'num_curl=' + str(num_curly_commas) + ', num_straight=' + str(num_straight_commas) + ', num_dots=' + str(num_full_stops)
        #print(msg + ': ' + ll)

#characterize_mirror_punctuation()
#characterize_stelae_punctuation()
def test_annatator_comparison():
    # compute annotator comparison statistics
    is_verbose = True
    message2user('Computing annotator comparision statistics:', is_verbose)
    message2user('\tFor received shi...', is_verbose)
    compare_annotation_between_different_annotators('received_shi')
    message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)

    if 0:
        message2user('\tFor mirrors...', is_verbose)
        compare_annotation_between_different_annotators('mirrors')
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('\tFor stelae...', is_verbose)
        compare_annotation_between_different_annotators('stelae')
        message2user('\tDone (' + str(get_timestamp()) + ').', is_verbose)
        message2user('Done (' + str(get_timestamp()) + ').', is_verbose)

def fix_issues_with_stelae_data():
    funct_name = 'fix_issues_with_stelae_data()'
    data_type = 'stelae'
    stanza_proc = stanza_processor(data_type)
    s_data = parse_mao_2008_stelae_data(is_verbose=True)
    uniqid2poem_dict = s_data.get_uniq2data_dict()
    every_line_rhymes = False
    temp_file = 'debug_temp_naive.txt'
    naive_output = 'debug_naive_output.txt'
    delete_file_if_it_exists(temp_file)
    delete_file_if_it_exists(naive_output)
    for k in uniqid2poem_dict:  # lu1983_poem -- for each unique poem ID...
        poem_num = int(k.split('.')[1])  # debug only
        poem = uniqid2poem_dict[k].get_poem_content_as_str()
        stanza_list = poem.split('。') # was
        st_inc = 0
        poem_id = uniqid2poem_dict[k].get_poem_id()
        stanza_id = poem_id + '.' + str(st_inc)
        # Process a single stanza
        for stanza in stanza_list:
            if not stanza.strip():
                continue
            stanza = convert_punctuation(stanza, data_type)
            stanza_proc.input_stanza(stanza, stanza_id, every_line_rhymes)
            if stanza.count(' ') > 0:  # this is a sign that the original poem wasn't punctuated (and therefore
                #   should be skipped)
                annotated_stan = []
                rijm_lijst = []
            else:
                annotated_stan, rijm_lijst = stanza_proc.naively_annotate(temp_file)
            #
            if not annotated_stan:  # if there are no rhymes in the stanza...
                append_line_to_output_file(naive_output, stanza_id + '： ' + stanza)
                continue

#test_annatator_comparison()
process_all_data_sets()
#test_multi_dataset_processor() #-----
#test_list_of_chars_for_lhan_data()

