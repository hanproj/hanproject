#! C:\Python36\
# -*- encoding: utf-8 -*-
#
import os
import codecs

#from py3_outlier_utils import readlines_of_utf8_file
#from py3_outlier_utils import get_data_from_pos
#from py3_outlier_utils import readlines_of_utf8_file
#from py3_outlier_utils import append_line_to_utf8_file

from anytree import Node, RenderTree, PreOrderIter, AsciiStyle
from soas_utils import rhyme_marker
from soas_utils import parse_schuessler_lhan_syllable
from soas_utils import get_phonological_data_dir
from soas_imported_from_py3 import readin_char2gsr_data
from soas_imported_from_py3 import is_compatibility_char
from soas_imported_from_py3 import readin_gsr2gsc_num_data
from soas_imported_from_py3 import convert_gsr2gsc_number
from soas_imported_from_py3 import readin_kcompatibility_variant_data_into_dict
from soas_imported_from_py3 import get_normal_char_given_compatibility_char
from soas_imported_from_py3 import is_compatibility_char
from soas_imported_from_py3 import get_gsr_number
from soas_imported_from_py3 import convert_local_variant2normal_char
from soas_imported_from_py3 import local_var2normal_char_dict
from soas_imported_from_py3 import get_user_msg_given_gsr_n_gsc_numbers
from soas_imported_from_py3 import readin_guangyun_data
from soas_imported_from_py3 import get_guangyun_data_for_char
from soas_imported_from_py3 import get_gsc_number

utf8_bom_b = b'\xef\xbb\xbf'

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

def get_hanproj_dir():
    return os.path.join(get_soas_code_dir(), 'hanproj')

def get_data_from_pos(string, position, delim):
    return string.split(delim, position+1)[int(position)]

def is_unicode(text):
    retval = False
    if 'str' in str(type(text)):
        retval = True
    return retval

def if_not_unicode_make_it_unicode(my_str):
    funct_name = 'if_not_unicode_make_it_unicode()'
    if not is_unicode(my_str):
        my_str = my_str.decode('utf8')
    return my_str

def safe_open_utf8_file_for_appending(filename):
    filename = if_not_unicode_make_it_unicode(filename)
    p, f = os.path.split(filename)
    if p and not os.path.isdir(p): # if the directory doesn't exist, create it
        os.makedirs(p)
    return codecs.open(filename, 'a', 'utf8')

def append_line_to_utf8_file(filename, content):
    funct_name = 'append_line_to_utf8_file()'
    output_ptr = safe_open_utf8_file_for_appending(filename)
    output_ptr.write(content + '\n')
    if output_ptr:
        output_ptr.close()

#def
def readlines_of_utf8_file(filename):
    funct_name = 'readlines_of_utf8_file()'
    retval = []
    if not os.path.isfile(filename):
        return retval
    with open(filename, 'rb') as f:
        line_list = f.readlines()
    line_list[0].replace(utf8_bom_b, b'')
    for line in line_list:
        line = line.decode('utf8')
        line = line.replace('\r\n', '')
        line = line.replace('\n', '')
        retval.append(line)
    return retval

def create_single_file_for_downloaded_ocr_data():
    funct_name = 'create_single_file_for_downloaded_ocr_data()'
    #D:\Ash\SOAS\data\先秦漢魏晉南北朝詩
    base_dir = os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'data', '先秦漢魏晉南北朝詩')
    base_filename = os.path.join(base_dir, 'raw-p')
    ext = '.txt'
    output_file = os.path.join(base_dir, '先秦漢魏晉南北朝詩-unified.txt')
    lines2ignore = ['Copyright © 2017 INCASEDO All rights reserved.',
                    '联系我们 | 隐私条款 | 如果智培',
                    '京ICP备17041772号-1',
                    'D:\Ash\SOAS\data\先秦漢魏晉南北朝詩']
    if os.path.isfile(output_file):
        print(funct_name + ': WARNING: Output file already exists! Deleting...')
        os.remove(output_file)
        print('\tDone!')

    for finc in range(1,61+1, 1):
        local_file = base_filename + str(finc) + ext
        #print(local_file)
        if not os.path.isfile(local_file):
            print('WARNING: No such file:')
            print('\tSkipping!')
            continue
        else:
            line_list = readlines_of_utf8_file(local_file)
            #print(u'\n'.join(line_list))
            trip_wire = '61頁'
            tripped = False
            num_empty_lines_in_a_row = 0
            for ll in line_list:
                if trip_wire in ll:
                    tripped = True
                elif tripped:
                    if not ll.strip():
                        if num_empty_lines_in_a_row == 0:
                            print(ll)
                            append_line_to_utf8_file(output_file, ll)
                            num_empty_lines_in_a_row += 1
                    else:
                        num_empty_lines_in_a_row = 0
                        if ll not in lines2ignore:
                            print(ll)
                            append_line_to_utf8_file(output_file, ll)
    # TO DO:
    # - create data structure for a single rhyme
def get_soas_data_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'data')

def readin_baxter1992_rhyme_data():
    funct_name = 'readin_baxter1992_rhyme_data()'
    data_file = os.path.join(get_soas_data_dir(), 'Baxter1992.tsv')
    if not os.path.isfile(data_file):
        print(funct_name + u' ERROR: input file: ' + data_file)
        print('\tDoes NOT exist!')
        return []
    data = readlines_of_utf8_file(data_file)
    return data


