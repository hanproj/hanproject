#! C:\Python36\
# -*- encoding: utf-8 -*-
#
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

import os
import codecs
from copy import deepcopy
encode = codecs.utf_8_encode
import sinopy
import scipy
import numpy
import cydifflib
#from num_conversion import kansuji2arabic
from soas_rnetwork_test import rnetwork
from soas_rnetwork_test import get_timestamp_for_filename
#import PyQt5
from PIL import Image
#from PIL.Image import core as _imaging
import pandas as pd
import networkx as nx
import altair as alt
import altair_viewer as alt_view
#nx_altair is one of many visualization libraries for networkx.
import nx_altair as nxa
import matplotlib.pyplot as plt
from infomap import Infomap
from py3_middle_chinese import get_mc_data_for_char
from test_is_hanzi import is_kana_letter
# from: https://www.programcreek.com/python/example/89583/networkx.draw_networkx_labels
plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

utf8_bom_b = b'\xef\xbb\xbf'

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

def get_hanproj_dir():
    return os.path.join(get_soas_code_dir(), 'hanproj')

def get_mirrors_dir():
    return os.path.join(get_hanproj_dir(), 'mirrors')

def get_stelae_dir():
    return os.path.join(get_hanproj_dir(), 'stelae')

def get_received_shi_dir():
    return os.path.join(get_hanproj_dir(), 'received-shi')

def get_received_bronzes_dir():
    return os.path.join(get_hanproj_dir(),'bronzes')

def get_schuesslerhanchinese_dir():
    return os.path.join(get_soas_code_dir(),'schuesslerhanchinese')

def readlines_of_utf8_file(filename):
    funct_name = 'readlines_of_utf8_file()'
    retval = []
    if not os.path.isfile(filename):
        print(funct_name + u' ERROR: filename INVALID: ' + filename)
        return retval
    with open(filename, 'rb') as f:
        line_list = f.readlines()
    line_list[0] = line_list[0].replace(utf8_bom_b, b'')
    for line in line_list:
        line = line.decode('utf8')
        line = line.replace('\r\n', '')
        line = line.replace('\n', '')
        retval.append(line)
    return retval

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

def append_line_to_output_file(filename, line, is_verbose=False):
    funct_name = 'append_line_to_output_file()'
    new_line = '\n'
    if line[len(line)-len(new_line): len(line)] == new_line:
        line = line[0:len(line)-len(new_line)]
    if os.path.exists(filename):
        append_write = 'a+'  # append if already exists
    else:
        append_write = 'w+'  # make a new file if not
    if is_verbose:
        print(u'trying to write to ' + filename)
    with codecs.open(filename, append_write, 'utf8') as f:
        f.write(line + new_line)

def readin_raw_han_poetry(is_verbose=False):
    funct_name = 'readin_raw_han_poetry()'
    input_file = os.path.join(get_received_shi_dir(), 'raw', '3 Han Poetry.csv')
    line_list = readlines_of_utf8_file(input_file)
    label_list = line_list[0].replace('\n','')
    label_list = label_list.split(',')
    line_list = line_list[1:len(line_list)]
    poem_name_list = []
    inc = 0
    for l in line_list:
        l = l.split(',')
        #print('line[' + label_list[0] + '] = ' + l[0])
        pname = l[0].replace('"','')
        poem_name_list.append(simp2trad(pname))
        if pname != simp2trad(pname) and is_verbose:
            inc += 1
            print('(' + str(inc) + ') ' + pname)
            print('(' + str(inc) + ') ' + simp2trad(pname))
            #print('SIMP/TRAD = ' + pname + ' / ' + simp2trad(pname))
        #print('line[' + label_list[1] + '] = ' + l[1])
        #print('line[' + label_list[2] + '] = ' + l[2])
        #print('line[' + label_list[3] + '] = ' + l[3])
        #print('-*'*100)
        #print(l)
    if is_verbose:
        print(str(len(poem_name_list)) + ' poems in')
        print('\t' + input_file)
        print(', '.join(poem_name_list))
    return poem_name_list

def get_list_poem_names_from_3_han_poetry():
    funct_name = 'get_list_poem_names_from_3_han_poetry()'
    input_file = os.path.join(get_received_shi_dir(), 'raw', '3 Han Poetry.csv')
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
        #self.labels = []
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
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'han-authors-in-lu.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    retval = readlines_of_utf8_file(input_file)
    return retval


def test_rolling_n_lines():
    funct_name = 'test_rolling_n_lines()'
    print(funct_name + ' welcomes you!')
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
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
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
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
    #poets_found = 0
    #found_list = []
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
        #for l in poet2data_dict[poet]:
        #    print('\t' + l)

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
            #print('pline=\n' + pline)
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
            if '劉騊駼' == poet:
                x = 1
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
#juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
    print(str(len(poet2data_dict.keys())) + ' poets found.')






