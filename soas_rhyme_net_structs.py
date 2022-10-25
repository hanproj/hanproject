#! C:\Python36\
# -*- encoding: utf-8 -*-
import os
import codecs
from soas_imported_from_py3 import is_kana_letter # safe
from soas_imported_from_py3 import readlines_of_utf8_file # safe
from soas_network_utils import parse_schuessler_late_han_syllable # safe
from soas_network_utils import get_schuessler_late_han_for_glyph # safe
from soas_network_utils import get_rhyme_from_late_han
#from soas_network_utils import readin_results_of_community_detection
from soas_network_utils import readin_community_detection_group_descriptions
#from soas_network_utils import get_com_det_group_descriptions_for_combo_data
from hanproj_filename_depot import filename_depot
from soas_network_utils import exception_chars
from soas_network_utils import punctuation
from soas_network_utils import readin_most_complete_schuessler_data
from soas_network_utils import append_line_to_output_file
from soas_network_utils import get_rhyme_from_schuessler_late_han_syllable
from anytree import Node, RenderTree, PreOrderIter, AsciiStyle
from soas_tree_structure import get_list_of_fayin_paths
from soas_network_utils import velar_initials
#from soas_misc import get_user_msg_given_gsr_n_gsc_numbers
#from soas_misc import get_guangyun_data_for_char
#from soas_misc import get_gsc_number
#from soas_misc import get_gsr_number
from soas_imported_from_py3 import readin_char2gsr_data
from soas_imported_from_py3 import is_compatibility_char
from soas_imported_from_py3 import readin_gsr2gsc_num_data
from soas_imported_from_py3 import convert_gsr2gsc_number
from soas_imported_from_py3 import readin_kcompatibility_variant_data_into_dict
from soas_imported_from_py3 import get_normal_char_given_compatibility_char
from soas_imported_from_py3 import is_compatibility_char
from soas_imported_from_py3 import get_gsr_number
from soas_imported_from_py3 import get_gsc_number
from soas_imported_from_py3 import get_user_msg_given_gsr_n_gsc_numbers

from soas_imported_from_py3 import convert_local_variant2normal_char
from soas_imported_from_py3 import local_var2normal_char_dict
from timeit import default_timer as timer
from datetime import timedelta
from time import gmtime, strftime

# NOTE: the similar looking chars are actually different code points
# also, this is necessary because there are a lot of exception characters in the mirror data
not_rhyming_char = ['□', '…', '・', '󸌇', '･', '、', '＊', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '×', '○',
                    'α', '‐', '【缺】', '■', '}']

def remove_unwanted_chars_from_str(tstr):
    unwanted_chars = [')','>','｛','？',']','「','”','）','■','；','：','\'','、','」', '･', '＊','×','?', '○','】','‐', '］',
                      '＝','●','々', 'e', ':','』','〕','Ⅱ', '!', '！', '》', '〗', '}', '☒']
    #if any(uc in tstr for uc in unwanted_chars):
    for c in unwanted_chars:
        if c in tstr:
            tstr = tstr.replace(c,'')
    return tstr

def debug_msg(funct_name, msg, print_msg):
    if print_msg:
        print(funct_name + ' ' + msg)

class rnetwork: # rhyme network
    def __init__(self):
        self.node_dict = {}
        self.same_zi_multi_rhyme_cnt = 0 # Number of times the same characters rhyme more than once in the same stanza
                                         # over the whole Shijing
    def add_node(self, zi, poem_stanza_num, raw_line, late_han_rhyme=''):
        if zi.isdigit():
            return
        if is_kana_letter(zi):
            return
        zi = remove_unwanted_chars_from_str(zi)
        if not zi.strip():
            return
        if late_han_rhyme:
            zi = zi + ' (' + late_han_rhyme + ')'
        if zi in self.node_dict:
            self.node_dict[zi].increment_node_weight()
            self.node_dict[zi].add_an_occurrence(poem_stanza_num)
            return
        if zi not in self.node_dict:
            self.node_dict[zi] = rnode(zi, poem_stanza_num, raw_line)
            self.color_store.add_rhyme_word(zi)