# NOTE: the max number of rhyme groups in any poem is 'i' (9)
def create_network_for_baxter1992_data():
    funct_name = 'create_network_for_baxter1992_data()'
    data = readin_baxter1992_rhyme_data()
    data = data[1:len(data)] # get rid of labels
    line_num_pos = 4
    line_pos = 6
    rhyme_word_pos = 9
    rhyme_num_pos = 8
    prev_stanza_num = -1
    prev_poem_num = 0
    stanza_dict = {}
    line_pairs_dict = {}
    for d in data: # d - one line of data: 7492	303	玄鳥	303.1	9	商之先后	商 + 之 + 先 + 后	商 + 之 + 先 + 后		后	0 0 0 0
        #print(d)

        d = d.split('\t')
        rhyme_word = d[rhyme_word_pos]
        rhyme_num = d[rhyme_num_pos]
        line = d[line_pos].replace(' + ', '')
        #print('RHYME_NUM = ' + rhyme_num)
        rnum = rhyme_num.split('.')
        line_num = d[line_num_pos]
        poem_num = rnum[0]
        try:
            stanza_num = rnum[1]
        except IndexError as ie:
            continue
        rhyme_type = rnum[2]
        poem_name = get_poem_name_given_number(poem_num)
        msg = '(' + poem_num + ') ' + poem_name + ', rhyme_word = ' + rhyme_word + ', rhyme num = ' + rhyme_num
        msg += ', stanza num = ' + stanza_num + ', rhyme type = ' + rhyme_type + ', line = ' + line + ', line # = ' + line_num
        #print(msg) # just testing to see if the indices are correct
        # the stanza_dict - is a dictionary of all lines within the current stanza
        if prev_stanza_num == -1:
            prev_stanza_num = stanza_num
        if '琴瑟友之' in line:
            x = 1
        #print('len(stanza_dict) = ' + str(len(stanza_dict)))
        if stanza_dict and prev_stanza_num != stanza_num: # process stanza dict data before moving to the next stanza
            if 0: # printout stanza_dicts
                for l in stanza_dict:
                    print(stanza_dict[l])
                print('-'*40)
            # note that only rhyming lines are in the stanza_dict
            prev_stanza_num = stanza_num
            max_ind = max(k for k, v in stanza_dict.items())
            prev_line = ''
            for linc in range(1, int(max_ind)+1, 1): # for each line in the stanza
                x = 1 # do stuff - line_pairs_dict
                try:
                    current_line = stanza_dict[str(linc)] # grab the current line
                    if '左右采之' in current_line:
                        x = 1
                except KeyError as ke:
                    continue # since some lines do not contain rhymes, and the stanza_dict only collects rhyming lines,
                             # then skip lines that do not rhyme
                if not prev_line:
                    prev_line = current_line
                    continue
                if prev_line[0] == current_line[0]: # if the prev line and current line have the same rhyme types (a, b, etc.)
                    if prev_line[1] not in line_pairs_dict:
                        line_pairs_dict[prev_line[1]] = []
                    if int(poem_num) - prev_poem_num > 1:
                        pn = int(poem_num) - 1
                    else:
                        pn = int(poem_num)
                    line_pairs_dict[prev_line[1]].append((str(pn), current_line[1]))
                    #msg2 = 'prev_line[1] = ' + prev_line[1] + ', poem_num = ' + poem_num + ', prev_pn = ' + str(prev_poem_num)
                    msg2 = 'prev_line[1] = ' + prev_line[1] + ', pn = ' + str(pn)
                    msg2 += ', current_line[1] = ' + current_line[1]
                    #print(msg2)
                    prev_line = current_line
                else:
                    # check if any lines AFTER the previous line are rhymes (with the previous line)
                    # NOTE: if there are, it's the first line of the same type after the previous line
                    for inner_inc in range(linc, int(max_ind)+1, 1):
                        try:
                            inner_line = stanza_dict[str(inner_inc)]
                        except KeyError as ke:
                            continue
                        if prev_line[0] == inner_line[0]:
                            if prev_line[1] not in line_pairs_dict:
                                line_pairs_dict[prev_line[1]] = []
                            if int(poem_num) - prev_poem_num > 1:
                                pn = int(poem_num) - 1
                            else:
                                pn = int(poem_num)
                            line_pairs_dict[prev_line[1]].append((str(pn), inner_line[1]))# inner_line[1]
                            prev_line = current_line
                            break
            stanza_dict.clear() # reset for next stanza
            stanza_dict[line_num] = (rhyme_type, line)
        else: # add stanza data to dictionary
            stanza_dict[line_num] = (rhyme_type, line)
        if int(poem_num) - prev_poem_num > 1:
            prev_poem_num = int(poem_num) - 1

    if line_pairs_dict:
        for k in line_pairs_dict:
            for tup in line_pairs_dict[k]:
                print(k + ' -> ' + ':'.join(tup))
            #print(k + ' -> ' + ':'.join(line_pairs_dict[k]))