juan_num2data_dict = {}
def parse_han_data_from_lu_1983_form_poems_with_poet_names(is_verbose=False):
    funct_name = 'parse_han_data_from_lu_1983_form_poems_with_poet_names()'
    print('Welcome to ' + funct_name + '!')
    global juan_num2data_dict
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
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
        if '漢高帝劉邦' in l:
            x = 1
        if entered_han_sec:
            if rlines.is_condition_true(outer_prev_line, print_rolling):
                x = 1
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
                #poet_name = ''
                #poet_intro = '' # poet & poet intro can last across several poems
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
                #poet_intro = ''
                poem_large_commentary = ''
                #poet_name = '' # poet name & poet intro can last across several poems
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
            #if rollines.is_condition_true(l, print_rolling):
            #    x = 1
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
                        #poet_intro = ''
                        poem_large_commentary = ''
                        #poet_name = ''
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
#    global poem_num2data_dict
    global juan_num2data_dict
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    #juan = '卷'
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
                #poem_name = ''
                #poem_content = []
                juan_num = get_arabic_juan_num_from_juan_tag(current_juan)
                #file_seq_num = str(juan_num) + '.' + str(seq_num)
                if juan_num not in juan_num2data_dict:
                    juan_num2data_dict[juan_num] = {}
                if seq_num not in juan_num2data_dict[juan_num]:
                    juan_num2data_dict[juan_num][seq_num] = ''
                juan_num2data_dict[juan_num][seq_num] = LU_poem.get_storage_file_msg()
                #LU_poem.print()
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
                        #file_seq_num = str(juan_num) + '.' + str(seq_num)
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
                        #file_seq_num = str(juan_num) + '.' + str(seq_num)
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
    #print(str(author_cnt) + ' authors.') # debug only
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
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'Lu 1983 先秦漢魏晉南北朝詩.txt')
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
    #poem_name_is_current_line = False

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
    #Lu 1983 先秦漢魏晉南北朝詩.txt
    input_file = os.path.join(get_received_shi_dir(), 'raw', 'han-authors-in-lu.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid filename:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    #def remove_part_of_line(line, start_tag)
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

simp2trad_var_dict = {}
if 0:
    def load_trad_variants_of_simp():
        funct_name = 'load_trad_variants_of_simp()'
        if simp2trad_var_dict:
            return
        if '𬬰' not in simp2trad_var_dict: #鎗
            simp2trad_var_dict['𬬰'] = u'鎗'
        base_dir = os.path.join('C:' + os.sep + u'Ash', 'research', 'code', 'python', 'data')
        filename = os.path.join(base_dir, 'kTraditionalVariant.txt')
        line_list = readlines_of_utf8_file(filename)
        #input_ptr = codecs.open(base_dir + os.sep + filename, 'r', 'utf8')
        delim = u' '
        processed_vars = []
        for line in line_list:
            line = line.strip()
            if line and line[0] == '#':
                continue
            pos = line.find('\t')
            if pos > -1:
                entry_ncr = line[0:pos]
                entry_glyph = convert_ncr_to_glyph(entry_ncr)
                variant_ncrs = line[pos+1:len(line)]
                variant_ncrs = variant_ncrs.replace('U+', u'')
                variant_ncrs = variant_ncrs.split(' ')
                processed_vars[:] = []
    #            print u'entry=' + entry_glyph
                for v in variant_ncrs:
                    var_glyph = convert_ncr_to_glyph(v)
    #                print u'var_glyph = ' + var_glyph
                    processed_vars.append(var_glyph)
                if entry_glyph not in simp2trad_var_dict.keys():
                    simp2trad_var_dict[entry_glyph] = []
                    for v in processed_vars:
                        simp2trad_var_dict[entry_glyph].append(v)
                else:
                    simp2trad_var_dict[entry_glyph].append(processed_vars)



#
# Installed the Chinese-converter library (https://pypi.org/project/chinese-converter/)
# Installation was done via the command line in the virtual env: /cygdrive/c/users/ash/vm4pdf/
#
# when trying to run 'test_chinese_converter()'
# it threw the following error:
#Traceback (most recent call last):
#  File "C:/Ash/research/code/python/py3_projects/soas_utils.py", line 4, in <module>
#    import chinese_converter
#  File "C:\Users\ash\vm4pdf\lib\site-packages\chinese_converter\__init__.py", line 12, in <module>
#    traditional, simplified = f.read().strip(), g.read().strip()
#  File "C:\Users\ash\vm4pdf\lib\encodings\cp1252.py", line 23, in decode
#    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
#UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 20: character maps to <undefined>
def test_chinese_converter():
    funct_name = 'test_chinese_converter()'
    #x = chinese_converter.to_traditional("题目")#''line[﻿"题目"] = "东门行"'))
    #print(x)

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

    bronze_dir = get_received_bronzes_dir()
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
            #x = 'hello'
            if l == '匕':
                x = 1
            # if there are any vessel_categories in this line...
            x = btype_dict[current_category]
            if any(v_cat == l for v_cat in vessel_categories):
                current_category = l.strip()
                current_type = ''
                print('CATEGORY: ' + current_category)
                if current_category not in cat2type2cnt_dict:
                    cat2type2cnt_dict[current_category] = {}
                if current_category not in cat2type2data_dict:
                    cat2type2data_dict[current_category] = {}

                #cat2type2cnt_dict[current_category] += 1 --> need vessel type to
                if not cat_dict[current_category]:
                    #print(l)
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
                    #if len(l) < 3:
                        #print('prev_line = ' + prev_line)
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
    if 0:
        for k1 in cat2type2cnt_dict:
            for k2 in cat2type2cnt_dict[k1]:
                print('cat2type2cnt_dict[' + k1 + '][' + k2 + '] = ' + str(cat2type2cnt_dict[k1][k2]))
btype_dict = {}
def readin_bronze_type_dict(verbose=False):
    funct_name = 'readin_bronze_type_dict()'
    global btype_dict
    if btype_dict:
        return
    input_file = os.path.join(get_received_bronzes_dir(), 'raw', 'Abbyy', 'indexing-data.txt')
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

def get_gbk():
    return "\u9515\u7691\u853c\u788d\u7231\u55f3\u5ad2\u7477\u66a7\u972d\u8c19\u94f5\u9e4c\u80ae\u8884\u5965\u5aaa\u9a9c\u9ccc\u575d\u7f62\u94af\u6446\u8d25\u5457\u9881\u529e\u7eca\u94a3\u5e2e\u7ed1\u9551\u8c24\u5265\u9971\u5b9d\u62a5\u9c8d\u9e28\u9f85\u8f88\u8d1d\u94a1\u72c8\u5907\u60eb\u9e4e\u8d32\u951b\u7ef7\u7b14\u6bd5\u6bd9\u5e01\u95ed\u835c\u54d4\u6ed7\u94cb\u7b5a\u8df8\u8fb9\u7f16\u8d2c\u53d8\u8fa9\u8fab\u82c4\u7f0f\u7b3e\u6807\u9aa0\u98d1\u98d9\u9556\u9573\u9cd4\u9cd6\u522b\u762a\u6fd2\u6ee8\u5bbe\u6448\u50a7\u7f24\u69df\u6ba1\u8191\u9554\u9acc\u9b13\u997c\u7980\u62e8\u94b5\u94c2\u9a73\u997d\u94b9\u9e41\u8865\u94b8\u8d22\u53c2\u8695\u6b8b\u60ed\u60e8\u707f\u9a96\u9eea\u82cd\u8231\u4ed3\u6ca7\u5395\u4fa7\u518c\u6d4b\u607b\u5c42\u8be7\u9538\u4faa\u9497\u6400\u63ba\u8749\u998b\u8c17\u7f20\u94f2\u4ea7\u9610\u98a4\u5181\u8c04\u8c36\u8487\u5fcf\u5a75\u9aa3\u89c7\u7985\u9561\u573a\u5c1d\u957f\u507f\u80a0\u5382\u7545\u4f25\u82cc\u6005\u960a\u9cb3\u949e\u8f66\u5f7b\u7817\u5c18\u9648\u886c\u4f27\u8c0c\u6987\u789c\u9f80\u6491\u79f0\u60e9\u8bda\u9a8b\u67a8\u67fd\u94d6\u94db\u75f4\u8fdf\u9a70\u803b\u9f7f\u70bd\u996c\u9e31\u51b2\u51b2\u866b\u5ba0\u94f3\u7574\u8e0c\u7b79\u7ef8\u4fe6\u5e31\u96e0\u6a71\u53a8\u9504\u96cf\u7840\u50a8\u89e6\u5904\u520d\u7ecc\u8e70\u4f20\u948f\u75ae\u95ef\u521b\u6006\u9524\u7f0d\u7eaf\u9e51\u7ef0\u8f8d\u9f8a\u8f9e\u8bcd\u8d50\u9e5a\u806a\u8471\u56f1\u4ece\u4e1b\u82c1\u9aa2\u679e\u51d1\u8f8f\u8e7f\u7a9c\u64ba\u9519\u9509\u9e7e\u8fbe\u54d2\u9791\u5e26\u8d37\u9a80\u7ed0\u62c5\u5355\u90f8\u63b8\u80c6\u60ee\u8bde\u5f39\u6b9a\u8d55\u7605\u7baa\u5f53\u6321\u515a\u8361\u6863\u8c20\u7800\u88c6\u6363\u5c9b\u7977\u5bfc\u76d7\u7118\u706f\u9093\u956b\u654c\u6da4\u9012\u7f14\u7c74\u8bcb\u8c1b\u7ee8\u89cc\u955d\u98a0\u70b9\u57ab\u7535\u5dc5\u94bf\u766b\u9493\u8c03\u94eb\u9cb7\u8c0d\u53e0\u9cbd\u9489\u9876\u952d\u8ba2\u94e4\u4e22\u94e5\u4e1c\u52a8\u680b\u51bb\u5cbd\u9e2b\u7aa6\u728a\u72ec\u8bfb\u8d4c\u9540\u6e0e\u691f\u724d\u7b03\u9ee9\u953b\u65ad\u7f0e\u7c16\u5151\u961f\u5bf9\u603c\u9566\u5428\u987f\u949d\u7096\u8db8\u593a\u5815\u94ce\u9e45\u989d\u8bb9\u6076\u997f\u8c14\u57a9\u960f\u8f6d\u9507\u9537\u9e57\u989a\u989b\u9cc4\u8bf6\u513f\u5c14\u9975\u8d30\u8fe9\u94d2\u9e38\u9c95\u53d1\u7f5a\u9600\u73d0\u77fe\u9492\u70e6\u8d29\u996d\u8bbf\u7eba\u94ab\u9c82\u98de\u8bfd\u5e9f\u8d39\u7eef\u9544\u9cb1\u7eb7\u575f\u594b\u6124\u7caa\u507e\u4e30\u67ab\u950b\u98ce\u75af\u51af\u7f1d\u8bbd\u51e4\u6ca3\u80a4\u8f90\u629a\u8f85\u8d4b\u590d\u8d1f\u8ba3\u5987\u7f1a\u51eb\u9a78\u7ec2\u7ecb\u8d59\u9eb8\u9c8b\u9cc6\u9486\u8be5\u9499\u76d6\u8d45\u6746\u8d76\u79c6\u8d63\u5c34\u64c0\u7ec0\u5188\u521a\u94a2\u7eb2\u5c97\u6206\u9550\u777e\u8bf0\u7f1f\u9506\u6401\u9e3d\u9601\u94ec\u4e2a\u7ea5\u9549\u988d\u7ed9\u4e98\u8d53\u7ee0\u9ca0\u9f9a\u5bab\u5de9\u8d21\u94a9\u6c9f\u82df\u6784\u8d2d\u591f\u8bdf\u7f11\u89cf\u86ca\u987e\u8bc2\u6bc2\u94b4\u9522\u9e2a\u9e44\u9e58\u5250\u6302\u9e39\u63b4\u5173\u89c2\u9986\u60ef\u8d2f\u8bd6\u63bc\u9e73\u9ccf\u5e7f\u72b7\u89c4\u5f52\u9f9f\u95fa\u8f68\u8be1\u8d35\u523d\u5326\u523f\u59ab\u6867\u9c91\u9cdc\u8f8a\u6eda\u886e\u7ef2\u9ca7\u9505\u56fd\u8fc7\u57da\u5459\u5e3c\u6901\u8748\u94ea\u9a87\u97e9\u6c49\u961a\u7ed7\u9889\u53f7\u704f\u98a2\u9602\u9e64\u8d3a\u8bc3\u9616\u86ce\u6a2a\u8f70\u9e3f\u7ea2\u9ec9\u8ba7\u836d\u95f3\u9c8e\u58f6\u62a4\u6caa\u6237\u6d52\u9e55\u54d7\u534e\u753b\u5212\u8bdd\u9a85\u6866\u94e7\u6000\u574f\u6b22\u73af\u8fd8\u7f13\u6362\u5524\u75ea\u7115\u6da3\u5942\u7f33\u953e\u9ca9\u9ec4\u8c0e\u9cc7\u6325\u8f89\u6bc1\u8d3f\u79fd\u4f1a\u70e9\u6c47\u8bb3\u8bf2\u7ed8\u8bd9\u835f\u54d5\u6d4d\u7f0b\u73f2\u6656\u8364\u6d51\u8be8\u9984\u960d\u83b7\u8d27\u7978\u94ac\u956c\u51fb\u673a\u79ef\u9965\u8ff9\u8ba5\u9e21\u7ee9\u7f09\u6781\u8f91\u7ea7\u6324\u51e0\u84df\u5242\u6d4e\u8ba1\u8bb0\u9645\u7ee7\u7eaa\u8ba6\u8bd8\u8360\u53fd\u54dc\u9aa5\u7391\u89ca\u9f51\u77f6\u7f81\u867f\u8dfb\u9701\u9c9a\u9cab\u5939\u835a\u988a\u8d3e\u94be\u4ef7\u9a7e\u90cf\u6d43\u94d7\u9553\u86f2\u6b7c\u76d1\u575a\u7b3a\u95f4\u8270\u7f04\u8327\u68c0\u78b1\u7877\u62e3\u6361\u7b80\u4fed\u51cf\u8350\u69db\u9274\u8df5\u8d31\u89c1\u952e\u8230\u5251\u996f\u6e10\u6e85\u6da7\u8c0f\u7f23\u620b\u622c\u7751\u9e63\u7b15\u9ca3\u97af\u5c06\u6d46\u848b\u6868\u5956\u8bb2\u9171\u7edb\u7f30\u80f6\u6d47\u9a84\u5a07\u6405\u94f0\u77eb\u4fa5\u811a\u997a\u7f34\u7ede\u8f7f\u8f83\u6322\u5ce4\u9e6a\u9c9b\u9636\u8282\u6d01\u7ed3\u8beb\u5c4a\u7596\u988c\u9c92\u7d27\u9526\u4ec5\u8c28\u8fdb\u664b\u70ec\u5c3d\u52b2\u8346\u830e\u537a\u8369\u9991\u7f19\u8d46\u89d0\u9cb8\u60ca\u7ecf\u9888\u9759\u955c\u5f84\u75c9\u7ade\u51c0\u522d\u6cfe\u8ff3\u5f2a\u80eb\u9753\u7ea0\u53a9\u65e7\u9604\u9e20\u9e6b\u9a79\u4e3e\u636e\u952f\u60e7\u5267\u8bb5\u5c66\u6989\u98d3\u949c\u9514\u7aad\u9f83\u9e43\u7ee2\u9529\u954c\u96bd\u89c9\u51b3\u7edd\u8c32\u73cf\u94a7\u519b\u9a8f\u76b2\u5f00\u51ef\u5240\u57b2\u5ffe\u607a\u94e0\u9534\u9f9b\u95f6\u94aa\u94d0\u9897\u58f3\u8bfe\u9a92\u7f02\u8f72\u94b6\u951e\u9894\u57a6\u6073\u9f88\u94ff\u62a0\u5e93\u88e4\u55be\u5757\u4fa9\u90d0\u54d9\u810d\u5bbd\u72ef\u9acb\u77ff\u65f7\u51b5\u8bd3\u8bf3\u909d\u5739\u7ea9\u8d36\u4e8f\u5cbf\u7aa5\u9988\u6e83\u532e\u8489\u6126\u8069\u7bd1\u9603\u951f\u9cb2\u6269\u9614\u86f4\u8721\u814a\u83b1\u6765\u8d56\u5d03\u5f95\u6d9e\u6fd1\u8d49\u7750\u94fc\u765e\u7c41\u84dd\u680f\u62e6\u7bee\u9611\u5170\u6f9c\u8c30\u63fd\u89c8\u61d2\u7f06\u70c2\u6ee5\u5c9a\u6984\u6593\u9567\u8934\u7405\u9606\u9512\u635e\u52b3\u6d9d\u5520\u5d02\u94d1\u94f9\u75e8\u4e50\u9cd3\u956d\u5792\u7c7b\u6cea\u8bd4\u7f27\u7bf1\u72f8\u79bb\u9ca4\u793c\u4e3d\u5389\u52b1\u783e\u5386\u6ca5\u96b6\u4fea\u90e6\u575c\u82c8\u8385\u84e0\u5456\u9026\u9a8a\u7f21\u67a5\u680e\u8f79\u783a\u9502\u9e42\u75a0\u7c9d\u8dde\u96f3\u9ca1\u9ce2\u4fe9\u8054\u83b2\u8fde\u9570\u601c\u6d9f\u5e18\u655b\u8138\u94fe\u604b\u70bc\u7ec3\u8539\u5941\u6f4b\u740f\u6b93\u88e2\u88e3\u9ca2\u7cae\u51c9\u4e24\u8f86\u8c05\u9b49\u7597\u8fbd\u9563\u7f2d\u948c\u9e69\u730e\u4e34\u90bb\u9cde\u51db\u8d41\u853a\u5eea\u6aa9\u8f9a\u8e8f\u9f84\u94c3\u7075\u5cad\u9886\u7eeb\u68c2\u86cf\u9cae\u998f\u5218\u6d4f\u9a9d\u7efa\u954f\u9e68\u9f99\u804b\u5499\u7b3c\u5784\u62e2\u9647\u830f\u6cf7\u73d1\u680a\u80e7\u783b\u697c\u5a04\u6402\u7bd3\u507b\u848c\u55bd\u5d5d\u9542\u7618\u8027\u877c\u9ac5\u82a6\u5362\u9885\u5e90\u7089\u63b3\u5364\u864f\u9c81\u8d42\u7984\u5f55\u9646\u5786\u64b8\u565c\u95fe\u6cf8\u6e0c\u680c\u6a79\u8f73\u8f82\u8f98\u6c07\u80ea\u9e2c\u9e6d\u823b\u9c88\u5ce6\u631b\u5b6a\u6ee6\u4e71\u8114\u5a08\u683e\u9e3e\u92ae\u62a1\u8f6e\u4f26\u4ed1\u6ca6\u7eb6\u8bba\u56f5\u841d\u7f57\u903b\u9523\u7ba9\u9aa1\u9a86\u7edc\u8366\u7321\u6cfa\u6924\u8136\u9559\u9a74\u5415\u94dd\u4fa3\u5c61\u7f15\u8651\u6ee4\u7eff\u6988\u891b\u950a\u5452\u5988\u739b\u7801\u8682\u9a6c\u9a82\u5417\u551b\u5b37\u6769\u4e70\u9ea6\u5356\u8fc8\u8109\u52a2\u7792\u9992\u86ee\u6ee1\u8c29\u7f26\u9558\u98a1\u9cd7\u732b\u951a\u94c6\u8d38\u9ebd\u6ca1\u9541\u95e8\u95f7\u4eec\u626a\u7116\u61d1\u9494\u9530\u68a6\u772f\u8c1c\u5f25\u89c5\u5e42\u8288\u8c27\u7315\u7962\u7ef5\u7f05\u6e11\u817c\u9efe\u5e99\u7f08\u7f2a\u706d\u60af\u95fd\u95f5\u7f17\u9e23\u94ed\u8c2c\u8c1f\u84e6\u998d\u6b81\u9546\u8c0b\u4ea9\u94bc\u5450\u94a0\u7eb3\u96be\u6320\u8111\u607c\u95f9\u94d9\u8bb7\u9981\u5185\u62df\u817b\u94cc\u9cb5\u64b5\u8f87\u9cb6\u917f\u9e1f\u8311\u8885\u8042\u556e\u954a\u954d\u9667\u8616\u55eb\u989f\u8e51\u67e0\u72de\u5b81\u62e7\u6cde\u82ce\u549b\u804d\u94ae\u7ebd\u8113\u6d53\u519c\u4fac\u54dd\u9a7d\u9495\u8bfa\u50a9\u759f\u6b27\u9e25\u6bb4\u5455\u6ca4\u8bb4\u6004\u74ef\u76d8\u8e52\u5e9e\u629b\u75b1\u8d54\u8f94\u55b7\u9e4f\u7eb0\u7f74\u94cd\u9a97\u8c1d\u9a88\u98d8\u7f25\u9891\u8d2b\u5ad4\u82f9\u51ed\u8bc4\u6cfc\u9887\u948b\u6251\u94fa\u6734\u8c31\u9564\u9568\u6816\u8110\u9f50\u9a91\u5c82\u542f\u6c14\u5f03\u8bab\u8572\u9a90\u7eee\u6864\u789b\u9880\u9883\u9ccd\u7275\u948e\u94c5\u8fc1\u7b7e\u8c26\u94b1\u94b3\u6f5c\u6d45\u8c34\u5811\u4f65\u8368\u60ad\u9a9e\u7f31\u6920\u94a4\u67aa\u545b\u5899\u8537\u5f3a\u62a2\u5af1\u6a2f\u6217\u709d\u9516\u9535\u956a\u7f9f\u8dc4\u9539\u6865\u4e54\u4fa8\u7fd8\u7a8d\u8bee\u8c2f\u835e\u7f32\u7857\u8df7\u7a83\u60ec\u9532\u7ba7\u94a6\u4eb2\u5bdd\u9513\u8f7b\u6c22\u503e\u9877\u8bf7\u5e86\u63ff\u9cad\u743c\u7a77\u8315\u86f1\u5def\u8d47\u866e\u9cc5\u8d8b\u533a\u8eaf\u9a71\u9f8b\u8bce\u5c96\u9612\u89d1\u9e32\u98a7\u6743\u529d\u8be0\u7efb\u8f81\u94e8\u5374\u9e4a\u786e\u9615\u9619\u60ab\u8ba9\u9976\u6270\u7ed5\u835b\u5a06\u6861\u70ed\u97e7\u8ba4\u7eab\u996a\u8f6b\u8363\u7ed2\u5d58\u877e\u7f1b\u94f7\u98a6\u8f6f\u9510\u86ac\u95f0\u6da6\u6d12\u8428\u98d2\u9cc3\u8d5b\u4f1e\u6bf5\u7cc1\u4e27\u9a9a\u626b\u7f2b\u6da9\u556c\u94ef\u7a51\u6740\u5239\u7eb1\u94e9\u9ca8\u7b5b\u6652\u917e\u5220\u95ea\u9655\u8d61\u7f2e\u8baa\u59d7\u9a9f\u9490\u9cdd\u5892\u4f24\u8d4f\u57a7\u6b87\u89de\u70e7\u7ecd\u8d4a\u6444\u6151\u8bbe\u538d\u6ee0\u7572\u7ec5\u5ba1\u5a76\u80be\u6e17\u8bdc\u8c02\u6e16\u58f0\u7ef3\u80dc\u5e08\u72ee\u6e7f\u8bd7\u65f6\u8680\u5b9e\u8bc6\u9a76\u52bf\u9002\u91ca\u9970\u89c6\u8bd5\u8c25\u57d8\u83b3\u5f11\u8f7c\u8d33\u94c8\u9ca5\u5bff\u517d\u7ef6\u67a2\u8f93\u4e66\u8d4e\u5c5e\u672f\u6811\u7ad6\u6570\u6445\u7ebe\u5e05\u95e9\u53cc\u8c01\u7a0e\u987a\u8bf4\u7855\u70c1\u94c4\u4e1d\u9972\u53ae\u9a77\u7f0c\u9536\u9e36\u8038\u6002\u9882\u8bbc\u8bf5\u64de\u85ae\u998a\u98d5\u953c\u82cf\u8bc9\u8083\u8c21\u7a23\u867d\u968f\u7ee5\u5c81\u8c07\u5b59\u635f\u7b0b\u836a\u72f2\u7f29\u7410\u9501\u5522\u7743\u736d\u631e\u95fc\u94ca\u9cce\u53f0\u6001\u949b\u9c90\u644a\u8d2a\u762b\u6ee9\u575b\u8c2d\u8c08\u53f9\u6619\u94bd\u952c\u9878\u6c64\u70eb\u50a5\u9967\u94f4\u9557\u6d9b\u7ee6\u8ba8\u97ec\u94fd\u817e\u8a8a\u9511\u9898\u4f53\u5c49\u7f07\u9e48\u9617\u6761\u7c9c\u9f86\u9ca6\u8d34\u94c1\u5385\u542c\u70c3\u94dc\u7edf\u6078\u5934\u94ad\u79c3\u56fe\u948d\u56e2\u629f\u9893\u8715\u9968\u8131\u9e35\u9a6e\u9a7c\u692d\u7ba8\u9f0d\u889c\u5a32\u817d\u5f2f\u6e7e\u987d\u4e07\u7ea8\u7efe\u7f51\u8f8b\u97e6\u8fdd\u56f4\u4e3a\u6f4d\u7ef4\u82c7\u4f1f\u4f2a\u7eac\u8c13\u536b\u8bff\u5e0f\u95f1\u6ca9\u6da0\u73ae\u97ea\u709c\u9c94\u6e29\u95fb\u7eb9\u7a33\u95ee\u960c\u74ee\u631d\u8717\u6da1\u7a9d\u5367\u83b4\u9f8c\u545c\u94a8\u4e4c\u8bec\u65e0\u829c\u5434\u575e\u96fe\u52a1\u8bef\u90ac\u5e91\u6003\u59a9\u9a9b\u9e49\u9e5c\u9521\u727a\u88ad\u4e60\u94e3\u620f\u7ec6\u9969\u960b\u73ba\u89cb\u867e\u8f96\u5ce1\u4fa0\u72ed\u53a6\u5413\u7856\u9c9c\u7ea4\u8d24\u8854\u95f2\u663e\u9669\u73b0\u732e\u53bf\u9985\u7fa1\u5baa\u7ebf\u82cb\u83b6\u85d3\u5c98\u7303\u5a34\u9e47\u75eb\u869d\u7c7c\u8df9\u53a2\u9576\u4e61\u8be6\u54cd\u9879\u8297\u9977\u9aa7\u7f03\u98e8\u8427\u56a3\u9500\u6653\u5578\u54d3\u6f47\u9a81\u7ee1\u67ad\u7bab\u534f\u631f\u643a\u80c1\u8c10\u5199\u6cfb\u8c22\u4eb5\u64b7\u7ec1\u7f2c\u950c\u8845\u5174\u9649\u8365\u51f6\u6c79\u9508\u7ee3\u9990\u9e3a\u865a\u5618\u987b\u8bb8\u53d9\u7eea\u7eed\u8be9\u987c\u8f69\u60ac\u9009\u7663\u7eda\u8c16\u94c9\u955f\u5b66\u8c11\u6cf6\u9cd5\u52cb\u8be2\u5bfb\u9a6f\u8bad\u8baf\u900a\u57d9\u6d54\u9c9f\u538b\u9e26\u9e2d\u54d1\u4e9a\u8bb6\u57ad\u5a05\u6860\u6c29\u9609\u70df\u76d0\u4e25\u5ca9\u989c\u960e\u8273\u538c\u781a\u5f66\u8c1a\u9a8c\u53a3\u8d5d\u4fe8\u5156\u8c33\u6079\u95eb\u917d\u9b47\u990d\u9f39\u9e2f\u6768\u626c\u75a1\u9633\u75d2\u517b\u6837\u7080\u7476\u6447\u5c27\u9065\u7a91\u8c23\u836f\u8f7a\u9e5e\u9cd0\u7237\u9875\u4e1a\u53f6\u9765\u8c12\u90ba\u6654\u70e8\u533b\u94f1\u9890\u9057\u4eea\u8681\u827a\u4ebf\u5fc6\u4e49\u8be3\u8bae\u8c0a\u8bd1\u5f02\u7ece\u8bd2\u5453\u5cc4\u9974\u603f\u9a7f\u7f22\u8f76\u8d3b\u9487\u9552\u9571\u7617\u8223\u836b\u9634\u94f6\u996e\u9690\u94df\u763e\u6a31\u5a74\u9e70\u5e94\u7f28\u83b9\u8424\u8425\u8367\u8747\u8d62\u9896\u8314\u83ba\u8426\u84e5\u6484\u5624\u6ee2\u6f46\u748e\u9e66\u763f\u988f\u7f42\u54df\u62e5\u4f63\u75c8\u8e0a\u548f\u955b\u4f18\u5fe7\u90ae\u94c0\u72b9\u8bf1\u83b8\u94d5\u9c7f\u8206\u9c7c\u6e14\u5a31\u4e0e\u5c7f\u8bed\u72f1\u8a89\u9884\u9a6d\u4f1b\u4fe3\u8c00\u8c15\u84e3\u5d5b\u996b\u9608\u59aa\u7ea1\u89ce\u6b24\u94b0\u9e46\u9e6c\u9f89\u9e33\u6e0a\u8f95\u56ed\u5458\u5706\u7f18\u8fdc\u6a7c\u9e22\u9f0b\u7ea6\u8dc3\u94a5\u7ca4\u60a6\u9605\u94ba\u90e7\u5300\u9668\u8fd0\u8574\u915d\u6655\u97f5\u90d3\u82b8\u607d\u6120\u7ead\u97eb\u6b92\u6c32\u6742\u707e\u8f7d\u6512\u6682\u8d5e\u74d2\u8db1\u933e\u8d43\u810f\u9a75\u51ff\u67a3\u8d23\u62e9\u5219\u6cfd\u8d5c\u5567\u5e3b\u7ba6\u8d3c\u8c2e\u8d60\u7efc\u7f2f\u8f67\u94e1\u95f8\u6805\u8bc8\u658b\u503a\u6be1\u76cf\u65a9\u8f97\u5d2d\u6808\u6218\u7efd\u8c35\u5f20\u6da8\u5e10\u8d26\u80c0\u8d75\u8bcf\u948a\u86f0\u8f99\u9517\u8fd9\u8c2a\u8f84\u9e67\u8d1e\u9488\u4fa6\u8bca\u9547\u9635\u6d48\u7f1c\u6862\u8f78\u8d48\u796f\u9e29\u6323\u7741\u72f0\u4e89\u5e27\u75c7\u90d1\u8bc1\u8be4\u5ce5\u94b2\u94ee\u7b5d\u7ec7\u804c\u6267\u7eb8\u631a\u63b7\u5e1c\u8d28\u6ede\u9a98\u6809\u6800\u8f75\u8f7e\u8d3d\u9e37\u86f3\u7d77\u8e2c\u8e2f\u89ef\u949f\u7ec8\u79cd\u80bf\u4f17\u953a\u8bcc\u8f74\u76b1\u663c\u9aa4\u7ea3\u7ec9\u732a\u8bf8\u8bdb\u70db\u77a9\u5631\u8d2e\u94f8\u9a7b\u4f2b\u69e0\u94e2\u4e13\u7816\u8f6c\u8d5a\u556d\u9994\u989e\u6869\u5e84\u88c5\u5986\u58ee\u72b6\u9525\u8d58\u5760\u7f00\u9a93\u7f12\u8c06\u51c6\u7740\u6d4a\u8bfc\u956f\u5179\u8d44\u6e0d\u8c18\u7f01\u8f8e\u8d40\u7726\u9531\u9f87\u9cbb\u8e2a\u603b\u7eb5\u506c\u90b9\u8bf9\u9a7a\u9cb0\u8bc5\u7ec4\u955e\u94bb\u7f35\u8e9c\u9cdf\u7ff1\u5e76\u535c\u6c89\u4e11\u6dc0\u8fed\u6597\u8303\u5e72\u768b\u7845\u67dc\u540e\u4f19\u79f8\u6770\u8bc0\u5938\u91cc\u51cc\u4e48\u9709\u637b\u51c4\u6266\u5723\u5c38\u62ac\u6d82\u6d3c\u5582\u6c61\u9528\u54b8\u874e\u5f5d\u6d8c\u6e38\u5401\u5fa1\u613f\u5cb3\u4e91\u7076\u624e\u672d\u7b51\u4e8e\u5fd7\u6ce8\u51cb\u8ba0\u8c2b\u90c4\u52d0\u51fc\u5742\u5785\u57b4\u57ef\u57dd\u82d8\u836c\u836e\u839c\u83bc\u83f0\u85c1\u63f8\u5412\u5423\u5494\u549d\u54b4\u5658\u567c\u56af\u5e5e\u5c99\u5d74\u5f77\u5fbc\u72b8\u72cd\u9980\u9987\u9993\u9995\u6123\u61b7\u61d4\u4e2c\u6e86\u6edf\u6eb7\u6f24\u6f74\u6fb9\u752f\u7e9f\u7ed4\u7ef1\u73c9\u67a7\u684a\u6849\u69d4\u6a65\u8f71\u8f77\u8d4d\u80b7\u80e8\u98da\u7173\u7145\u7198\u610d\u6dfc\u781c\u78d9\u770d\u949a\u94b7\u94d8\u94de\u9503\u950d\u950e\u950f\u9518\u951d\u952a\u952b\u953f\u9545\u954e\u9562\u9565\u9569\u9572\u7a06\u9e4b\u9e5b\u9e71\u75ac\u75b4\u75d6\u766f\u88e5\u8941\u8022\u98a5\u87a8\u9eb4\u9c85\u9c86\u9c87\u9c9e\u9cb4\u9cba\u9cbc\u9cca\u9ccb\u9cd8\u9cd9\u9792\u97b4\u9f44"

def sinopy_test():
    import sinopy
    gbk = get_gbk()
    print(str(len(gbk)))

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
    #for lp in lu_poem_names:
    #    print(lp)
    #for rh in raw_han_names:
    #    print(rh)
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
    #raw_han_short = list(numpy.array(raw_han_names) - numpy.array(intersec))
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
    #cydifflib.get_close_matches()

def parse_han_data_from_lu_1983():
    funct_name = 'parse_han_data_from_lu_1983()'
    is_verbose = False
    delim = '\t'
    line_return ='\n'
    output_file = os.path.join(get_received_shi_dir(), 'processed-Lu-1983-先秦漢魏晉南北朝詩.txt')
    # if output file already exists, delete it
    if os.path.isfile(output_file):
        os.remove(output_file)
    # add labels to the output file
    label_list = ['Unique Poem#', 'Juan.Seq#', 'Poem Name', 'Poet\'s Name', 'Poet Intro', 'Poem Refs',
                  'Poem Commentary', 'Poem Content']
    append_line_to_output_file(output_file, delim.join(label_list) + line_return)
    #parse_han_data_from_lu_1983_form_poems_with_poet_names(is_verbose)
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
#   read in Lu 1983 data from pre-processed file
def readin_lu_1983_data(is_verbose=False):
    funct_name = 'readin_lu_1983_data()'
    global lu1983_dict
    global lu1983_labels
    if lu1983_dict:
        return lu1983_labels
    input_file = os.path.join(get_received_shi_dir(), 'processed-Lu-1983-先秦漢魏晉南北朝詩.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Input file INVALID!')
        print('\t' + input_file)
        return []
    line_list = readlines_of_utf8_file(input_file)
    lu1983_labels = line_list[0][:]
    line_list = line_list[1:len(line_list)]
    for l in line_list:
        if is_verbose:
            print(l)
        if '莫莫高山。' in l:
            x = 1
        l = l.split('\t')
        unique_id = l[0]
        l = l[1:len(l)]
        lu1983_dict[unique_id] = '\t'.join(l)
    return lu1983_labels

schuessler = ''
def load_schuessler_data():
    global schuessler
    if schuessler:
        return
    schuessler = sch_glyph2phonology()

def get_schuessler_late_han_for_glyph(glyph):
    load_schuessler_data()
    return schuessler.get_late_han(glyph)

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
    #test_poem = ['步出城東門。遙望江南路。前日風雪中。故人從此去。我欲渡河水。河水深無梁。願為雙黃鵠。高飛還故鄉。']
    #test_poem = ''
    for stanza in test_poem:
        stanza = stanza.split('。')
        for s in stanza:
            if s:
                last_char = s[len(s)-1]
                lc_late_han = schuessler.get_late_han(last_char)
                print(s + '(' + lc_late_han + ')。')


    if 0:
        for k in lu1983_dict:
            #print(k + ': ')# + lu1983_dict[k])
            lu_poem.set_data_with_line_from_file(k, lu1983_dict[k])
            uniqid2poem_dict[k] = ''
            uniqid2poem_dict[k] = deepcopy(lu_poem)
        for k in uniqid2poem_dict:
            print('-'*50)
            poem = uniqid2poem_dict[k].get_poem_content_as_str()

            #uniqid2poem_dict[k].print_poem_content()

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

def grab_last_character_in_line(line):
    funct_name = 'grab_last_character_in_line()'
    # take into account 虛字 like 之、兮、乎, etc
    if not line.strip():
        return ''
    exception_chars = ['之', '兮', '乎', '也']
    last_char = line[len(line)-1]
    if last_char in exception_chars:
        last_char = line[len(line)-2]
    return last_char

def get_kmss2015_rhyme_words_naively(inscription, unique_id, ignore_unpunctuated=True):
    funct_name = 'get_rhyme_words_naively()'
    retval = {}
    if ignore_unpunctuated and '。' not in inscription and '，' not in inscription:
        print(funct_name + ' poem not punctuated with 「。」')
        print('stanza=' + stanza)
        return retval
    #len2num_occ_dict = {}
    stanza = stanza.split('。')
    line_inc = 0
    rw2line_dict = {}
    for line in stanza:
        if not line.strip():
            continue
        line_inc += 1
        # if line_inc is a multiple of 2
        if not line_inc % 2:
            #print('line_inc=' + str(line_inc))
            line_id = unique_id + '.' + str(line_inc)
            #if len(line) < line_length:
            #    continue
            #zi = line[line_length-1]
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
        #len2num_occ_dict = {}
        stanza = stanza.split('。')
        line_inc = 0
        rw2line_dict = {}
        for line in stanza:
            if not line.strip():
                continue
            line_inc += 1
            # if line_inc is a multiple of 2
            if not line_inc % 2:
                #print('line_inc=' + str(line_inc))
                line_id = unique_id + '.' + str(line_inc)
                #if len(line) < line_length:
                #    continue
                #zi = line[line_length-1]
                if '兮' == line[len(line)-1]: # remove '兮' if it appears as last character in line
                    line = line[0:len(line)-1]
                zi = line[len(line) - 1]
                if zi == '□' or zi == '…' or zi == '・':
                    continue
                if zi not in rw2line_dict:
                    rw2line_dict[zi] = []
                rw2line_dict[zi].append((line,line_id))
    return rw2line_dict
        # grab_last_character_in_line


def naively_annotate_han_dynasty_poems():
    funct_name = 'naively_annotate_han_dynasty_poems()'
    readin_lu_1983_data()
    LU_poem = lu1983_poem()
    LU_poem.set_data_labels(lu1983_labels)
    uniqid2poem_dict = {}
    rhyme_net = rnetwork()
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
        #print('Processing k=' + k)
        #print(k + ': ')# + lu1983_dict[k])
        LU_poem.set_data_with_line_from_file(k, lu1983_dict[k])
        uniqid2poem_dict[k] = ''
        uniqid2poem_dict[k] = deepcopy(LU_poem)
    for k in uniqid2poem_dict:#lu1983_poem
        print('-'*50)
        poem = uniqid2poem_dict[k].get_poem_content_as_str()
        print(k + ': ' + poem)
        stanza_list = poem.split('\n')
        st_inc = 0
        #LU_poem.get
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

    #rnet_raw_data = rhyme_net.print_all_nodes_n_edges(False) # False = don't print to screen
    rhyme_net.get_infomap_linked_list_of_rhyme_network()

    #lu_graph = rhyme_net.get_networkx_graph_of_rhyme_network()

    #use_networkx_n_altair_visualization(lu_graph)
    #print('rnet_raw_data = ' )
    #for rrd in rnet_raw_data:
    #    print(rrd)
    #lu1983_graph.
    #lu1983_graph.    #.interactive() enables click-and-drag and zoom on the graph.
    if 1 and visualization_type == 'nx':
        alt.data_transformers.disable_max_rows()
        pos = nx.spring_layout(lu1983_graph)
        # Add attributes to each node.
        for n in lu1983_graph.nodes():
            #G.nodes[n]['weight'] = np.random.randn()
            lu1983_graph.nodes[n]['name'] = n
            #G.nodes[n]['viable'] = np.random.choice(['yes', 'no'])
    #
    # INFOMAP stuff
    # Run the Infomap search algorithm to find optimal modules

    if 1:
        #print(f"Found {im.num_top_modules} modules with codelength: {im.codelength}")
        #print("Result")
        #print("\n#node module")
        #for node in im.tree:
        ##    if node.is_leaf:
        #        print(node.node_id, node.module_id)
        #print('*'*100)

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
        # plt.show()

        viz.save('my_viz_test.html')
        alt_view.show(viz)
        graph = viz.interactive()
        for cluster_id in cluster2zi_dict:
            print(str(cluster_id) + ':')
            print('\t' + ''.join(cluster2zi_dict[cluster_id]))
        #return graph


def test_visualize_infomap_output():
    funct_name = 'test_visualize_infomap_output()'
    filename = 'lu1983_infomap_output.txt'
    visualize_infomap_output(filename)

def visualize_infomap_output(filename):
    funct_name = 'visualize_infomap_output()'
    line_list = readlines_of_utf8_file(filename)
    for ll in line_list:
        print(ll)

def is_unicode(text):
    retval = False
    if 'str' in str(type(text)):
        retval = True
    return retval

def append_line_to_utf8_file(filename, content):
    funct_name = 'append_line_to_utf8_file()'
    output_ptr = safe_open_utf8_file_for_appending(filename)
    output_ptr.write(content + '\n')
    if output_ptr:
        output_ptr.close()

def if_not_unicode_make_it_unicode(my_str):
    funct_name = 'if_not_unicode_make_it_unicode()'
    if not is_unicode(my_str):
        my_str = my_str.decode('utf8')
    return my_str

def safe_open_utf8_file_for_appending(filename):
    filename = if_not_unicode_make_it_unicode(filename)
    p, f = os.path.split(filename)
    if p and not os.path.isdir(p):  # if the directory doesn't exist, create it
        os.makedirs(p)
    return codecs.open(filename, 'a', 'utf8')


# 'saveas' must be a filename ending in .html
def use_networkx_n_altair_visualization(nx_graph, saveas=''):
    funct_name = 'use_networkx_n_altair_visualization()'
    print('Entering ' + funct_name + '...')
    alt.data_transformers.disable_max_rows()
    pos = nx.spring_layout(nx_graph)
    # Add attributes to each node.
    for n in nx_graph.nodes():
        #G.nodes[n]['weight'] = np.random.randn()
        nx_graph.nodes[n]['name'] = n
        #G.nodes[n]['viable'] = np.random.choice(['yes', 'no'])

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
    #if juan_num not in juan_num2data_dict:
    #    juan_num2data_dict[juan_num] = {}
    #if seq_num not in juan_num2data_dict[juan_num]:
    #    juan_num2data_dict[juan_num][seq_num] = ''
    #juan_num2data_dict[juan_num][seq_num] = pmsg

#def get_schuessler_item_given_label(line, label, label_list):
class sch_glyph2phonology:
    def __init__(self):
        self.glyph2data = get_schuessler_late_han_data()
        #data = zh_ipa + delim + qy_ipa + delim + lh_ipa + delim + ocm_ipa
        self.mandarin_pos = 0
        self.qieyun_pos = 1
        self.late_han_pos = 2
        self.min_oc_pos = 3

    def print_all_data(self):
        for k in self.glyph2data:
            print('glyph2data[' + k + '] = ' + '\n'.join(self.glyph2data[k]))

    def print_all_mandarin(self):
        for k in self.glyph2data:
            print(k + ': ' + self.get_mandarin(k))

    def print_all_qieyun(self):
        for k in self.glyph2data:
            print(k + ': ' + self.get_qieyun(k))

    def print_all_late_han(self):
        inc = 0
        for k in self.glyph2data:
            x = self.get_late_han(k)
            late_han = self.get_late_han(k)
            if late_han:
                late_han = late_han.split(' ')
            if len(late_han) >= 1:
                print(k + ': ' + ' '.join(late_han))
            if self.get_late_han(k).strip():
                inc += 1
        print(str(inc) + ' entries have LHan data.')

    def print_all_ocm(self):
        inc = 0
        for k in self.glyph2data:
            ocm = self.get_ocm(k)
            print(k + ': ' + ocm)

    def get_late_han(self, glyph):
        retval = self.get_data_from_pos(glyph, self.late_han_pos)
        retval = list(set(retval.split(' ')))
        return ' '.join(retval)

    def get_ocm(self, glyph):
        return self.get_data_from_pos(glyph, self.min_oc_pos)

    def get_qieyun(self, glyph):
        return self.get_data_from_pos(glyph, self.qieyun_pos)

    def get_mandarin(self, glyph):
        return self.get_data_from_pos(glyph, self.mandarin_pos)
        #retval = []
        #try:
        #    for line in self.glyph2data[glyph]:#.split('\t')[self.mandarin_pos]
        #        retval.append(line.split('\t')[self.mandarin_pos])
        #except:
        #    x = 1
        #return ' '.join(retval)

    def get_data_from_pos(self, glyph, pos):
        retval = []
        #if glyph == '片':
        #    x = 1
        try:
            for line in self.glyph2data[glyph]:
                data = line.split('\t')[pos]
                if data not in retval:
                    if data.strip():
                        retval.append(data)
        except:
            x = 1
        return ' '.join(retval).strip()

def remove_dupes(data):
    data = data.split(' ')
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
    #if 0:
    #    line = line.split(' ')
    #    retval = ''
        #if '(' in line:
        #    x = 1
    #    for e in line:
    #        if 'ᴮ/ᶜ' in e:
    #            base = e.replace('ᴮ/ᶜ', '')
    #            retval += base + 'ᴮ ' + base + 'ᶜ '
    #        else:
    #            retval += e + ' '
    #    return retval.strip()

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


def get_schuessler_late_han_data(is_verbose=False):
    funct_name = 'get_schuessler_late_han_data()'
    input_file = os.path.join(get_schuesslerhanchinese_dir(), 'raw', 'SchuesslerTharsen.tsv')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: INVALID input file:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    if is_verbose:
        print('LABELS:')
        print('\t' + line_list[0])
    label_list = line_list[0]
    label_list = label_list.split('\t')
    line_list = line_list[1:len(line_list)] # remove labels
    if is_verbose:
        print('FORMAT: ')
        print('\t' + line_list[0])
    format_list = line_list[0]
    line_list = line_list[1:len(line_list)] # remove format
    # ID=1298	wf_pinyin={	wf_graph={	wf_relationship={	pinyin_index=gǔ1	graph=古	QY_IPA=kuoᴮ	LH	LH_IPA=kɑᴮ	OCM	OCM_IPA=*kâɁ
    num_labels = len(label_list)
    delim = '\t'
    retval = {}
    exceptions = ['箄 and other characters', '琥珀 < 虎魄', '姮娥 ~ 恆娥', '顥[Lü],昊', '艎 / 艕', '艕,艎', '嚅唲,儒兒',
                  '娥 (in héng-é)姮娥', '梃,鋌', '於兔,於瑙', '阤,陊 (duò) (Mand. tuó), 陊 (Mand. duò)', '杝,扡', '射油']
    except_dict = {'箄 and other characters':'箄', '琥珀 < 虎魄':'琥珀,虎魄', '姮娥 ~ 恆娥':'姮娥,恆娥', '顥[Lü],昊':'顥,昊',
                   '艎 / 艕':'', '娥 (in héng-é)姮娥':'', '阤,陊 (duò) (Mand. tuó), 陊 (Mand. duò)':'阤,陊','射油':'油'}
    #data = glyph + delim + zh_ipa + delim + qy_ipa + delim + lh_ipa + delim + ocm_ipa
    #
    # these line are exceptions in the data; just handle them directly hear and skip them in the normal processing
    lines2add = {'慚':'cuō3' + delim + 'tsʰâ,dzâ' + delim + delim,
                 '貸':'dài2'+ delim + delim + delim,
                 '潏':'jué10' + delim + delim + delim,
                 '蔚':'wèi11' + delim + delim + delim}
    #
    # LHan exceptions:
    lhan_exceptions = {'痣':'tśəᶜ kiəᶜ', '躓':'ṭis', '質':'tśit', '蛭':'tet tśit ṭit', '紙':'tśiɑiɁ kiɑiɁ',
                       '植':'dźik ḍəᶜ', '培':'bə bəuᴮ', '癠':'dzei dzeiᴮ dzeiᶜ', '讙':'xyɑn xion xuɑn', '檢':'kiɑmᴮ kiamᴮ',
                       '仔':'tsiə tsiəᴮ', '洚':'goŋ gouŋ g/kɔŋᶜ', '殺':'ṣat sɛt', '謾':'mian mɑn mɑnᶜ man manᶜ',
                       '院瑗':'wanᶜ wenᶜ', '抓':'tṣauᴮ tṣauᶜ', '綴':'ṭot ṭos ṭuas ṭuat', '翠':'tsʰus tsʰuis',
                       '率':'ṣuis ṣuit luit', '潏':'kuet juit jut', '鳳':'puəmᶜ buŋᶜ mie me ŋe', '青':'tsieŋ tseŋ tsʰeŋ',
                       '蒩':'tsiɑ tsɑ tsʰiɑ', '論':'luən lun luənᶜ', '芒':'muɑŋ mɑŋ huɑŋ', '麑':'ŋe mie me',
                       '能':'nə nəŋ', '聳':'sioŋᴮ tsʰioŋᶜ tsʰoŋᶜ','竦':'sioŋᴮ tsʰioŋᶜ tsʰoŋᶜ', '醒':'seŋ seŋᴮ seŋᶜ',
                       '蹂':'ńu ńuᴮ ńuᶜ', '來':'lə mɛk','繂':'luit', '繘':'kuit wit', '澗':'nuan nuanᶜ','汏':'dɑs',
                       '鬌':'tuɑiᴮ toiᴮ tuɑᴮ','揭':'gɨat kʰias', '皎':'keiauᴮ keuᴮ', '皦':'keiauᴮ keuᴮ', '匱':'gwis',
                       '餽':'gwih gwis', '饋':'gwih gwis', '潸':'ṣanᴮ ṣɛn ṣan', '焉':'Ɂɑn Ɂiɑn', '燕':'Ɂenᶜ Ɂenᴮ',
                       '毒': 'douk douh', '剬': 'tuɑn tśuanᴮ duɑn don tśuan tśion', '差':'tṣʰɑi tṣʰɛ tṣʰai',
                       '皇': 'guɑŋ Ɣuɑŋ', '煌': 'guɑŋ Ɣuɑŋ', '牛': 'ŋiu ŋu', '葚': 'dźimᴮ źimᴮ', '實': 'dźit źit',
                       '饁': 'wɑp jɑp', '適':'tśek śek', '夫':'buɑ puɑ', '棧':'dẓanᴮ dẓɛnᶜ dẓɛnᴮ'}
    ocm_exceptions = {'九':'*kuɁ kwəɁ', '啄':'*trôk *tôs *tôh *troh', '咮':'*tôks *tôs *tôh *troh', '凡':'*bom *bam',
                      '飯':'*bans *bons *ban', '肺':'*phots *phats', '胐':'*phəiɁ *phə̂t *phuiɁ *phut',
                      '補': '*mpaɁ *mpâɁ *pâɁ', '晨': '*m-dən *dən', '荒': '*hmâŋ *hmlaŋ *hmâŋ', '利': '*rih', '遐': '*gâ',
                      '望': '*maŋᴬ', '磏': '*ram *riam', '鎌':'*ram *riam', '鋁':'*raɁ', '坻':'*dri'}

    #data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
    left_outs2add = {'鵠':'hú gǔ' + delim + 'ɣuok kuok' + delim + 'gouk kouk' + delim + 'gûk kûk',
                     '飾':'shì' + delim + 'śjək' + delim + 'śɨk' + delim + 'lhək',
                     '葵':'kuí' + delim + 'gwi' + delim + 'gwi' + delim + 'gwi',
                     '羹':'gēng' + delim + 'kɐŋ' + delim + 'kaŋ' + delim + 'krâŋ',
                     '歇':'xiē' + delim + 'xjɐt' + delim + 'hɨɑt' + delim + 'hat',
                     '葩':'pā' + delim + 'pʰa' + delim + 'pʰa' + delim + '',
                     '桂':'guì' + delim + 'kiweiᶜ' + delim + 'kueᶜ' + delim + 'kwêh',
                     '鴦':'yāng' + delim + 'ʔjaŋ' + delim + 'ʔɨɑŋ' + delim + 'ʔɑŋ',
                     '絕':'jué' + delim + 'dzjwät' + delim + 'dzyat' + delim + 'dzot',
                     '芝':'zhī' + delim + 'tśɨ' + delim + 'tśɨ tśə' + delim + 'tə',
                     '兮':'xī' + delim + 'ɣiei' + delim + 'ɣei' + delim + 'gî',
                     '大':'dà dài' + delim + 'dâiᶜ' + delim + 'dɑs dɑh' + delim + 'dâs',
                     '返':'fǎn' + delim + 'pjwɐnᴮ' + delim + 'puɑnᴮ' + delim + 'panʔ',
                     '晚': 'wǎn' + delim + 'mjwɐnᴮ' + delim + 'muɑnᴮ' + delim + 'manʔ',
                     '憙':'xǐ' + delim + 'xjɨᴮ' + delim + 'hɨəᴮ hɨᴮ' + delim + 'həʔ',
                     '俙':'xī' + delim + 'xjei' + delim + 'hɨi' + delim + 'həi'}
    # '':'' + delim + '' + delim + '' + delim + ''
    # upside-down a - ɐ
    # funky i       - ɨ
    # phat a        - ɑ
    # umlauted a    - ä
    # tone a        - ᴬ
    # tone b        - ᴮ
    # tone c        - ᶜ
    # aspiration h  - ʰ
    # ng            - ŋ
    # glottal stop  - ʔ
    # schwa         - ə

    for k in left_outs2add:
        retval[k] = []
        retval[k].append(left_outs2add[k])
    #, '抓':''}#棧: dẓanᴮ or dẓɛnᴮ/ᶜ; 仔: tsiə(ᴮ);院: wanᶜ/wenᶜ;瑗: wanᶜ/wenᶜ; 禜: waŋ(ᶜ)
                                      #遺: wi wih wis?; 翳: Ɂei(h); 燕: Ɂenᶜ Ɂenᶜ ~ Ɂenᴮ; 剡: jamᴮ jamᴮ
    # 炫: Ɣ(u)enᶜ; 休: x(ɨ)u; 星: seŋ / S tsʰeŋ dzieŋ; 信: sinᶜ  sinᶜ; 笑: siauᶜ / S tsʰiauᶜ
    # 繘: kiut kuit ju(it -> LH	kiut (kuit),ju(i)t
    # 爰: wɑn wɑn
    #
    # process normal data
    #
    # TO DO (2022-04-14):
    #  - finish cleaning up Schuessler's Late Han data (starting with "S /":
    #     笑: tsʰiauᶜ S / siauᶜ;
    #     癬: tsʰiɑnᴮ sianᴮ S /
    #     涎: lanᴮ janᶜ zian S)
    #  - then: 望: muɑŋᴬ/ᶜ muɑŋ
    #  - 覃: dəm  jamᴮ (double space)
    #  - 說: śos śuɑs  śuat śot śos śuas (double space)
    #  - 蹂: ńu()ᴮ ńu()ᶜ; 醒: seŋ()ᴮ seŋ()ᶜ
    #  - 鉛: jyan / jon
    for k in lines2add:
        if k not in retval:
            retval[k] = []
        retval[k].append(lines2add[k])
    ids2skip = ['553', '579', '2054', '3922']
    for l in line_list:
        l = l.split(delim)
        len_l = len(l)
        ID = l[label_list.index('ID')]
        if ID in ids2skip:
            continue
        zh_ipa = l[label_list.index('pinyin_index')]
        glyph = l[label_list.index('graph')]
        if glyph == '○':
            continue

        if ',' in zh_ipa:
            zh_ipa = zh_ipa.replace(',', ' ')
            x = 1
        if '-' in zh_ipa and len(glyph) > 1:
            continue # this is a word with more than one syllable

        if is_verbose:
            print('ID=' + ID + ', glyph=' + glyph)
        if len(glyph) > 1:
            if glyph in except_dict: # these entries are handled above
                glyph = except_dict[glyph]
                if not glyph.strip():
                    zh_ipa = ''
                    continue
        qy_ipa = l[label_list.index('QY_IPA')]
        lh_ipa = l[label_list.index('LH_IPA')]
        #if glyph == '繘' or '繂' in glyph:
        #    x = 1
        lh_ipa = cleanup_late_han_ipa(lh_ipa)
        ocm_ipa = l[label_list.index('OCM_IPA')]
        ocm_ipa = cleanup_ocm_ipa(ocm_ipa)
        if ',' in glyph:
            for g in glyph.split(','):
                if g in lhan_exceptions:
                    lh_ipa = lhan_exceptions[g]
                if g in ocm_exceptions:
                    ocm_ipa = ocm_exceptions[g]
                if '  ' in lh_ipa:
                    lh_ipa = lh_ipa.replace('  ',' ')
                data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
                if g not in retval:
                    retval[g] = []
                if g == '片':
                    y = retval[g]
                    x = 1
                if data not in retval[g]:
                    if '  ' in data: # debug only
                        x = 1# debug only
                    retval[g].append(data)
        else:
            glyph = list(glyph)
            for g in glyph:
                if g in lhan_exceptions:
                    lh_ipa = lhan_exceptions[g]
                if g in ocm_exceptions:
                    ocm_ipa = ocm_exceptions[g]

                if '  ' in lh_ipa:
                    lh_ipa = lh_ipa.replace('  ',' ')
                #if g == '蟲':
                #    x = 1
                data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
                if is_verbose:
                    print('glyph=' + g)
                if g not in retval:
                    retval[g] = []
                if g == '片':
                    y = retval[g]
                    x = 1 # '率' made it here, 4x
                if data not in retval[g]:
                    if '  ' in data: # debug
                        x = 1 # debug
                    retval[g].append(data)
    if 0:#is_verbose:
        print(str(len(retval)) + ' lines.')
        total_cnt = 0
        for k in retval:
            if k == '率':
                y = retval[k]
                x = 1

            total_cnt += len(retval[k])
        print(str(total_cnt) + ' in total count.')


        #print(l)
        #print('\tzh_ipa: ' + zh_ipa + ', glyph: ' + glyph + ', qy_ipa: ' + qy_ipa + ', lh_ipa: ' + lh_ipa + ', ocm_ipa: ' + ocm_ipa)

    return retval

def test_schuessler_phonological_data():
    funct_name = 'test_schuessler_phonological_data()'
    schuessler = sch_glyph2phonology()
    #schuessler.print_all_data()
    #schuessler.print_all_mandarin()
    #schuessler.print_all_qieyun()
    #schuessler.print_all_late_han()
    schuessler.print_all_ocm()

def cleanup_ocm_ipa(ocm):
    if ' ~ ' in ocm:
        ocm = ocm.replace(' ~ ', ' ')  # just treat each one as a possibility
    if ' ?' in ocm:
        ocm = ocm.replace(' ?','')
    if '?' in ocm:
        ocm = ocm.replace('?', '')
    #if '(' not in ocm and ' or ' in ocm:
    #    ocm = ocm.replace(' or ', ' ')
    if ' (or ' in ocm:
        ocm = ocm.replace(' (or ', ' ')
        ocm = ocm.replace(')','')
    if ' or ' in ocm:
        ocm = ocm.replace(' or ', ' ')
    if ' (etc.)' in ocm:
        ocm = ocm.replace(' (etc.)','')
    if ' < ' in ocm:
        ocm = ocm.replace(' < ',' ')
    if ' (< ' in ocm:
        ocm = ocm.replace(' (< ', ' ')
    if ' >) ' in ocm:
        ocm = ocm.replace(' >) ', ' ')
        ocm = ocm.replace('(','')
    if ' > ' in ocm:
        ocm = ocm.replace(' > ', ' ')
    if ',' in ocm:
        ocm = ocm.replace(',', ' ')
    if '(prob. ' in ocm:
        ocm = ocm.replace('(prob. ', '')
        ocm = ocm.replace(')','')
    if '(i.e. ' in ocm:
        ocm = ocm.replace('(i.e. ', '')
        ocm = ocm.replace(')', '')
    if ' (= ' in ocm:
        ocm = ocm.replace(' (= ',' ')
        ocm = ocm.replace(')','')
    if '瞑' in ocm:
        x = 1
    if ' (瞑)' in ocm:
        ocm = ocm.replace(' (瞑)', '')
        #handle_x_slash_y((Ɂ/h))
    ocm = handle_short_parens(ocm)
    return ocm

def cleanup_late_han_ipa(lh_ipa):
    if 'or' in lh_ipa:
        if ' or ' in lh_ipa:
            lh_ipa = lh_ipa.replace(' or ', ' ')
        if 'or ' == lh_ipa[0:2+1]:
            lh_ipa = lh_ipa[2+1:len(lh_ipa)]
        if ' or' == lh_ipa[len(lh_ipa) - 3:len(lh_ipa)]:
            lh_ipa = lh_ipa[0:len(lh_ipa) - 3]
    if '?' in lh_ipa:
        lh_ipa = lh_ipa.replace('?', '')
    if ' ~ ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' ~ ', ' ')  # just treat each one as a possibility
    if ',' in lh_ipa:
        lh_ipa = lh_ipa.replace(',', ' ')
    if ' < ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' < ', ' ')  # just treat each one as a possibility
    if ' (> ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' (> ', ' ')
        lh_ipa = lh_ipa.replace(')', '')
        lh_ipa = lh_ipa.replace('  ', '')
    if ' > ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' > ', ' ')  # just treat each one as a possibility
    if '> ' in lh_ipa:
        if '> ' == lh_ipa[0:2]:
            lh_ipa = lh_ipa[2:len(lh_ipa)]
    if ' ?' in lh_ipa:
        lh_ipa = lh_ipa.replace(' ?', '')
    if ' (' in lh_ipa:
        lh_ipa = lh_ipa.replace(' (', ' ')
        lh_ipa = lh_ipa.replace(')', '')
    if ' MHan' in lh_ipa:
        lh_ipa = lh_ipa.replace(' MHan', '')
    if '/S ' in lh_ipa:
        lh_ipa = lh_ipa.replace('/S ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
    if 'S ' in lh_ipa:
        lh_ipa = lh_ipa.replace('S ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
    lh_ipa = remove_dupes(lh_ipa)
    # piaŋᴮ/ᶜ
    if 'ᴮ/ᶜ' in lh_ipa:
        lh_ipa = handle_b_slash_c(lh_ipa)
    if 'ᴬ/ᶜ' in lh_ipa:
        lh_ipa = handle_a_slash_c(lh_ipa)
    if '(ᶜ)' in lh_ipa:  # need one for (ᴮ) as well
        lh_ipa = handle_paren_c(lh_ipa)
    if '(ᴮ)' in lh_ipa:
        lh_ipa = handle_paren_b(lh_ipa)
    if '(Ɂ)' in lh_ipa:
        lh_ipa = handle_paren_x(lh_ipa, '(Ɂ)')
    if '(h)' in lh_ipa:
        lh_ipa = handle_paren_x(lh_ipa, '(h)')
    if '/' in lh_ipa:
        x = 1
        lh_ipa = lh_ipa.replace(' / ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
        if '/ ' == lh_ipa[0:2]:
            lh_ipa = lh_ipa[2:len(lh_ipa)]
        if '/ ' == lh_ipa[len(lh_ipa) - 2:len(lh_ipa)] or ' /' == lh_ipa[len(lh_ipa) - 2:len(lh_ipa)]:
            lh_ipa = lh_ipa[0:len(lh_ipa) - 2]
    return lh_ipa

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

# ASSUMPTIONS:
#   - (if no 「，」) rhyme words appear before 「。」
#   - (if both 「，」、「。」) rhyme words appear before 「，」、「。」
def get_rhyme_words_for_kmss2015_mirror_inscription(unique_id, inscription, use_unpunctuated=False):
    funct_name = 'get_rhyme_words_for_kmss2015_mirror_inscription()'
    punct_list = ['。', '，']
    retval = []
    if use_unpunctuated and '，' not in inscription and '。' not in inscription: # handle unpunctuated case
        return retval
    elif '，' in inscription: # handle ...，...，...。 case
        if inscription.count('。') > 1:
            print(funct_name + ' UNUSUAL situation. ' + unique_id + ' has both 「，」、「。」 AND ')
            print('\tmore than one 「。」')
            return retval
        inscription = inscription.replace('。', '')
        inscription = inscription.split('，')
        for i in inscription:
            last_char = grab_last_character_in_line(i)
            if '・' in last_char or '…' in last_char or '□' in last_char:
                continue
            if last_char not in retval:
                retval.append(last_char)
    elif '。' in inscription: # handle ...。...。...。 case
        inscription = inscription.split('。')
        for i in inscription:
            last_char = grab_last_character_in_line(i)
            if '・' in last_char or '…' in last_char or '□' in last_char:
                continue
            if last_char not in retval:
                retval.append(last_char)
    if len(retval) == 1:
        retval = [] # can't have just one rhyme word
    return retval


def process_kyomeishusei2015_han_mirror_data():
    funct_name = 'process_kyomeishusei2015_han_mirror_data()'
    id2inscription = readin_kyomeishusei2015_han_mirror_data()
    no_punct = []
    w_punct = []
    im = Infomap("--two-level --directed")
    rhyme_net = rnetwork()
    for id in id2inscription:
        #print(id + ': ' + '\n'.join(id2inscription[id]))
        #if len(id2inscription[id]) != 1:
        #    print('len: ' + str(len(id2inscription[id])))
        #    if 0 and len(id2inscription[id]) > 2 and len(id2inscription[id]) < 502:
        #        print('*'*100)
        for l in id2inscription[id]:
            rw_words = get_rhyme_words_for_kmss2015_mirror_inscription(id, l, use_unpunctuated=False)
            rhymes = ','.join(rw_words)
            rhymes = rhymes[0:len(rhymes)-1]
            print(id + ': ' + '\n'.join(id2inscription[id]) + ', RHYME WORDS: ' + rhymes)
            if rw_words: # if there are any rhyme words...
                #
                # add Nodes
                for rhyme_word in rw_words:
                    rhyme_net.add_node(rhyme_word, '1', '\n'.join(id2inscription[id]))
                    weight = rhyme_net.get_node_weight(rhyme_word)
                #
                # add Edges
                for left_inc in range(0, len(rw_words), 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, len(rw_words), 1):
                        rhyme_num = id
                        msg += id + ': '
                        msg += rw_words[left_inc] + ':' + rw_words[right_inc] + ', num_rhymes_same_type = '
                        msg += str(len(rw_words)) + ', poem_stanza_num = ' + rhyme_num
                        #if print_debug_msg:
                        #print(msg) # debug only
                        msg = ''
                        rhyme_net.add_edge(rw_words[left_inc], rw_words[right_inc], len(rw_words), rhyme_num)
                        #im.add_link(rw_list[left_inc], rw_list[right_inc])
                        edge_weight = rhyme_net.get_edge_weight(rw_words[left_inc], rw_words[right_inc])
    nodes_n_edges = rhyme_net.print_all_nodes_n_edges(is_verbose=False)
    #for e in nodes_n_edges:
    #    print(e)
    rhyme_net.get_infomap_linked_list_of_rhyme_network()



def readin_kyomeishusei2015_han_mirror_data():
    funct_name = 'readin_kyomeishusei2015_han_mirror_data()'
    base_dir = os.path.join(get_mirrors_dir(), 'raw', 'txt')
    # note: the data file is 03
    input_file = os.path.join(base_dir, 'kyomeishusei2015_03.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid file: ' + input_file)
        return []
    line_list = readlines_of_utf8_file_for_mirror_data(input_file)
    start_tag = '《漢三國西晉鏡銘集成 00001》'
    start_looking = False
    unique_id = ''
    id2inscription = {}
    current_id = ''
    for ll in line_list:
        if ll.strip().isdigit():
            continue # ignore page numbers
        #print(ll)
        ll = ll.strip()
        if start_tag in ll:
            start_looking = True
        if start_looking:

           #x = '《漢三國西晉鏡銘集成 '
            if '《漢三國西晉鏡銘集成 ' in ll:
                ll = ll.split('》')
                unique_id = ll[0].replace('《漢三國西晉鏡銘集成 ', 'kyomeishusei2015_')
                if '1499' in unique_id:
                    x = 1
                #print('unique_id = \'' + unique_id + '\'')
                #print('data source = \'' + ll[1] + '\'' )
            elif '《Ⅱ漢三國西晉鏡銘集成 ' in ll:
                ll = ll.split('》')
                unique_id = ll[0].replace('《Ⅱ漢三國西晉鏡銘集成 ', 'kyomeishusei2015_')
            elif ll and '〔' == ll[0]:
                inscription_name = ll.split('〕[')[0] + '〕'
                try:
                    name_in_source = '[' + ll.split('〕[')[1].split('］')[0] + '］'
                except IndexError as ie:
                    #print(unique_id + ' has some irregularities. Skipping.')
                    #continue
                    x = 1
                #print('inscrption name = ' + inscription_name + ', name in source = ' + name_in_source)
            elif ll and '◎' in ll:
                orig_ll = ll
                if '06133' in unique_id:
                    x = 1
                try:
                    inscription = ll.split('◎')[1].strip()
                    inscription = inscription.split('（')[0]  # get rid of commentary like （註）異體字銘帶 鏡Ⅱ式では「精」につくり，
                except IndexError as ie:
                    x = 1
                inscription = remove_num_from_end_of_str_if_there_is_one(inscription)
                if unique_id not in id2inscription:
                    id2inscription[unique_id] = []
                id2inscription[unique_id].append(inscription)

                #print('inscription = ' + inscription)
                if 0 and inscription.count('。') == 5:
                    print(unique_id + ' (' + str(inscription.count('。')) + ')' + add_late_han_before_each_period(inscription))
    return id2inscription

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

#get_schuessler_late_han_for_glyph(glyph)
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
    #print('input = ' + zh_num)
    #for inc in range(len(zh_num)-1, -1, -1):
    for inc in range(0, len(zh_num), 1):
        #print(str(inc) + ' : ' + zh_num[inc])
        retval += str(zh2ara_dict[zh_num[inc]])
    #retval = int(retval)
    retval = f"{int(retval):{num_digits}}"
    #print(retval)
    #f"{num_poems:03}"
    #print(retval)
    return retval

def readin_mao_2008_stelae_data():
    funct_name = 'readin_mao_2008_stelae_data()'
    base_dir = os.path.join(get_stelae_dir(), 'raw', 'txt')
    input_file1 = os.path.join(base_dir, '毛遠明 《漢魏六朝碑刻校注》第一冊.txt')
    input_file2 = os.path.join(base_dir, '毛遠明 《漢魏六朝碑刻校注》第二冊.txt')
    base_num_list = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if not os.path.isfile(input_file1):
        print(funct_name + ' ERROR: Invalid file: ' + input_file1)
        return []
    if not os.path.isfile(input_file2):
        print(funct_name + ' ERROR: Invalid file: ' + input_file2)
        return []
    line_list1 = readlines_of_utf8_file(input_file1)
    line_list2 = readlines_of_utf8_file(input_file2)
    line_list = line_list1 + line_list2
    mou_unique = ''
    delim = '\t'
    start_new_poem = False
    poem_content = []
    #last_line = line_list[len(line_list)-1]
    pos = -1
    line_list_len = len(line_list)
    for ll in line_list:
        if '二四〇' in ll:
            x = 1
        pos += 1
        #if pos == line_list_len-1:
        #    x = 1
        if '：' in ll:
            ll = ll.split('：')
            # if the beginning of a poem section
            if any(zh_num in ll[0] for zh_num in base_num_list):
                # if previous poem exists, print it
                if poem_content:
                    for l in poem_content:
                        print(l)
                    #print('')
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
                        x = 1
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
                        #continue
                    if '（' in date_data:
                        date_data = date_data.split('（')
                        zh_date_year = date_data[0]
                        western_year = date_data[1].split('）')[0]
                        zh_date_month = date_data[1].split('）')[1]
                ara_num = convert_zh_num2ara_num(zh_num)
                #print(zh_num + ':' + ara_num)
                mou_unique = 'Mou2008.' + ara_num
                #print(mou_unique)
                msg = mou_unique + delim + zh_num + '：' + stele_name + '，' + zh_date_year + '（' + western_year
                msg += '）' + zh_date_month
                if page_num:
                    msg += '，' + page_num
                print(msg)
                start_new_poem = False
            else:
                poem_content.append('：'.join(ll))
        else:
            if '守□不歇，比性乾坤' in ll:
                x = 1
            if ll:
                poem_content.append(ll)
            else:
                if ll == '':
                    if poem_content and poem_content[len(poem_content)-1] != '': # don't add two empty lines in a row
                        poem_content.append(ll)
    # print out last poem
    for l in poem_content:
        print(l)
                #print(ll[0])
def test_get_schuessler_late_han_for_glyph(glyph_list):
    for glyph in glyph_list:
        retval = get_schuessler_late_han_for_glyph(glyph)
        print(glyph + ': ' + retval)

#cydifflib_test()
#test_get_the_intersection_of_two_lists()
#test_get_the_difference_of_two_lists()
#compare_poem_names_between_lu_1983_and_raw_han_csv()
#test_trad_to_simp_conversion_and_vice_verse()
#sinopy_test()
#readin_bronze_type_dict()
#get_schuessler_late_han_data()
#test_rolling_n_lines()

#readin_kyomeishusei2015_han_mirror_data()

#readin_mao_2008_stelae_data()
#test_schuessler_phonological_data()

#test_distance_between_tags()
#test_handle_short_parens()

#naively_annotate_han_dynasty_poems()
process_kyomeishusei2015_han_mirror_data()

#test_visualize_infomap_output()
#explore_rhyme_structure_of_han_dynasty_poems()

#test_get_schuessler_late_han_for_glyph(['貴','富'])#['光','明'])#['里','海','何'])#['門','山'])

#clean_up_mou_n_zhong_2016_data() # bronzes
#print_lu1983_dict()
#readin_lu_1983_data()

#parse_han_data_from_lu_1983() #------

#get_list_of_author_names_from_lu_1983()

#readin_raw_han_poetry()
#test_get_arabic_num_given_chinese_num()
#test_chinese_converter()