def test_late_han_data():
    s_p = stanza_processor()
    test_char = '土'
    lhan = s_p.get_late_han(test_char)
    x = 1

class stanza_processor:
    def __init__(self, data_type):
        self.rmarker = rhyme_marker()
        self.zero_out_data()
        self.every_line_rhymes = False # True = every line has rhyme; False = every other line has rhyme
        self.exception_chars = exception_chars #['之', '兮', '乎', '也', '矣']
        self.punctuation = punctuation
        self.data_type = data_type
        self.glyph2late_han = readin_most_complete_schuessler_data()
        self.temp_naive_output_file = ''

    def get_late_han(self, glyph):
        retval = ''
        if glyph in self.glyph2late_han:
            retval = self.glyph2late_han[glyph]

        return retval

    def input_stanza(self, stanza_str, stanza_id, every_line_rhymes):
        self.zero_out_data()
        self.stanza_str = stanza_str
        self.stanza_id = stanza_id
        self.every_line_rhymes = every_line_rhymes

    def zero_out_data(self):
        self.stanza_id = ''
        self.stanza_str = ''
        self.rmarker.reset_memory()

    def annotate_with_combo_community_detection(self):
        funct_name = 'annotate_with_combo_community_detection()'
        #annotated_stanza, rw_list = self.naively_annotate() # instead of using thi, write results out to file, and use that
        annotated_stanza, rw_list = self.re_use_naively_annotated_data()
        filename_storage = filename_depot()
        com_det_file = filename_storage.get_filename_for_combined_data_community_detection()