def create_network_for_baxter1992_data_2():
    funct_name = 'create_network_for_baxter1992_data_2()'
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
    test_stanza_list = ['39.1']#, '54.4']
    for d in data: # d - one line of data: 7492	303	玄鳥	303.1	9	商之先后	商 + 之 + 先 + 后	商 + 之 + 先 + 后		后	0 0 0 0
        #print(d)

        d = d.split('\t')
        print(str(len(d)))
        rhyme_word = d[rhyme_word_pos]
        rhyme_num = d[rhyme_num_pos]
        #any(substring in string for substring in substring_list)
        #if not any(stanza in rhyme_num for stanza in test_stanza_list):
        #    continue
        line_w_type = d[line_w_type_pos]
        line = d[line_pos].replace(' + ', '')
        if '武王' in line and '304' in rhyme_num:
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
        poem_name = get_poem_name_given_number(poem_num)
        msg = '(' + poem_num + ') ' + poem_name + ', rhyme_word = ' + rhyme_word + ', rhyme num = ' + rhyme_num
        msg += ', stanza num = ' + stanza_num + ', rhyme type = ' + rhyme_type + ', line = ' + line + ', line # = ' + line_num
        msg += ', line_w_type = ' + line_w_type
        rtype = get_rhyme_type_if_it_is_there(line_w_type)
        if rtype:
            if line_w_type.count(rtype) > 1:
                if line_w_type not in multi_list:
                    multi_list.append(line_w_type)
        #print(msg) # just testing to see if the indices are correct
        # the stanza_dict - is a dictionary of all lines within the current stanza
        if prev_stanza_num == -1:
            prev_stanza_num = stanza_num

        if prev_stanza_num == stanza_num and prev_poem_num == poem_num: # NOT entering new stanza NOR entering new poem
            if is_line_a_rhyming_line(line_w_type):
                x = 1  # add data to stanza dict
                if rhyme_type not in stanza_dict:
                    stanza_dict[rhyme_type] = []
                stanza_dict[rhyme_type].append((line_num, line, rhyme_word, rhyme_num))
                #print(line_w_type + ' IS a rhyming line!')
            else:
                #print(line_w_type + ' is NOT a rhyming line!')
                continue # skip line that does NOT rhyme
        else:
            #
            # TO DO (2022-03-19):
            #  - problem:
            #       The stanza dict is not getting processed for the last stanza of the last poem
            #
            x = 1 # process stanza dict data (i.e., add to line_pairs_dict)
            print('\nProcessing Stanza dict:')
            #last_key = list(stanza_dict)[-1]
            #
            # TO DO: (as of 2022-03-17)
            #
            # - In the 'for e in stanza_dict[k]:' for loop
            #   add in support such that the line_pairs_dict gets filled in
            #   use the 'last_sd_element' to know when to stop
            #   i.e., e_1 -> e_2; e_2 -> e_3; e_3 -> e_4 and stop when you hit the last element
            #sd_line_num_pos = 0
            #sd_line_pos = 1
            #sd_rhyme_word_pos = 2
            #sd_rhyme_num_pos = 3
            for k in stanza_dict:
                msg2p = 'stanza_dict[' + k + '] = ('#(' + ','.join(stanza_dict[k]) + ')')
                for e in stanza_dict[k]:
                    msg2p += '(' + ','.join(e) + '); '
                msg2p = msg2p[0:len(msg2p)-2] + ')'
                print(msg2p)
            for k in stanza_dict: # k = rhyme type (like 'a', 'b', etc.) - per rhyme type in the stanza
                print(k)
                G_ab = len(stanza_dict[k]) # the number of rhymes of the current type within this stanza
                                           # (one of Mattis' definitions for 'rhyme group')
                try:
                    last_sd_element = stanza_dict[k][-1]
                except IndexError as ie:
                    x = 1
                s_rhyme_group = []
                for inc in range(0, len(stanza_dict[k]), 1): # go through each stanza line for this rhyme type --
                    # i.e., per stanza line for a given rhyme type
                    #if 0: # for debug only
                    #    try:
                    #        print('stanza_dict[k][inc][sd_rhyme_word_pos] = ' + stanza_dict[k][inc][sd_rhyme_word_pos])
                    #        print('stanza_dict[k][inc][sd_rhyme_num_pos] = ' + stanza_dict[k][inc][sd_rhyme_num_pos])
                    #    except IndexError as ie:
                    #        x = 1
                    #
                    # NOTE: in add_node():
                    #       if the node doesn't already exist, it's created
                    #       if the node DOES exist, then this occurrence is added to its list of occurrences
                    #       (assuming it's not already there. If it is, it's not counted twice)
                    #rhyme_net.add_node(zi, poem_stanza_num=)
                    rhyme_net.add_node(stanza_dict[k][inc][sd_rhyme_word_pos], stanza_dict[k][inc][sd_rhyme_num_pos])
                    s_rhyme_group.append(stanza_dict[k][inc][sd_rhyme_word_pos])
                    #rhyme_net.add_edge()
                    #
                    # deal with pairs of rhyming lines and edges
                    # -- need edge between each pair of rhyming words in stanza (for same rhyme type)
                    if inc < len(stanza_dict[k])-1: # stanza_dict[k] tup: (line_num, line, rhyme_word, rhyme_num)
                        first_rhyming_line = stanza_dict[k][inc][1]
                        sec_rhyming_line = stanza_dict[k][inc + 1][1]
                        print(str(inc) + ': ' + first_rhyming_line + ' -> ' + sec_rhyming_line)
                        rhyme_pairs.add_pair_of_rhyming_lines(first_rhyming_line, sec_rhyming_line)
                        srhyme_num = stanza_dict[k][inc][3]
                        print('first_rhyming_line = ' + first_rhyming_line + ', rhyme_num = ' + srhyme_num)

                s_rhyme_group  = list(set(s_rhyme_group))#nodes2make_edges = ['仔', '仕', '以', '伺', '似', '你']
                num_lines_same_type = len(s_rhyme_group)
                for left_inc in range(0, num_lines_same_type, 1):
                    msg = '-'*40 + '\n'
                    for right_inc in range(left_inc + 1, num_lines_same_type, 1):
                        x = 1
                        msg += s_rhyme_group[left_inc] + ':' + s_rhyme_group[right_inc] + ', num_lines_same_type = '
                        msg += str(num_lines_same_type) + ', poem_stanza_num = ' + rhyme_num + '\n'
                    #print(msg)
                        rhyme_net.add_edge(s_rhyme_group[left_inc], s_rhyme_group[right_inc], num_lines_same_type, rhyme_num)
                        #msg += nodes2make_edges[left_inc] + '-' + nodes2make_edges[right_inc] + ', '

                print('')

                #for e in stanza_dict[k]:
                #    print('\t' + str(e[0]) + ':' + e[1])
            stanza_dict = {} # reset dict for next stanza
            #
            # Process the current line (which is in a different stanza and/or poem as the stanza dict data just processed
            prev_stanza_num = stanza_num
            prev_poem_num = poem_num
            if is_line_a_rhyming_line(line_w_type):# add data to stanza dict
                if rhyme_type not in stanza_dict:
                    stanza_dict[rhyme_type] = []
                stanza_dict[rhyme_type].append((line_num, line, rhyme_word, rhyme_num))
                #print(k + '\n\t'.join(stanza_dict[k]))

    rhyme_pairs.print_out_rhyming_pairs_plus_num_occurrences(2)
    rhyme_pairs.print_out_unique_rhyming_pairs()
    rhyme_net.print_num_nodes()
    rhyme_net.print_num_edges()
    rhyme_net.print_all_edges()

    if 0:
        if line_pairs_dict:
            for k in line_pairs_dict:
                for tup in line_pairs_dict[k]:
                    print(k + ' -> ' + ':'.join(tup))
                #print(k + ' -> ' + ':'.join(line_pairs_dict[k]))
        if multi_list:
            print('Lines with multiple rhymes:')
            for ml in multi_list:
                print(ml)
            print('There were ' + str(len(multi_list)) + ' lines with multiple rhymes.')

def anytree_test():
    funct_name = 'anytree_test()'
    print(funct_name + ' Welcome!')

    udo = Node("Udo")
    marc = Node("Marc", parent=udo)
    lian = Node("Lian", parent=marc)
    dan = Node("Dan", parent=udo)
    jet = Node("Jet", parent=dan)
    jan = Node("Jan", parent=dan)
    joe = Node("Joe", parent=dan)

    print(udo)
    #Node('/Udo')
    print(joe)
    #Node('/Udo/Dan/Joe')

    for pre, fill, node in RenderTree(udo):
        print("%s%s" % (pre, node.name))

    # the list produces all possible paths from the root node 'udo'
    print(list(PreOrderIter(udo, filter_=lambda node: node.is_leaf)))
    # also prints out a tree
    #print(RenderTree(udo, style=AsciiStyle()).by_attr())

