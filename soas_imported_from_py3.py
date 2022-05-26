#! C:\Python36\
# -*- encoding: utf-8 -*-
import os
import codecs
#from py3_outlier_utils import get_py3_project_dir
#from soas_utils import readlines_of_utf8_file
import copy

utf8_bom = '\xef\xbb\xbf'
utf8_bom_b = b'\xef\xbb\xbf'
py_filename = 'py3_middle_chinese.py'
gy_dict = {}

def get_python_dir():
    return os.path.join('C:' + os.sep + 'Ash', 'research', 'code', 'python')

def get_py3_project_dir():
    return os.path.join(get_python_dir(), 'py3_projects')

def get_name_for_this_py_file():
    return os.path.join(get_py3_project_dir(), py_filename)

def get_oc_seminar_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'research', 'OC Seminar Leiden')

def get_guangyun_dir():
    return os.path.join(get_oc_seminar_dir(), 'reference_docs_and_files', 'guangyun_qieyun')

def readin_guangyun_zi_data(verbose=False):
    funct_name = 'readin_guangyun_zi_data()'
    input_file = os.path.join(get_guangyun_dir(),'guangyun_hanzi.txt')
    gy_data = readlines_of_utf8_file(input_file)
    if verbose:
        print(funct_name)
        print('Read in data:')
        for l in gy_data:
            print(l)
        print(str(len(gy_data)) + ' lines of data.')
    return gy_data

def main():
    print('Welcome to ' + get_name_for_this_py_file())
    gy_data = readin_guangyun_zi_data(False)
    gy_dict = {}
    delim = '\t'
    problem_lines = []
    for l in gy_data:
        if l.strip():
            l = l.split(delim)
            if len(l) < 2:
                print('PROBLEM with ' + delim.join(l))
                problem_lines.append(delim.join(l))
                continue
            entry = l[0]
            fayin = l[1]
            if entry not in gy_dict:
                gy_dict[entry] = []
            if fayin not in gy_dict[entry]:
                gy_dict[entry].append(fayin)
    inc = 0
    kinc = 0
    entries_w_multi_vowels = []
    e_finals = []
    rime2heyun_dict = {}
    for k in gy_dict:
        if len(gy_dict[k]) > 1:
            kinc += 1
            e_finals = []
            for l in gy_dict[k]:
                inc += 1
                #print('(' + str(inc) + ') ' + k + delim + l)
                l = l.split('-')[1]
                l = l.split(' ')
                final = l[0]
                yun = l[1][1]
                if final  + ': ' + yun not in e_finals:
                    e_finals.append(final + ': ' + yun)
            if len(e_finals) > 1:
                if k not in entries_w_multi_vowels:
                    entries_w_multi_vowels.append(k)
                for f in e_finals: # for each final...
                    other_finals = copy.deepcopy(e_finals)
                    other_finals.remove(f) # list of finals in e_finals, excluding f
                    if f not in rime2heyun_dict:
                        rime2heyun_dict[f] = []
                    # for each unique list of "other finals", add to the dict
                    if not is_list_a_in_list_of_lists(other_finals, rime2heyun_dict[f]):
                        rime2heyun_dict[f].append(other_finals)
                #print(k + '\t' + '\r\n\t'.join(gy_dict[k]))
                x = 1
    for f in rime2heyun_dict:
        print(f + ':')
        for l in rime2heyun_dict[f]:
            print('\t' + ', '.join(l))

    print(str(kinc) + ' entries have multiple pronunciations.')
    if problem_lines:
        print('There is a PROBLEM with these lines (' + str(len(problem_lines)) + '):')
        for l in problem_lines:
            print(l)

def is_list_a_in_list_of_lists(list_a, list_of_lists):
    funct_name = 'is_list_a_in_list_of_lists()'
    positive_match = False
    for l in list_of_lists:
        if set(l) == set(list_a):
            positive_match = True
    return positive_match

def test_is_list_a_in_list_of_lists():
    funct_name = 'test_is_list_a_in_list_of_lists()'
    l_of_l = ['-ip 影緝 入 三B 開 於汲', '-jep 影葉 入 三B 開 於輒', '-jaep 影業 入 三 開 於業']
    test_lists = ['-ip2 影緝 入 三B 開 於汲', '-jep 影葉 入 三B 開 於輒', '-jaep2 影業 入 三 開 於業']
    for list_a in test_lists:
        is_in_list = is_list_a_in_list_of_lists(list_a, l_of_l)
        if is_in_list:
            print(list_a + ' IS in ' + '\n\r\t'.join(l_of_l))
        else:
            print(list_a + ' is NOT in ' + '\n\r\t'.join(l_of_l))