#        com_det_file = get_com_det_group_descriptions_for_combo_data()
        desired_groups = [] # if empty, it gets all groups
        rw2group_dict, group2rw_list = readin_community_detection_group_descriptions(com_det_file, desired_groups)
        rw_pos = 0
        group_id_pos = 0
        cd_annotated_stanza = [] # cd = com det
        for nas in annotated_stanza:
            if '唌々' in nas:
                x = 1
            if 'a' in nas: # the naively annotated stanza always (Not always! Yes! always!) uses 'a' to mark rhymes
                nas = nas.split('a')
                rw = nas[1][0]
                # get marker
                if rw in rw2group_dict:
                    group_num_tup = rw2group_dict[rw] # (group_id, node_weight, orig_node_id)
                    if len(group_num_tup) > 1:
                        x = 1
                    group_num = int(group_num_tup[0][group_id_pos])
                else:
                    cd_annotated_stanza.append(''.join(nas))
                    continue
                marker = get_com_det_rhyme_marker(group_num)
                # annotate line
                try:
                    new_line = str(nas[0]) + marker + str(nas[1])
                except TypeError as te:
                    x = 1
                cd_annotated_stanza.append(new_line)
            else: # not a rhyming line
                cd_annotated_stanza.append(nas)
        return cd_annotated_stanza, rw_list

    def re_use_naively_annotated_data(self):
        if self.temp_naive_output_file:
            return self.readin_temp_naively_annotated_data()
        else:
            return self.naively_annotate()

    def naively_annotate(self, temp_naive_output_file=''):
        funct_name = 'naively_annotate()'#'get_rhyme_words_from_stanza()'
        annotated_stanza = []
        rw_list = []
        self.temp_naive_output_file = temp_naive_output_file
        #if self.temp_naive_output_file:
        #    delete_file_if_it_exists(self.temp_naive_output_file)
        if not self.stanza_str.strip() or '。' not in self.stanza_str:
            return annotated_stanza, rw_list
        # There is some weirdness with mirror punctuation for a minority of mirrors.
        # These need to be handled differently. The ones without the weirdness (i.e., the majority) are
        # processed normally
        if self.data_type == 'mirrors' and if_special_mirror_punctuation(self.stanza_str):
            return get_rhyme_words_for_kmss2015_mirror_inscription(self.stanza_id, self.stanza_str, self.every_line_rhymes,self.temp_naive_output_file)

        stanza = self.stanza_str.split('。')
        line_inc = 0
        modulo = 2
        if self.every_line_rhymes:
            modulo = 1
        for line in stanza:
            if not line.strip() or line[len(line)-1] == '：':
                continue
            #if '沒□□□' in line:
            #    x = 1
            line_inc += 1
            line_id = self.stanza_id + '.' + str(line_inc)
            # if this is a rhyming line...
            if not line_inc % modulo:
                zi = line[len(line) - 1]  # get the rhyming word
                zi_pos = len(line) - 1  # get the rhyming word's position
                if zi == '々': # get the character preceeding 々
                    zi = line[len(line) - 2]
                    zi_pos -= 1
                if zi == ')' or zi == '）':
                    if '（下闕）' in line: # special case for inline notes in Stelae
                        if line[zi_pos - 1] == '闕':
                            zi_pos -= len('（下闕）')
                            zi = line[zi_pos]
                            x = 1
                    else:
                        zi_pos -= 3
                        try:
                            zi = line[zi_pos]
                        except IndexError as ie:
                            x = 1

                if any(exception_char in zi for exception_char in self.exception_chars):
                    zi = line[len(line) - 2]
                    zi_pos -= 1

                if any(punk_char in zi for punk_char in self.punctuation):
                    zi_pos -= 1
                    zi = line[zi_pos]

                #if zi == '□' or zi == '…' or zi == '・' or zi == '󸌇' or zi == '･' or zi == '、': # note: ・ = U+FF65, ・ = U+30FB
                if any(c in zi for c in not_rhyming_char):
                    #
                    # annotate line
                    annotated_stanza.append(line)
                    rw_list.append(('', -1, line, line_id))
                    continue

                if '}' == line[zi_pos]:
                    annotated_stanza.append(line)
                    rw_list.append(('', -1, line, line_id))
                    continue
                # Annotate the rhyme, but don't add it to the list of rhyme words (won't have a late han reading)
                left = line[:zi_pos]
                right = line[zi_pos:]
                new_line = left + 'a' + right
                annotated_stanza.append(new_line)
                rw_list.append((zi, zi_pos, line, line_id))
            else:
                #
                # this line doesn't need annotation, as it doesn't have a rhyme word
                rw_list.append(('', -1, line, line_id))
                annotated_stanza.append(line)
        if self.temp_naive_output_file:
            delete_file_if_it_exists(self.temp_naive_output_file)
            delim = '\t'
            for astan in annotated_stanza:
                append_line_to_utf8_file(self.temp_naive_output_file, astan)
            for tup in rw_list:
                line_out = tup[0] + delim + str(tup[1]) + delim + tup[2] + delim + tup[3]
                append_line_to_utf8_file(self.temp_naive_output_file, line_out)
        return annotated_stanza, rw_list  # rw2line_dict

    def readin_temp_naively_annotated_data(self):
        funct_name = 'readin_temp_naively_annotated_data()'
        annotated_stanza =  []
        rw_list = []
        if if_file_exists(self.temp_naive_output_file, funct_name):
            data_lines = readlines_of_utf8_file(self.temp_naive_output_file)
            for dl in data_lines:
                if dl.count('\t') == 3:
                    dl = dl.split('\t')
                    rw_list.append((dl[0], dl[1], dl[2], dl[3]))
                else:
                    annotated_stanza.append(dl)
        return annotated_stanza, rw_list

    def schuessler_annotate(self):
        funct_name = 'schuessler_annotate()'
        print_debug_msgs = True
        annotated_stanza, rw_list = self.re_use_naively_annotated_data()#self.naively_annotate()
        rw_pos = 0
        #
        # Calculate optimized rhyme path for rhyme words
        lh_fayin_dict = {}
        raw_rw_list = []
        rhyme2rw_list = {}
        for e in rw_list:
            rw_word = e[rw_pos]
            if rw_word:
                raw_rw_list.append(rw_word)
        for rw_word in raw_rw_list:
            if rw_word not in lh_fayin_dict:
                lh_fayin_dict[rw_word] = []
            if rw_word == '土':
                x = 1
            lhan_list = self.get_late_han(rw_word)  # possibly has multiple readings
            for lh in lhan_list:
                if lh not in lh_fayin_dict[rw_word]:
                    lh_fayin_dict[rw_word].append(lh)
        #
        # chooses single reading for each character by optimizing rhyme group for rhyming
        #debug_msg(funct_name, 'BEGIN pronunciation path calculation for:\n\t' + ''.join(raw_rw_list) + '...', print_debug_msgs)
        #debug_file = 'fayin_path_test_data.txt' # DEBUG ONLY
        #delete_file_if_it_exists(debug_file)# DEBUG ONLY
        #append_lh_fayin_dict_data_to_file(debug_file,lh_fayin_dict, True) # DEBUG ONLY
        #start_time = timer()
        #root_node = create_tree(lh_fayin_dict) # ------- original code
        #pad_list = given_root_node_get_list_of_possible_paths(root_node) # ------- orginal code
        #end_time = timer()
        #print('\tTime elapsed:')
        #print('\t\t' + str(timedelta(seconds=end_time - start_time)))

        #append_pad_list_data_to_file(debug_file, pad_list, True) # DEBUG ONLY
        print('Calculating all possible pronunciation paths, starting at:')
        print('\t' + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        num_readings = 0
        for c in lh_fayin_dict:
            num_readings += len(lh_fayin_dict[c])
        print('\t' + str(len(lh_fayin_dict)) + ' rhyming words, and ' + str(num_readings) + ' readings.')
        start_time = timer()
        pad_list = get_list_of_fayin_paths(lh_fayin_dict) # replaces library
        end_time = timer()
        print('\tTime elapsed:')
        print('\t\t' + str(timedelta(seconds=end_time - start_time)))
        print(str(len(pad_list)) + ' possible paths.')
        print('')
        print('Calculating optimized path:')
        start_time = timer()
        lh_fayin_path = find_path_optimized_for_rhyme(pad_list)
        end_time = timer()
        print('\tTime elapsed:')
        print('\t\t' + str(timedelta(seconds=end_time - start_time)))

        #debug_msg(funct_name, '\tEND pronunciation calculation.', print_debug_msgs)
        rw2lhan_dict = {}
        kinc = 0
        for ck in lh_fayin_dict:
            if ck not in rw2lhan_dict:
                rw2lhan_dict[ck] = ''
            try:
                rw2lhan_dict[ck] = lh_fayin_path[kinc]
            except IndexError as ie:
                #get_user_msg_given_gsr_n_gsc_numbers
                #get_guangyun_data_for_char
                # get_gsc_number()
                # get_gsr_number()
                gsc_num = get_gsc_number(ck)
                gsr_num = get_gsr_number(ck)
                msg = get_user_msg_given_gsr_n_gsc_numbers(gsr_num, gsc_num, ck)
                print(ck + ' is missing data.\n\t' + msg)
                x = 1

            kinc += 1
        #
        # Schuessler Annotate Stanza
        s_annotated_stanza = []
        for nas in annotated_stanza:
            if 'a' in nas: # the naively annotated stanza always (Not always! Yes! always!) uses 'a' to mark rhymes
                nas = nas.split('a')
                rw = nas[1][0]
                if rw == '{': # in the original data, the author uses { } for character formulas, but we won't have
                    # late Han data for them, so just treat them like non-rhyming lines
                    s_annotated_stanza.append(nas)
                    continue
                late_han = rw2lhan_dict[rw]
                rhyme = get_rhyme_from_late_han(late_han) # takes string input
                if not rhyme.strip():
                    chars_missing_data = []
                    for k in lh_fayin_dict:
                        if not lh_fayin_dict[k]:
                            chars_missing_data.append(k)
                    for c in chars_missing_data:
                        gsc_num = get_gsc_number(c)
                        gsr_num = get_gsr_number(c)
                        msg = get_user_msg_given_gsr_n_gsc_numbers(gsr_num, gsc_num, c)
                        print(c + ' is missing data.\n\t' + msg)
                        x = 1

                if rhyme not in rhyme2rw_list:
                    rhyme2rw_list[rhyme] = []
                rhyme2rw_list[rhyme].append(rw)
                # get marker
                marker = self.rmarker.get_marker(rhyme)
                # annotate line
                new_line = nas[0] + marker + '(' + rhyme + ')' + nas[1]
                s_annotated_stanza.append(new_line)
            else: # not a rhyming line
                s_annotated_stanza.append(nas)

        return s_annotated_stanza, rw_list, rw2lhan_dict, rhyme2rw_list
        #
        # TO DO:
        # - finish up this function
        #   a. use schuessler annotation -- need markers
        #   b. you have all of the

def if_special_mirror_punctuation(stanza_str):
    retval = False
    if '，' in stanza_str and '。' in stanza_str:
        retval = True
    return retval

def delete_file_if_it_exists(filename):
    if os.path.isfile(filename):
        os.remove(filename)

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


# IMPORTANT: This is using a naive assumption about the rhyming patterns
# ASSUMPTIONS:
#   - (if no 「，」) rhyme words appear before 「。」
#   - (if both 「，」、「。」) rhyme words appear before 「，」、「。」
def get_rhyme_words_for_kmss2015_mirror_inscription(unique_id, inscription, every_line_rhymes, output_file='', use_unpunctuated=False):
    funct_name = 'get_rhyme_words_for_kmss2015_mirror_inscription()'
    punct_list = ['。', '，']
    retval = []
    annotated_stanza = []
    if use_unpunctuated and '，' not in inscription and '。' not in inscription:  # handle unpunctuated case
        return retval, annotated_stanza
    elif '，' in inscription:  # handle ...，...，...。 case
        #if inscription.count('。') > 1:
        #    debug_file = os.path.join(get_hanproj_dir(), 'mirrors', 'mirror_debug_data.txt')
        #    db_msg = funct_name + ' UNUSUAL situation. ' + unique_id + ' has both 「，」、「。」 AND '
        #    db_msg += '\tmore than one 「。」]\n\t' + inscription
        #    print(db_msg)
        #    append_line_to_utf8_file(debug_file, db_msg)
        #    return retval
        inscription = inscription.replace('。', '')
        inscription = inscription.split('，')
        line_inc = 0
        line_id = ''
        modulo = 2
        if every_line_rhymes:
            modulo = 1

        for i in inscription:
            last_char = grab_last_character_in_line(i)
            line_inc += 1
            line_id = unique_id + '.' + str(line_inc)
            if not line_inc % modulo: # even lines if 'every_line_rhymes' = True, all lines otherwise
                if last_char:
                    char_pos = last_char[1]
                    last_char = last_char[0]
                #if '・' in last_char or '…' in last_char or '□' in last_char:
                if any(c in last_char for c in not_rhyming_char):
                    retval.append(('', -1, i, line_id))
                    annotated_stanza.append(i)
                    last_char = ''
                    char_pos = ''
                    continue
                if any(c in last_char for c in punctuation):
                    retval.append(('', -1, i, line_id))
                    annotated_stanza.append(i)
                    last_char = ''
                    char_pos = ''
                    continue
                if last_char == '々': # get the character preceeding 々
                    #zi = line[len(line) - 2]
                    char_pos -= 1
                    last_char = i[char_pos]

                if last_char and (last_char, char_pos, i, line_id) not in retval:
                    retval.append((last_char, char_pos, i, line_id))
                    left = i[:char_pos]
                    right = i[char_pos:]
                    new_line = left + 'a' + right # this assuming naive anntotation
                    annotated_stanza.append(new_line)
                else:
                    retval.append(('', -1, i, line_id))
                    annotated_stanza.append(i)
                last_char = ''
                char_pos = ''
                i = ''
            else:
                retval.append(('', -1, i, line_id))
                annotated_stanza.append(i)
                last_char = ''
                char_pos = ''
                continue

    if retval and retval[len(retval) - 1] == '':
        retval = retval[0:len(retval) - 1]
    if output_file: #  output_file
        delete_file_if_it_exists(output_file)
        delim = '\t'
        for astan in annotated_stanza:
            append_line_to_utf8_file(output_file, astan)
        #line_inc = 0
        for tup in retval:
            #line_inc += 1
            line_out = tup[0] + delim + str(tup[1]) + delim + tup[2] + delim + tup[3]
            append_line_to_utf8_file(output_file, line_out)
    return annotated_stanza, retval

def grab_last_character_in_line(line):
    funct_name = 'grab_last_character_in_line()'
    # take into account 虛字 like 之、兮、乎, etc
    if not line.strip():
        return ''
    if '守善不報，' in line:
        x = 1
    #exception_chars = ['之', '兮', '乎', '也', '矣', '焉']
    char_pos = len(line)-1
    last_char = line[len(line)-1]
    if last_char == '）':
        last_char = line[len(line) - 2]
        char_pos -= 1
    elif last_char in exception_chars:
        last_char = line[len(line) - 2]
        char_pos -= 1
    return last_char, char_pos


#
# input data should be of the format:
# key = '鄉'
# value = ['hian']
def create_tree(test_data_dict):
    funct_name = 'create_tree()'
    root_node = Node("root")
    prev_parent = [root_node]
    total_nodes = []
    #total_nodes.append(root_node)
    for e in test_data_dict:
        fayin = test_data_dict[e]
        if 'str' in str(type(fayin)):
            fayin = fayin.split(' ')
        fayin_nodes = []
        for fy in fayin:
            for pp in prev_parent:
                temp_node = Node(fy, parent=pp)
                #total_nodes.append(temp_node)
                fayin_nodes.append(temp_node)
        prev_parent = fayin_nodes[:]
    return root_node

def given_root_node_get_list_of_possible_paths(root_node):
    funct_name = 'given_root_node_get_list_of_possible_paths()'
    pad_list = []  # list of paths
    if str(root_node) != 'Node(\\''/root\\'')':
        try:
            test_list = [list(leaf.path) for leaf in
                         PreOrderIter(root_node, filter_=lambda node: node.is_leaf)]
        except TypeError as te:
            return pad_list
        for tl in test_list:
            p = str(tl[len(tl) - 1])  # .path
            pad = retreive_path_from_nodes(p)
            if pad not in pad_list:
                pad_list.append(pad)
    return pad_list

def retreive_path_from_nodes(node):
    if not node:
        return node
    orig_node = node
    node = node.split('/')
    node = node[2:len(node)]
    if not node:
        return orig_node
    last_n = node.pop().replace(')','')
    last_n = last_n.replace('\'','')
    node.append(last_n)
    return node

#
# TO DO:
# write a version of parse_schuessler_late_han_syllable() that ONLY gets the final
# calculating and return 4 values is not efficient. this function is taking a long time
# for large data sets. Find any and every way to speed it up
def find_path_optimized_for_rhyme(path_list, is_verbose=False):
    funct_name = 'find_path_optimized_for_rhyme()'
    rmarker = rhyme_marker()
    path2data_dict = {}
    pinc = 0
    retval = ''
    if len(path_list) > 1:
        for pad in path_list:
            if pinc not in path2data_dict:
                path2data_dict[pinc] = {}
            for lhan in pad:
                rhyme = get_rhyme_from_schuessler_late_han_syllable(lhan) # was n_rhyme
                #initial, medial, rhyme, pcoda = parse_schuessler_late_han_syllable(lhan)
                #if n_rhyme != rhyme:
                #    if n_rhyme == 'ue' and rhyme == 'e':
                #        x = 1 # ignore this case
                #    elif n_rhyme == 'an' and rhyme == 'n':
                #        x = 1 # ignore this case
                    #elif n_rhyme == 'ua' and rhyme == 'a':
                    #    x = 1 # ignore this case
                #    elif n_rhyme == 'u' + rhyme:
                #        if initial in velar_initials:
                #            x = 1
                #    elif rhyme[0] == 'y':
                #         x = 1
                #    else:
                #        x = 1 # this is the interesting case
                # mark = rmarker.get_marker(rhyme)
                if rhyme not in path2data_dict[pinc]:
                    path2data_dict[pinc][rhyme] = 0
                path2data_dict[pinc][rhyme] += 1
            pinc += 1
        pinc2min_singles = {}
        for k1 in path2data_dict:
            if k1 not in pinc2min_singles:
                pinc2min_singles[k1] = 0
            for k2 in path2data_dict[k1]:
                if is_verbose:
                    print('[' + str(k1) + '][' + k2 + '] = ' + str(path2data_dict[k1][k2]))
                if path2data_dict[k1][k2] == 1:
                    pinc2min_singles[k1] += 1
        min_singles = 10000000
        min_inc = -1
        for pinc in pinc2min_singles:
            if pinc2min_singles[pinc] <= min_singles:
                min_singles = pinc2min_singles[pinc]
                min_inc = pinc
        if is_verbose:
            print('MIN: min # singles: ' + str(min_singles) + ', inc = ' + str(min_inc))
            print('=> ' + ' '.join(path_list[min_inc]))
        retval = path_list[min_inc]
    elif len(path_list) == 1:
        retval = path_list[0]

    return retval

rw_list_for_rm = ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z', 'aa', 'bb', 'cc', 'dd', 'ee', 'ff', 'gg', 'hh', 'ii', 'jj', 'kk', 'll', 'mm', 'nn', 'oo',
                  'pp', 'qq', 'rr', 'ss', 'tt', 'uu', 'vv', 'ww', 'xx', 'yy', 'zz']