#anytree_test()
def find_path_optimized_for_rhyme(path_list):
    funct_name = 'find_path_optimized_for_rhyme()'
    rmarker = rhyme_marker()
    #parse_schuessler_lhan_syllable()
    path2data_dict = {}
    pinc = 0
    for pad in path_list:
        if pinc not in path2data_dict:
            path2data_dict[pinc] = {}

        for lhan in pad:
            initial, medial, rhyme, pcoda = parse_schuessler_lhan_syllable(lhan)
            #mark = rmarker.get_marker(rhyme)
            if rhyme not in path2data_dict[pinc]:
                path2data_dict[pinc][rhyme] = 0
            path2data_dict[pinc][rhyme] += 1
        pinc += 1
    pinc2min_singles = {}
    for k1 in path2data_dict:
        if k1 not in pinc2min_singles:
            pinc2min_singles[k1] = 0
        for k2 in path2data_dict[k1]:
            print('[' + str(k1) + '][' + k2 + '] = ' + str(path2data_dict[k1][k2]))
            if path2data_dict[k1][k2] == 1:
                pinc2min_singles[k1] += 1
    min_singles = 10000
    min_inc = -1
    for pinc in pinc2min_singles:
        if pinc2min_singles[pinc] <= min_singles:
            min_singles = pinc2min_singles[pinc]
            min_inc = pinc
    print('MIN: min # singles: ' + str(min_singles) + ', inc = ' + str(min_inc))
    print('=> ' + ' '.join(path_list[min_inc]))

def test_create_tree():
    funct_name = ''
#    test_data_dict = {'清': 'tsʰieŋ', '名': 'mieŋ nenᶜ', '生': 'ṣɛŋ', '盈': 'jeŋ', '成': 'dźeŋ', '聽': 'tʰeŋ tʰeŋᶜ'}
    test_data_dict = {"清": "tsʰieŋ", "名": "mieŋ nenᶜ", "生": "ṣɛŋ", "盈": "jeŋ", "成": "dźeŋ", "聽": "tʰeŋ tʰeŋᶜ"}

    root_node = create_tree(test_data_dict)
    each_path = list(PreOrderIter(root_node, filter_=lambda node: node.is_leaf))
    #for p in each_path:
    #    print(p.path)
    test_list = [list(leaf.path) for leaf in PreOrderIter(root_node, filter_=lambda node: node.is_leaf)]
    pad_list = []
    for tl in test_list:
        p = str(tl[len(tl)-1])#.path
        #p = p.split('/')
        pad = retreive_path_from_nodes(p)
        #ap = allpaths(root_node)
        #print(tl)
        if pad not in pad_list:
            pad_list.append(pad)
        #print('|'.join(pad))
    for p in pad_list:
        print(p)
    find_path_optimized_for_rhyme(pad_list)



def retreive_path_from_nodes(node):
    node = node.split('/')
    node = node[2:len(node)]
    last_n = node.pop().replace(')','')
    last_n = last_n.replace('\'','')
    node.append(last_n)
    return node

def allpaths(start):
    skip = len(start.path) - 1
    return [leaf.path[skip:] for leaf in PreOrderIter(start, filter_=lambda node: node.is_leaf)]

def create_tree(test_data_dict):
    funct_name = 'create_tree()'
    root_node = Node("root")

    prev_parent = [root_node]
    total_nodes = []
    #total_nodes.append(root_node)
    for e in test_data_dict:
        fayin = test_data_dict[e]
        fayin = fayin.split(' ')
        fayin_nodes = []
        for fy in fayin:
            for pp in prev_parent:
                temp_node = Node(fy, parent=pp)
                #total_nodes.append(temp_node)
                fayin_nodes.append(temp_node)
        prev_parent = fayin_nodes[:]
    return root_node

if 0:
    char2gsr_num_dict = {}
    def readin_char2gsr_data():
        funct_name = 'readin_char2gsr_data()'
        global char2gsr_num_dict
        if char2gsr_num_dict:
            return
        input_file = os.path.join(get_phonological_data_dir(),'kGSR.txt')
        if not os.path.isfile(input_file):
            print(funct_name + ' ERROR: Invalid input file: ' + input_file)
            return
        data = readlines_of_utf8_file(input_file)
        for d in data:
            d = d.split('\t')
            if d[0] not in char2gsr_num_dict:
                char2gsr_num_dict[d[0]] = ''
            char2gsr_num_dict[d[0]] = d[1]

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

if 0:
    def get_gsc_number(tchar):
        gsr_num = get_gsr_number(tchar)
        retval = -1
        if gsr_num.strip():
            retval = convert_gsr2gsc_number(gsr_num)
        return retval

    def get_gsr_number(tchar):
        readin_char2gsr_data()
        if is_compatibility_char(tchar):
            tchar = get_normal_char_given_compatibility_char(tchar)
        tchar = convert_local_variant2normal_char(tchar) # does nothing if tchar isn't a variant
        retval = ''
        if tchar in char2gsr_num_dict:
            retval = char2gsr_num_dict[tchar]
        return retval

if 0:
    def is_compatibility_char(entry):
        readin_kcompatibility_variant_data_into_dict()
        retval = False
        if entry in compat2normal_dict:
            retval = True
        return retval

    def get_normal_char_given_compatibility_char(entry):
        funct_name = 'get_normal_char_given_compatibility_char()'
        readin_kcompatibility_variant_data_into_dict()
        retval = entry
        if entry in compat2normal_dict:
            retval = compat2normal_dict[entry]
        return retval

