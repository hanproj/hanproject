#! C:\Python36\
# -*- encoding: utf-8 -*-
#
import os
from py3_outlier_utils import readlines_of_utf8_file
from py3_outlier_utils import get_data_from_pos
from py3_outlier_utils import readlines_of_utf8_file
from py3_outlier_utils import append_line_to_utf8_file

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