class rhyme_marker:
    def __init__(self):
        self.rw_list = rw_list_for_rm[:]
        #self.rhyme2marker_dict = {}
        self.reset_memory()
        #self.cnt = -1

    def get_marker(self, rhyme):
        retval = ''
        if rhyme in self.rhyme2marker_dict:
            retval = self.rhyme2marker_dict[rhyme]
        else:
            self.cnt += 1
            retval = self.rw_list[self.cnt]
            self.rhyme2marker_dict[rhyme] = retval
        return retval

    def reset_memory(self):
        self.rhyme2marker_dict = {}
        self.rw2lhan_dict = {}
        self.marker2rhyme_dict = {}
        self.cnt = -1
        self.m2r_dict = {}

    def fill_marker2rhyme_dict(self, stanza_rw_list):
        if self.marker2rhyme_dict:
            return
        for rw in stanza_rw_list:
            lhan = get_schuessler_late_han_for_glyph(rw)
            if not lhan:
                continue
            if ' ' in lhan:
                lhan = lhan.split(' ')
            else:
                lhan = [lhan]
            #if self.cnt == -1:
            #    self.cnt = 0
            for lh in lhan:
                #initial, medial, rhyme, pcoda = parse_schuessler_late_han_syllable(lh)
                rhyme = get_rhyme_from_schuessler_late_han_syllable(lh)
                marker = self.get_marker(rhyme)
                if marker not in self.marker2rhyme_dict:
                    self.marker2rhyme_dict[marker] = rhyme

    def get_marker2rhyme_dict(self):
        #self.fill_marker2rhyme_dict()
        if self.m2r_dict:
            return self.m2r_dict
        rhyme_list = self.rhyme2marker_dict.keys()
        self.m2r_dict = {}
        for r in rhyme_list:
            m = self.rhyme2marker_dict[r]
            if m not in self.m2r_dict:
                self.m2r_dict[m] = ''
            self.m2r_dict[m] = r
        return self.m2r_dict

    def get_rhyme_given_marker(self, m):
        self.get_marker2rhyme_dict()
        retval = ''
        if m in self.m2r_dict:
            retval = self.m2r_dict[m]
        return retval