if 0:
    compat2normal_dict = {}
    # format: compat2normal_dict[compat_char] = normal_char
    def readin_kcompatibility_variant_data_into_dict():  # kCompatibilityVariant.txt
        funct_name = 'readin_kcompatibility_variant_data_into_dict()'
        global compat2normal_dict
        if compat2normal_dict:
            return compat2normal_dict
        #base_dir = os.path.join('C:' + os.sep + 'Ash', 'research', 'code', 'python', 'data')
        #get_hanproj_dir()
        filename = 'kCompatibilityVariant.txt'
        line_list = readlines_of_utf8_file(os.path.join(get_hanproj_dir(), 'hanproject', filename))
        delim = '\t'
        for l in line_list:
            compat_char = get_data_from_pos(l, 0, delim)
            normal_char = get_data_from_pos(l, 1, delim)
            normal_char = normal_char.replace('U+', u'')
            if len(normal_char) == 5:
                print(funct_name + ' cannot process ' + normal_char)
                print('\t' + ' Only 4 byte chars are currently supported.')
                continue
            normal_char = convert_2byte_ncr_to_unicode_char(normal_char)
            # print(u'compat: ' + compat_char + u', normal: ' + normal_char)
            if compat_char not in compat2normal_dict.keys():
                compat2normal_dict[compat_char] = ''
            compat2normal_dict[compat_char] = normal_char

def convert_2byte_ncr_to_unicode_char(mstr):
    funct_name = 'convert_2byte_ncr_to_unicode_char()'
    if len(mstr) != 4:
        print(funct_name + ' ERROR: expected sring of length 4, got length = ' + len(mstr) + ' (' + mstr + ')')
        return 0x0
    hob = convert_stringnum2hexnum(mstr[0])
    s_hob = convert_stringnum2hexnum(mstr[1])
    t_hob = convert_stringnum2hexnum(mstr[2])
    lob = convert_stringnum2hexnum(mstr[3])
    retval = (hob << 12)
    retval += (s_hob << 8)
    retval += (t_hob << 4)
    retval += lob
    return chr(retval)

def convert_4byte_ncr_to_unicode_char(mstr):
    funct_name = 'convert_4byte_ncr_to_unicode_char()'
    if len(mstr) > 5:
        print(funct_name + ' ERROR: expected string of length 5, got length = ' + str(len(mstr)) + ' (' + mstr + ')')
        return 0x0
    hob = convert_stringnum2hexnum(mstr[0])
    hob = hob - 0x1
    s_hob = convert_stringnum2hexnum(mstr[1])
    t_hob = convert_stringnum2hexnum(mstr[2])
    high10bits = (hob << 6)
    high10bits += (s_hob << 2)
    high10bits += (t_hob >> 2)
    low10bits = (t_hob << 8)
    f_hob = convert_stringnum2hexnum(mstr[3])
    lob = convert_stringnum2hexnum(mstr[4])
    low10bits += (f_hob << 4)
    low10bits += lob
    retval = get_unicode_char_from_high_and_low_10bits(high10bits, low10bits)#.decode('utf8')
    return retval

def get_unicode_char_from_high_and_low_10bits(high10bits, low10bits):
    high10bits += 0x40  # this is the  0x10000 mask that was subtracted out when creating the surrogates; here it  has been adjusted for it's position in the 10 highest bits and is being added back ni
    #		case 4:   //                         byte4  |  byte3  |  byte2  |  byte 1
    #				  //range#4, input:        0000 0000|000x xxxx|xxxx xxxx|xxxx xxxx
    #				  //range#4, result:       1111 0xxx|10xx xxxx|10xx xxxx|10xx xxxx
    #				  //range#4, byte3 mask:   0000 0000|0000 0011|1111 0000|0000 0000//111111000000000000=0x3F000
    #				  //range#4, byte4 mask:   0000 0000|0001 1100|0000 0000|0000 0000//111000000000000000000=0x1C0000
    #				  //range#4, byte3 header: 0000 0000|1000 0000|0000 0000|0000 0000//100000000000000000000000=0x800000
    #				  //range#4, byte4 header: 1111 0000|0000 0000|0000 0000|0000 0000//11110000000000000000000000000000=0xF0000000
    # //				  byte1  = code_point & lsb_mask; lsb_mask = 0x3F (= b11 1111)
    byte1 = low10bits & 0x3f  # grab least significant 6 bits from low surrogate
    byte1 += 0x80  # apply header (most significant 2 bits)
    # //				  byte2  = (code_point & b2_mask)<<2; b2_mask = 0xFC0 (=b1111 1100 0000)
    # byte 2:  a. grab least significant 2 bits from high10bits
    #               b. shift those 4 places to the left
    #               c. grab the most significant 4 bits from low10bits
    #               d. shift those 6 places to the right
    #               e. apply header: 0x80
    byte2 = ((high10bits & 0x3) << 4) | (low10bits >> 6) + 0x80
    # //				  byte3  = (code_point & r4_b3_mask)<<4;  r4_b3_mask = 0x3F000
    byte3 = ((high10bits & 0xfc) >> 2) + 0x80
    # //				  byte4  = (code_point & r4_msb_mask)<<6;//1000000000000000000000 ; r4_msb_mask  = 0x1C0000
    byte4 = (high10bits >> 8) + 0xf0
    # //				  byte1 |= lsb_header;  lsb_header = 0x80
    # //				  byte2 |= r4_byte2_header; r4_byte2_header = 0x8000
    # //				  byte3 |= r4_byte3_header;//UINT r4_byte3_header = 0x800000;
    # //				  byte4 |= r4_byte4_header; r4_byte4_header = 0xF0000000
    # //				  retval = byte4 | byte3 | byte2 | byte1;
    #    // 0x20000=(b)10|0000 0000|0000 0000=utf8: 1111 0000|1000 0010|1000 0000|1000 0000..../101000000000000000=0x28000
    #			//11110000100000101000000010000000=0xF0828080
    return ''.join([chr(byte4), chr(byte3), chr(byte2), chr(byte1)])

def test_convert_2byte_ncr_to_unicode_char():
    funct_name = 'test_convert_2byte_ncr_to_unicode_char()'
    print(funct_name + ' Welcome!')
    test_chars = ['4f60', '597d', '55ce']#[0x4f60, 0x597d, 0x55ce]
    for tc in test_chars:
        print(convert_2byte_ncr_to_unicode_char(tc))

str2hex_num_dict = {'0':0x0, '1':0x1, '2':0x2, '3':0x3, '4':0x4, '5':0x5, '6':0x6, '7':0x7, '8':0x8, '9':0x9,
                    'a':0xa, 'b':0xb, 'c':0xc, 'd':0xd, 'e':0xe, 'f':0xf}