def calculate_mc_yun2_oc_bu():
    funct_name = 'calculate_mc_yun2_oc_bu()'
    oc_handbook_dir = os.path.join(get_oc_seminar_dir(), 'ashs-oc-handbook')
    input_file = os.path.join(oc_handbook_dir, 'baxter_ocbu2mcyun.csv')
    input_lines = readlines_of_utf8_file(input_file)
    label_list = input_lines[0]
    input_lines = input_lines[1:len(input_lines)]
    oc_bu_pos = 0
    oc_bu_rec_pos = 1
    mc_yun_rec_pos = 2
    mc_deng_pos = 3
    mc_yun_pos = 4
    initial_comment_pos = 5
    delim = '\t'
    oc2mc_dict = {}
    mc2oc_dict = {}
    for l in input_lines:
        #print(l)
        l = l.split(delim)
        oc_bu = l[oc_bu_pos]
        oc_bu_rec = l[oc_bu_rec_pos]
        mc_yun_rec = l[mc_yun_rec_pos]
        mc_deng = l[mc_deng_pos]
        mc_yun = l[mc_yun_pos]
        mc_yun_msg = mc_yun + ' ' + mc_yun_rec
        mc_yun_msg = mc_yun
        if mc_yun_msg not in mc2oc_dict:
            mc2oc_dict[mc_yun_msg] = []

        oc_bu_msg = oc_bu + '部 ' + oc_bu_rec
        oc_bu_msg = oc_bu


        if oc_bu_msg not in mc2oc_dict[mc_yun_msg]:
            mc2oc_dict[mc_yun_msg].append(oc_bu_msg)

        if oc_bu not in oc2mc_dict:
            oc2mc_dict[oc_bu] = []
        if mc_yun not in oc2mc_dict[oc_bu]:
            oc2mc_dict[oc_bu].append(mc_yun)

        try:
            init_comment = l[initial_comment_pos]
        except IndexError:
            init_comment = ''
        msg = 'OC: ' + oc_bu_rec + '(' + oc_bu + ') > ' + mc_yun_rec + ' (' + mc_yun + ' ' + mc_deng + '等)'
        if init_comment:
            msg += ' ' + init_comment
        print(msg)
    for ocbu in oc2mc_dict:
        print(ocbu + '部: ' + u', '.join(oc2mc_dict[ocbu]))
    print()
    for mc_yun in mc2oc_dict:
        print(mc_yun + '： ' + u', '.join(mc2oc_dict[mc_yun]))

def readin_guangyun_zi_dict():
    funct_name = 'readin_guangyun_zi_dict()'
    global gy_dict
    if gy_dict:
        return

    gy_data = readin_guangyun_zi_data()
    for g in gy_data:
        g = g.split('\t')
        zi = g[0]
        zi_data = g[1]
        if '上' in zi_data:
            x = 1
        if zi not in gy_dict:
            gy_dict[zi] = []
        gy_dict[zi].append(zi_data)

def get_mc_data_for_char(tchar):
    funct_name = 'get_mc_data_for_char()'
    readin_guangyun_zi_dict()
    try:
        return gy_dict[tchar]
    except KeyError as ke:
        return {}

def test_get_mc_data_for_char():
    funct_name = 'test_get_mc_data_for_char()'
    print('Welcome to ' + funct_name + '!')
    test_chars = ['𪄛','寔','湜','殖', '識']
    for tc in test_chars:
        data = get_mc_data_for_char(tc)
        print(tc + ': ')
        print('\t' + u'\n\t'.join(data))

def append_line_to_utf8_file(filename, content):
    funct_name = 'append_line_to_utf8_file()'
    output_ptr = safe_open_utf8_file_for_appending(filename)
    output_ptr.write(content + '\n')
    if output_ptr:
        output_ptr.close()

def safe_open_utf8_file_for_appending(filename):
    filename = if_not_unicode_make_it_unicode(filename)
    p, f = os.path.split(filename)
    if p and not os.path.isdir(p):  # if the directory doesn't exist, create it
        os.makedirs(p)
    return codecs.open(filename, 'a', 'utf8')

def if_not_unicode_make_it_unicode(my_str):
    funct_name = 'if_not_unicode_make_it_unicode()'
    if not is_unicode(my_str):
        my_str = my_str.decode('utf8')
    return my_str

def is_unicode(text):
    retval = False
    if 'str' in str(type(text)):
        retval = True
    return retval

def is_kana_letter(test_char):
    return (is_katakana_letter(test_char) or is_hiragana_letter(test_char))

def is_hiragana_letter(test_char):
    lower_limit = '\u3041'
    upper_limit = '\u3093'
    retval = False
    if test_char == '\u30f6' or test_char == '\u30fc' or test_char == '\u30fb':
        retval = True
    else:
        retval = (test_char >= lower_limit) & (test_char <= upper_limit)
    return retval

def is_katakana_letter(test_char):
    # U+30a1 to U+30f6 - doesn't include punctuation
    lower_limit = '\u30a1'
    upper_limit = '\u30f6'
    # ー = U+30fc
    # ・ = U+30fb
    retval = False
    if test_char == '\u30fc' or test_char == '\u30fb':
        retval = True
    else:
        retval = (test_char >= lower_limit) & (test_char <= upper_limit)
    return retval

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

#test_get_mc_data_for_char()
#test_readin_guangyun_zi_data()
#calculate_mc_yun2_oc_bu()
#main()
#test_is_list_a_in_list_of_lists()