def if_file_exists(filename, funct_name):
    retval = False
    if os.path.isfile(filename):
        retval = True
    else:
        print(funct_name + ' ERROR: Invalid input file:  ' + filename)
    return retval

def get_phonological_data_dir():
    return os.path.join(get_soas_code_dir(), 'hanproj', 'phonological_data')

def get_hanproj_dir():
    return os.path.join(get_soas_code_dir(), 'hanproj')

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

# latin alphabet from 'a' (97 + 0) -> 'z' (97 + 25)
# latin alphabet from 'A' (65 + 0) -> 'Z' (65 + 25)
# greek alphabet from 'α' (03b1) -> 'ω' (03b1 + 24)
# greek alphbet from 'A' (0391) -> 'Ω' (0391 + 24)
# 1-26: latin lower case
# 27-51: greek lower case
# 51-77: latin upper case
# 78-104: α + {latin lower case}
# 105-131: β + {latin lower case}

def create_list_of_rhyme_markers():
    funct_name = 'create_list_of_rhyme_markers()'
    #a is 61 HEX, 97 DEC; chr(97) = 'a'
    latin_lower = 97
    latin_upper = 65
    greek_lower = 0x03b1
    num_latin_letters = 26
    retval = []
    for inc in range(0, num_latin_letters, 1):
        retval.append(chr(latin_lower + inc))
    num_greek_letters = 25
    for inc in range(0, num_greek_letters, 1):
        retval.append(chr(greek_lower + inc))
    for inc in range(0, num_latin_letters, 1):
        retval.append(chr(latin_upper + inc))
    for o_inc in range(0, num_greek_letters, 1):
        for i_inc in range(0, num_latin_letters, 1):
            retval.append(chr(greek_lower + o_inc) + chr(latin_lower + i_inc))
    for o_inc in range(0, 50, 1):
        for inc in range(0, num_latin_letters, 1):
            retval.append(chr(latin_lower + inc) + str(o_inc))
    x = len(retval)
    return retval