# only works on single digits
def convert_stringnum2hexnum(str_num):
    return str2hex_num_dict[str_num.lower()]

def test_convert_4byte_ncr_to_unicode_char():
    funct_name = 'test_convert_4byte_ncr_to_unicode_char()'
    print(funct_name + ' Welcome!')
    #20000:	𠀀 	20001:	𠀁 	20002:	𠀂 	20003:	𠀃
    test_chars = ['20000']  # [0x4f60, 0x597d, 0x55ce]
    #convert_4byte_ncr_to_unicode_char
    for tc in test_chars:
        print(convert_4byte_ncr_to_unicode_char(tc))

def test_get_normal_char_given_compatibility_char():
    funct_name = 'test_get_normal_char_given_compatibility_char()'
    test_chars = ['悔', '視', '福', '祉', '祝', '虜', '穀', '勉', '海', '廉', '節', '者', '祥', '祐']
    for tc in test_chars:
        print(tc + ': ' + get_normal_char_given_compatibility_char(tc))

def readin_chars_missing_schuessler_data():
    funct_name = 'readin_chars_missing_schuessler_data()'
    input_file = os.path.join(get_phonological_data_dir(), 'chars_missing_schuessler_data.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file: ' + input_file)
        return []
    data = readlines_of_utf8_file(input_file)
    data = data[0]
    data = list(set(data))
    return data

def print_out_chars_missing_schuessler_data_to_gsc_num():
    funct_name = 'print_out_chars_missing_schuessler_data_to_gsc_num()'
    #chars_missing_s = readin_chars_missing_schuessler_data()
    readin_local_variants()
    chars_missing_s = local_var2normal_char_dict.keys()

    no_gsr_num = []
    for c in chars_missing_s:
        gsr_num = get_gsr_number(c)
        if not gsr_num.strip():
            no_gsr_num.append(c)
        gsr_num = gsr_num.split(' ')
        for gsr in gsr_num:
            gsc_num = convert_gsr2gsc_number(gsr)
            if gsr.strip():
                print(c + '\t' + gsc_num + '\t')
                #print(c + ': gsr=' + gsr + ', gsc=' + gsc_num)
    if no_gsr_num:
        print(str(len(no_gsr_num)) + ' entries are missing GSR numbers!')
        print('\t' + ''.join(no_gsr_num))

if 0:
    gsr2gsc_num_dict = {}
    def readin_gsr2gsc_num_data(is_verbose=False):
        funct_name = 'readin_gsr2gsc_num_data()'
        global gsr2gsc_num_dict
        if gsr2gsc_num_dict:
            return
        input_file = os.path.join(get_phonological_data_dir(), 'gsr2gsc_number.txt')
        if not os.path.isfile(input_file):
            print(funct_name + ' ERROR: Invalid input file: ' + input_file)
            return
        data = readlines_of_utf8_file(input_file)
        for d in data:
            d = d.split('\t')
            gsr_num = d[0]
            if gsr_num not in gsr2gsc_num_dict:
                gsr2gsc_num_dict[gsr_num] = ''
            gsr2gsc_num_dict[gsr_num] = d[1]
        if is_verbose:
            for k in gsr2gsc_num_dict:
                print(k + ': ' + gsr2gsc_num_dict[k])

# this doesn't work
def get_ordered_list_of_gsc_numbers_DEPRECATED():
    readin_gsr2gsc_num_data()
    raw_data = gsr2gsc_num_dict.values()
    unordered_data = []
    for rd in raw_data:
        rd = rd.split('; ')
        for e in rd:
            unordered_data.append(e)
    unordered_data = list(set(unordered_data))
    num2alpha_dict = {}
    num_data = []
    for ud in unordered_data:
        if 'A' in ud:
            ud = ud[0:len(ud)-1]
        ud = float(ud.replace('-', '.'))
        num_data.append(ud)
        #print(str(ud))
    num_data = list(set(num_data))
    num_data.sort()
    maj2minor_dict = {}
    for nd in num_data:
        k = str(nd).split('.')[0]
        v = str(nd).split('.')[1]
        if k not in maj2minor_dict:
            maj2minor_dict[k] = []
        maj2minor_dict[k].append(v)
    for k in maj2minor_dict:
        maj2minor_dict[k].sort()
        for inner_k in maj2minor_dict[k]:
            print(k + '.' + inner_k)

if 0:
    def convert_gsr2gsc_number(gsr_num):
        if not gsr_num.strip():
            return ''
        readin_gsr2gsc_num_data()
        if '0049q' in gsr_num:
            x = 1
        try:
            if gsr_num[len(gsr_num)-1] == '\'':
                gsr_num = gsr_num[0:len(gsr_num) - 1]
            if gsr_num[len(gsr_num)-1].isalpha():
                gsr_num = gsr_num[0:len(gsr_num) - 1]
        except IndexError as ie:
            x = 1
        gsr_num = str(int(gsr_num))
        gsc_num = gsr2gsc_num_dict[gsr_num]
        return gsc_num

def test_get_gsr_number():
    funct_name = 'test_get_gsr_number()'
    tchar_list = ['滋', '慎', '恩', '坤', '優', '熹', '祺', '苓']
    for c in tchar_list:
        gsr_num = get_gsr_number(c)
        gsc_num = convert_gsr2gsc_number(gsr_num)
        if gsr_num.strip():
           print(c + ': ' + gsr_num + ' -> ' + gsc_num)

def get_ordered_list_of_gsc_numbers():
    funct_name = 'get_ordered_list_of_gsc_numbers()'
    input_file = os.path.join(get_phonological_data_dir(), 'max_gsc_per_bu.txt')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: Invalid input file: ' + input_file)
        return []
    data = readlines_of_utf8_file(input_file)
    retval = []
    for d in data:
        maxval = int(d.split('-')[1])
        bu_num = d.split('-')[0]
        for inc in range(1, maxval+1, 1):
            retval.append(bu_num + '-' + str(inc))
    return retval

def get_list_of_chars_missing_sch_data_ordered_by_gsc_num():
    funct_name = 'get_list_of_chars_missing_sch_data_ordered_by_gsc_num()'
    chars_missing_s = readin_chars_missing_schuessler_data()
    gsc_number_list = get_ordered_list_of_gsc_numbers()
    #get_gsr_number()
    gsc2char_list_dict = {}
    output_file = os.path.join(get_phonological_data_dir(), 'missing_schuessler_char_list.txt')
    if os.path.isfile(output_file):
        os.remove(output_file)
    for mc in chars_missing_s:
        gsr_num = get_gsr_number(mc)
        if not gsr_num.strip():
            continue
        gsr_num = gsr_num.split(' ')
        for gsr in gsr_num:
            gsc_num = convert_gsr2gsc_number(gsr)
            gsc_num = gsc_num.split('; ')
            for gsc in gsc_num:
                gsc = gsc.replace('A', '')
                #print(mc + ':  ' + gsr + ' -> ' + gsc)
                if gsc not in gsc2char_list_dict:
                    gsc2char_list_dict[gsc] = []
                gsc2char_list_dict[gsc].append(mc)
    #for gld in gsc2char_list_dict:
    #    print(gld + ': ' + ''.join(gsc2char_list_dict[gld]))
    retval = {}
    for gsc in gsc_number_list:
        if gsc in gsc2char_list_dict:
            if gsc not in retval:
                retval[gsc] = []
            retval[gsc] = gsc2char_list_dict[gsc]
    for g in retval:
        for e in retval[g]:
            append_line_to_utf8_file(output_file, g + '\t' + e + '\t')
            print(g + ': ' + e)
        #print(g + ': ' + ''.join(retval[g]))
    #convert_gsr2gsc_number()

def delete_file_if_it_exists(filename):
    if os.path.isfile(filename):
        os.remove(filename)

def transform_missing_sch_file2_ordered_list():
    funct_name = 'transform_missing_sch_file2_ordered_list()'
    input_file = os.path.join(get_phonological_data_dir(), 'missing_schuessler_char_list.txt')
    output_file = os.path.join(get_phonological_data_dir(), 'missing_schuessler_char_list2.txt')
    if not if_file_exists(input_file, funct_name):
        return
    delete_file_if_it_exists(output_file)
    raw_data = readlines_of_utf8_file(input_file)
    gsc2char_list_dict = {}
    gsc_pos = 1
    char_pos = 0
    gsc_number_list = get_ordered_list_of_gsc_numbers()
    for rd in raw_data:
        rd = rd.split('\t')
        if rd[gsc_pos] not in gsc2char_list_dict:
            gsc2char_list_dict[rd[gsc_pos]] = ''
        gsc2char_list_dict[rd[gsc_pos]] = rd[char_pos]
    retval = {}
    for gsc in gsc_number_list:
        if gsc in gsc2char_list_dict:
            if gsc not in retval:
                retval[gsc] = []
            retval[gsc] = gsc2char_list_dict[gsc]
    for g in retval:
        for e in retval[g]:
            append_line_to_utf8_file(output_file, g + '\t' + e + '\t')
            print(g + ': ' + e)

def transform_missing_sch_file3_ordered_list():
    funct_name = 'transform_missing_sch_file_ordered_list()'
    input_file = os.path.join(get_phonological_data_dir(), 'char2gsc.txt')
    output_file = os.path.join(get_phonological_data_dir(), 'missing_schuessler_char_list3.txt')
    if not if_file_exists(input_file, funct_name):
        return
    delete_file_if_it_exists(output_file)
    raw_data = readlines_of_utf8_file(input_file)
    gsc2char_list_dict = {}
    gsc_pos = 2
    char_pos = 0
    proxy_pos = 1
    #暟	闓	27-2
    gsc_number_list = get_ordered_list_of_gsc_numbers()
    proxy2char_dict = {}
    for rd in raw_data:
        rd = rd.split('\t')
        if rd[gsc_pos] not in gsc2char_list_dict:
            gsc2char_list_dict[rd[gsc_pos]] = ''
        gsc2char_list_dict[rd[gsc_pos]] = rd[proxy_pos]
        if rd[proxy_pos] not in proxy2char_dict:
            proxy2char_dict[rd[proxy_pos]] = ''
        proxy2char_dict[rd[proxy_pos]] = rd[char_pos]
    retval = {}
    for gsc in gsc_number_list:
        if gsc in gsc2char_list_dict:
            if gsc not in retval:
                retval[gsc] = []
            retval[gsc] = gsc2char_list_dict[gsc]
    for g in retval:
        for e in retval[g]:
            c = proxy2char_dict[e]
            append_line_to_utf8_file(output_file, c + '\t' + g + '\t' + e)
            print(c + ': ' + g + ': ' + e)

def if_file_exists(filename, funct_name):
    retval = False
    if os.path.isfile(filename):
        retval = True
    else:
        print(funct_name + ' ERROR: Invalid input file:  ' + filename)
    return retval

if 0:
    local_var2normal_char_dict = {}
def readin_local_variants():
    funct_name = 'readin_local_variants()'
    global local_var2normal_char_dict
    if local_var2normal_char_dict:
        return
    input_file = os.path.join(get_soas_code_dir(), 'hanproj', 'hanproject', 'local_variants.txt')
    if not if_file_exists(input_file, funct_name):
        return
    data = readlines_of_utf8_file(input_file)
    for d in data:
        d = d.split('\t')
        if d[0] not in local_var2normal_char_dict:
            local_var2normal_char_dict[d[0]] = ''
        local_var2normal_char_dict[d[0]] = d[1]

if 0:
    def convert_local_variant2normal_char(tchar):
        if tchar in local_var2normal_char_dict:
            tchar = local_var2normal_char_dict[tchar]
        return tchar

def test_readin_local_variants():
    readin_local_variants()

if 0:
    char2gy_dict = {}
    def readin_guangyun_data():
        funct_name = 'readin_guangyun_data()'
        global char2gy_dict
        if char2gy_dict:
            return
        input_file = os.path.join(get_phonological_data_dir(), 'baxter_guangyun_utf8.txt')
        if not if_file_exists(input_file, funct_name):
            return
        raw_data = readlines_of_utf8_file(input_file)
        for rd in raw_data:
            rd = rd.split('\t')
            char_list = rd[10]
            # print(char_list)
            char_list = list(set(char_list))
            for c in char_list:
                if c not in char2gy_dict:
                    char2gy_dict[c] = []
                char2gy_dict[c].append('\t'.join(rd))
                # test = '聑𠲷𢬴笘喋㝪跕䩞𧚊㑙𨓊涉䶬'
                # print('test=' + test)
                # test = list(set(test))
                # print('list(set(test))=' + ''.join(test))