cd_markers = []
def get_com_det_rhyme_marker(group_num):
    global cd_markers
    group_num -= 1 # convert from group number (1 -> N) to array index (0 -> N-1)
    retval = -1
    if not cd_markers:
        cd_markers = create_list_of_rhyme_markers()
    if group_num <= len(cd_markers) - 1:
        retval = cd_markers[group_num]
    return retval

def append_pad_list_data_to_file(filename, pad_list, is_verbose=False):
    funct_name = 'append_pad_list_data_to_file()'
    msg = ''
    for pl in pad_list:
        msg = ' '.join(pl)
        if is_verbose:
            print(msg)
        append_line_to_output_file(filename, msg)

def append_lh_fayin_dict_data_to_file(filename, lh_fayin_dict, is_verbose=False):
    funct_name = 'append_lh_fayin_dict_data_to_file()'
    msg = ''
    for k in lh_fayin_dict:
        msg = k + '\t' + ' '.join(lh_fayin_dict[k])
        if is_verbose:
            print(msg)
        append_line_to_output_file(filename, msg)

    #lh_fayin_path
def test_create_list_of_rhyme_markers():
    markers = create_list_of_rhyme_markers()
    inc = 0
    for m in markers:
        inc += 1
        print('(' + str(inc) + ') ' + m)
#test_create_list_of_rhyme_markers()

#test_late_han_data()