if 0:
    def get_guangyun_data_for_char(schar):
        readin_guangyun_data()
        retval = ''
        if schar in char2gy_dict:
            retval = char2gy_dict[schar]
        return retval

def semiautomatically_approximate_schuessler_late_han():
    funct_name = 'semiautomatically_approximate_schuessler_late_han()'
    input_file = os.path.join(get_phonological_data_dir(), 'need_shengfu_file.txt')
    #output_file = os.path.join(get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    output_file = os.path.join(get_phonological_data_dir(), 'char2gsc.txt')
    print('Reading in current Schuessler data...')
    # current_schuessler = readin_most_complete_schuessler_data()
    print('\tDone.')
    if not if_file_exists(input_file, funct_name):
        return
    raw_data = readlines_of_utf8_file(input_file)
    print(u'Output will go to the \'' + output_file + u'\' file!')
    for zi in raw_data:
        # rd = rd.split('\t')
        # char_list = rd[10]
        gy_data = get_guangyun_data_for_char(zi)
        failed = []
        for gd in gy_data:
            try:
                gd = gd.split('\t')
                char_list = gd[10]
            except IndexError as ie:
                x = 1
            # print(rd + ': ' + char_list)
            char_list = list(set(char_list))
            clinc = 0
            msg_out = zi + '- '
            for cl in char_list:
                gsc = get_gsc_number(cl)
                if gsc == -1:
                    gsc = 'X'
                    clinc += 1
                    continue
                msg_out += str(clinc) + ':' + cl + '(' + str(gsc) + '), '
                clinc += 1
            msg_out = msg_out[0:len(msg_out) - len('), ') + 1]
            var = input("Select number: " + msg_out + '\n')
            print()
            print("you entered:", var)
            print()

            substitute = char_list[int(var)]
            # if substitute in current_schuessler:
            #    lhan = current_schuessler[substitute]
            gsc_num = get_gsc_number(substitute)
            print("-> " + substitute + " => " + str(gsc_num))
            if str(gsc_num).strip() and gsc_num != -1:
                print('Writing \'' + substitute + '\t' + str(gsc_num) + '\' to file.')
                append_line_to_utf8_file(output_file, zi + '\t' + substitute + '\t' + str(gsc_num))
            else:
                print('No GSC number!')
                failed.append(zi)
    print(str(len(failed)) + ' number of characters did not have an GSC. Redo those!')
    print(''.join(failed))

                #test_readin_local_variants()
            #get_list_of_chars_missing_sch_data_ordered_by_gsc_num()
def readin_most_complete_schuessler_data():
    funct_name = 'readin_most_complete_schuessler_data()'
    input_file = os.path.join(get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    if not if_file_exists(input_file, funct_name):
        return []
    data = readlines_of_utf8_file(input_file)
    retval = {}
    for d in data:
        d = d.split('\t')
        if d[0] not in retval:
            retval[d[0]] = []
        retval[d[0]].append(d[1])
    return retval

if 0:
    def get_user_msg_given_gsr_n_gsc_numbers(gsr, gsc, zi=''):
        msg_out = ''
        if gsc != -1:  #
            msg_out += 'GSC ' + gsc + '):'
        elif gsr:
            msg_out += 'GSR ' + gsr + '; No GSC#!):'
        else:
            msg_out += 'No GSR or GSC number. Use same MC method!)'
            if zi:
                gy_data = get_guangyun_data_for_char(zi)
                if gy_data:
                    msg_out += '\n' + gy_data
        return msg_out

def append_char_to_most_complete_schuessler_late_han_data(tchar):
    funct_name = 'append_char_to_most_complete_schuessler_late_han_data()'
    sch_data = readin_most_complete_schuessler_data()
    output_file = os.path.join(get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    if tchar in sch_data:
        return True
    normal = ''
    normal_gsr = ''
    normal_gsc = ''
    if is_compatibility_char(tchar):
        normal = get_normal_char_given_compatibility_char(tchar)
        normal_gsr = get_gsr_number(normal) # returns '' on failure
        normal_gsc = get_gsc_number(normal) # returns -1 on failure
    else:
        normal = tchar
        gsr = get_gsr_number(tchar)
        gsc = get_gsc_number(tchar)

    msg_out = 'Input Late Han pronunciation for ' + normal + ' ('
    if normal:
        msg_out += get_user_msg_given_gsr_n_gsc_numbers(normal_gsr, normal_gsc)
        lhan = input(msg_out + '\n')
        file_msg = normal + '\t' + lhan
        if normal not in sch_data:
            print('file_msg=' + file_msg)
            append_line_to_utf8_file(output_file, file_msg)
        file_msg = tchar + '\t' + lhan
        print('file_msg=' + file_msg)
        append_line_to_utf8_file(output_file, file_msg)
        return
    gsr = get_gsr_number(tchar)
    gsc = get_gsc_number(tchar)
    msg_out += get_user_msg_given_gsr_n_gsc_numbers(gsr, gsc)
    lhan = input(msg_out + '\n')
    file_msg = tchar + '\t' + lhan
    print('file_msg=' + file_msg)
    append_line_to_utf8_file(output_file, file_msg)

def test_append_char_to_most_complete_schuessler_late_han_data():
    funct_name = 'test_append_char_to_most_complete_schuessler_late_han_data()'
    test_char_list = '蹊濭滂尫婿毹蒂喚幬笳' #'神福祥祐祝視祑節者廉虜'
    test_char_list = list(set(test_char_list))
    for t in test_char_list:
        #print(t)
        append_char_to_most_complete_schuessler_late_han_data(t)
        #print(t)
#test_append_char_to_most_complete_schuessler_late_han_data()
##readin_max_gsc_num_per_bu()
#get_ordered_list_of_gsc_numbers()
#get_list_of_chars_missing_sch_data_ordered_by_gsc_num()
#print_out_chars_missing_schuessler_data_to_gsc_num()
#readin_chars_missing_schuessler_data()
#test_create_tree()
#test_get_gsr_number()
#test_get_normal_char_given_compatibility_char()
#transform_missing_sch_file2_ordered_list()
#semiautomatically_approximate_schuessler_late_han()
#transform_missing_sch_file3_ordered_list()