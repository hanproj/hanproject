#! C:\Python36\
# -*- encoding: utf-8 -*-
from PyQt5 import QtWidgets, uic
#from PyQt5 import QtGui.QColor
from PyQt5.QtGui import QColor

#from PyQt5.QtCore import
#QtWidgets.Qcol
import sys
import os
import re
import copy
from soas_network_utils import get_hanproj_dir
from soas_network_utils import readlines_of_utf8_file
from soas_rnetwork_test import delete_file_if_it_exists
from soas_network_utils import append_line_to_output_file
#from soas_network_utils import append_line_to_utf8_file
from soas_imported_from_py3 import append_line_to_utf8_file
from soas_network_utils import is_hanzi
from soas_network_utils import get_rhyme_groups_from_annotated_poem
from soas_network_utils import exception_chars
from soas_network_utils import if_file_exists
from soas_network_utils import readin_most_complete_schuessler_data
from soas_network_utils import is_poem_annotated
from soas_network_utils import does_line_have_rhyme_marker
from soas_network_utils import get_rhyme_word_and_marker_from_line_of_poem

#rw, m = get_rhyme_word_and_marker_from_line_of_poem(p)

#from soas_network_utils import readin_results_of_community_detection
from soas_network_utils import readin_community_detection_group_descriptions

def debug_msg(msg, origin, do_print_msg=False):
    output = ''
    if do_print_msg:
        if origin:
            output = origin + ' '
        output += msg
        print(output)

def file_does_exist(filename):
    retval = False
    if os.path.isfile(filename):
        retval = True
    return retval

def get_received_shi_naively_annotated_file():
    return os.path.join(get_hanproj_dir(), 'received-shi', 'naively_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')

def get_received_shi_com_det_annotated_file():
    return os.path.join(get_hanproj_dir(), 'received-shi', 'com_det_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')

def get_received_shi_schuessler_annotated_file():
    return os.path.join(get_hanproj_dir(), 'received-shi', 'schuessler_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')

def get_mirors_naively_annotated_file():
    return os.path.join(get_hanproj_dir(), 'mirrors', 'naively_annotated_kyomeishusei2015_han_mirror_data.txt')

def get_mirors_schuessler_annotated_file():
    return os.path.join(get_hanproj_dir(), 'mirrors', 'schuessler_annotated_kyomeishusei2015_han_mirror_data.txt')

def get_mirrors_com_det_annotated_file():
    return os.path.join(get_hanproj_dir(), 'mirrors', 'com_det_annotated_kyomeishusei2015_han_mirror_data.txt'
                        )
def get_stelae_naively_annotated_file():
    return os.path.join(get_hanproj_dir(), 'stelae', 'naively_annotated_毛遠明 《漢魏六朝碑刻校注》.txt')

def get_stelae_schuessler_annotated_file():
    return os.path.join(get_hanproj_dir(), 'stelae', 'schuessler_annotated_毛遠明 《漢魏六朝碑刻校注》.txt')

def get_stelae_com_det_annotated_file():
    return os.path.join(get_hanproj_dir(), 'stelae', 'com_det_annotated_毛遠明 《漢魏六朝碑刻校注》.txt')

def readin_received_shi_naively_annotated_data():
    return readin_received_shi_data(get_received_shi_naively_annotated_file())

def readin_received_shi_schuessler_annotated_data():
    return readin_received_shi_data(get_received_shi_schuessler_annotated_file())

def readin_received_shi_com_det_annotated_data():
    return readin_received_shi_data(get_received_shi_com_det_annotated_file())

#kyomeishusei2015_00001: 脩相思、毌相a忘。常樂未a央。
#kyomeishusei2015_00002: 脩相思、願毌相a忘。大樂未a央。
#kyomeishusei2015_00003: 安樂未a央。脩相思、願毌相a忘。
#kyomeishusei2015_00004: 常樂未a央。脩相思、願毌相a忘。
def readin_mirrors_naively_annotated_data():
    funct_name = 'readin_mirrors_naively_annotated_data()'
    return readin_mirrors_data(get_mirors_naively_annotated_file())

def readin_mirrors_schuessler_annotated_data():
    return readin_mirrors_data(get_mirors_schuessler_annotated_file())

def readin_mirrors_com_det_annotated_data():
    return readin_mirrors_data(get_mirrors_com_det_annotated_file())

#
# TO DO:
# - ensure that the mirrors data is consistent for each type: com_det, naive, schuessler
def readin_mirrors_data(filename):
    #return '' # debug only --remove
    raw_data = readlines_of_utf8_file(filename)
    retval = {}
    for rd in raw_data:
        poem_num = rd.split('.')
        if len(poem_num) <= 4:
            poem_num = poem_num[1]
        else:
            continue
        poem_num = poem_num.split(':')#[0])
        poem_only = poem_num[1]
        if rd.split():
            poem = rd#
        else:
            continue
        poem_num = int(poem_num[0])
#        if poem.strip():
#            print('poem_num = ' + str(poem_num) + ': ' + poem)
        if poem_num not in retval:
            retval[poem_num] = []
        if poem_only.strip():
            retval[poem_num].append(poem)
    return retval

def readin_stelae_naively_annotated_data():
    return readin_stelae_data(get_stelae_naively_annotated_file())

def readin_stelae_schuessler_annotated_data():
    return readin_stelae_data(get_stelae_schuessler_annotated_file())

def readin_stelae_com_det_annotated_data():
    return readin_stelae_data(get_stelae_com_det_annotated_file())

#
#
# TO DO:
#   Unify the output of the annotators; they aren't the same and it's trashing everything
#
def readin_stelae_data(filename):
    raw_data = readlines_of_utf8_file(filename)
    retval = {}
    for rd in raw_data:
        poem_num = rd.split('.')
        if len(poem_num) >= 2:
            poem_num = int(poem_num[1])
        else:
            continue
        poem_only = rd.split('： ')
        try:
            poem_only = poem_only[1]
        except IndexError as ie:
            x = 1
        if rd.split():
            poem = rd#
        else:
            continue
        #poem_num = int(poem_num[0])
        if poem_num not in retval:
            retval[poem_num] = []
        if poem_only.strip():
            retval[poem_num].append(poem)
    return retval

#
# TO DO:
# 1) fix the 'prev' 'next' buttons: Lu1983 data goes from 1 - 541.
#    PROBLEM: When you hit 'prev' at 1, it goes back to 539

def readin_received_shi_data(filename):
    raw_data = readlines_of_utf8_file(filename)
    #Lu1983.001.1.1： 大風起兮雲飛揚。
    #Lu1983.001.1.2： 威加海內兮歸故a鄉。
    #Lu1983.001.1.3： 安得猛士兮守四方。
    #Lu1983.002.1.1： 鴻鵠高飛。
    #Lu1983.002.1.2： 一舉千a里。
    #Lu1983.002.1.3： 羽翼就。
    #Lu1983.002.1.4： 橫絕四a海。
    retval = {}
    for rd in raw_data:
        poem_num = int(rd.split('.')[1])
        if poem_num not in retval:
            retval[poem_num] = []
        retval[poem_num].append(rd)
    return retval

#def readin_received_shi_schuessler_annotated_data():
#    return readlines_of_utf8_file(get_received_shi_schuessler_annotated_file())
# data_type
#    the type of physical medium the poetry comes from
#    received_shi
#    mirrors
#    stelae
# annotation_type
#    the type of analysis done on the data
#    naive
#    com_det
#    schuessler
class poem_array:
#    def __init__(self, annotation_type, data_type):
#        self.set_data(annotation_type,data_type)
    def __init__(self):
        self.zero_out_data()

    def zero_out_data(self):
        self.annotation_type = ''
        self.data_type = ''
        self.poem_array = {}
        self.indicies = []
        self.current_poem = 1

    def is_data_empty(self):
        retval = False
        if not self.poem_array:
            retval = True
        return retval

    def set_data(self, annotation_type, data_type):
        self.zero_out_data()
        self.annotation_type = annotation_type
        self.data_type = data_type
        if annotation_type == 'naive':
            if 'received_shi' in data_type:
                self.poem_array = readin_received_shi_naively_annotated_data()
            elif 'mirrors' in data_type:
                self.poem_array = readin_mirrors_naively_annotated_data()
            elif 'stelae' in data_type:
                self.poem_array = readin_stelae_naively_annotated_data()
        elif annotation_type == 'schuessler':
            if 'received_shi' in data_type:
                self.poem_array = readin_received_shi_schuessler_annotated_data()
            elif 'mirrors' in data_type:
                self.poem_array = readin_mirrors_schuessler_annotated_data()
            elif 'stelae' in data_type:
                self.poem_array = readin_stelae_schuessler_annotated_data()
        elif annotation_type == 'com_det':
            if 'received_shi' in data_type:
                self.poem_array = readin_received_shi_com_det_annotated_data()
            elif 'mirrors' in data_type:
                self.poem_array = readin_mirrors_com_det_annotated_data()
            elif 'stelae' in data_type:
                self.poem_array = readin_stelae_com_det_annotated_data()

        self.indicies = list(self.poem_array.keys())# contiguous
        self.current_poem = self.indicies[0]

    def increment_to_next_poem(self):
        current_ind = self.indicies.index(self.current_poem)
        if current_ind == len(self.indicies) - 1:  # if this is the highest index
            self.current_poem = self.indicies[0]  # then wrap back to beginning of poems
        elif current_ind < len(self.indicies) - 1:  #
            self.current_poem = self.indicies[current_ind + 1]

    def get_next_poem(self):
        self.increment_to_next_poem()
        return self.get_current_poem()

    def decrement_to_prev_poem(self):
        current_ind = self.indicies.index(self.current_poem)
        if current_ind == 0:  # if this is the lowest index
            self.current_poem = self.indicies[len(self.indicies) - 1]  # then wrap to last poem (one with highest index)
        elif current_ind > 0:
            self.current_poem = self.indicies[current_ind - 1]

    def get_prev_poem(self):
        self.decrement_to_prev_poem()
        return self.get_current_poem()

    def get_current_poem(self):
        retval = ''
        if self.current_poem in self.indicies:
            retval = self.poem_array[self.current_poem]
        return retval

    def is_poem_number_in_array(self, poem_num):
        retval = False
        if poem_num in self.indicies:
            retval = True
        return retval

    def get_poem_num(self, poem_num):
        retval = ''
        if self.is_poem_number_in_array(poem_num):
            poem_ind = self.indicies.index(poem_num)
            retval = self.poem_array[poem_ind]
        return retval

class poem_data:
    def __init__(self, data_type):
        self.data_type = data_type
        self.reset()

    def reset(self):
        self.do_print_msg = True
        self.class_name = 'poem_data'
        self.schuessler = poem_array()
        self.naive = poem_array()
        self.com_det = poem_array()
        #self.stelae_indicies = []
        #self.current_poem = 1

    def new_data_type(self, data_type):
        self.reset()
        self.data_type = data_type
        self.naive.set_data('naive', data_type)
        self.com_det.set_data('com_det', data_type)
        self.schuessler.set_data('schuessler')
    def get_total_num_poems(self):
        retval = 0
        if self.naive:
            retval = len(self.naive)
        elif self.schuessler:
            retval = len(self.schuessler)
        elif self.com_det:
            retval = len(self.com_det)
        return retval

    def increment_to_next_poem(self):
        if self.naive:
            self.naive.increment_to_next_poem()
        if self.com_det:
            self.com_det.increment_to_next_poem()
        if self.schuessler:
            self.schuessler.increment_to_next_poem()

        #total_num = self.get_total_num_poems()
        #if total_num > 0:
        #    if self.current_poem + 1 <= total_num:
        #        self.current_poem += 1
        #    else:
        #        self.current_poem = 1

    # self.current_poem refers to realworld data, so it goes from 1 -> N
    # the poem dictionaries also go from 1 -> N
    def decrement_to_prev_poem(self):
        if self.naive:
            self.naive.decrement_to_prev_poem()
        if self.com_det:
            self.com_det.decrement_to_prev_poem()
        if self.schuessler:
            self.schuessler.decrement_to_prev_poem()


        #total_num = self.get_total_num_poems() # should be N-1 (since the poem dictionaries start at 1)
        #if total_num > 0:
        #    if 'stelae' in self.data_type: # goes from 0 to N-1
        #        if self.current_poem - 1 < 0:
        #            self.current_poem = total_num
        #        else:
        #            self.current_poem -= 1
        #    else: # normal case
        #        if self.current_poem == 1:
        #            self.current_poem = total_num
        #        else:
        #            self.current_poem -= 1

    def get_current_naive_poem(self):
        funct_name = 'get_current_naive_poem()'
        retval = []
        if self.naive.is_data_empty():
            self.naive.set_data('naive', self.data_type)
        retval = self.naive.get_current_poem()

            #if 'received_shi' in self.data_type:
            #    self.naive = readin_received_shi_naively_annotated_data()
            #elif 'mirrors' in self.data_type:
            #    self.naive = readin_mirrors_naively_annotated_data()
            #elif 'stelae' in self.data_type:
            #    self.naive = readin_stelae_naively_annotated_data()
            #    self.stelae_indicies = list(self.naive.keys())
            #else:
            #    origin = self.class_name + '::' + funct_name
            #    debug_msg('Unsupported data type: ' + self.data_type, origin, self.do_print_msg)
        #if 'stelae' in self.data_type:
        #    if self.current_poem < len(self.stelae_indicies):
        #        retval = self.naive[self.stelae_indicies[self.current_poem]]
        #elif self.current_poem in self.naive:
        #    retval = self.naive[self.current_poem]

        return retval

    def get_current_com_det_poem(self):
        funct_name = 'get_current_com_det_poem()'
        retval = []
        if self.com_det.is_data_empty():
            self.com_det.set_data('com_det', self.data_type)
        retval = self.com_det.get_current_poem()

            #if 'received_shi' in self.data_type:
            #    self.com_det = readin_received_shi_com_det_annotated_data()

            #elif 'mirrors' in self.data_type:
            #    self.com_det = readin_mirrors_com_det_annotated_data()
            #elif 'stelae' in self.data_type:
            #    self.com_det = readin_stelae_com_det_annotated_data()
            #else:
            #    origin = self.class_name + '::' + funct_name
            #    debug_msg('Unsupported data type: ' + self.data_type, origin, self.do_print_msg)

        #if 'stelae' in self.data_type:
        #    if self.current_poem < len(self.stelae_indicies):
        #        retval = self.com_det[self.stelae_indicies[self.current_poem]]
        #elif self.current_poem in self.com_det:
        #    retval = self.com_det[self.current_poem]

        return retval

    def get_current_schuessler_poem(self):
        funct_name = 'get_current_schuessler_poem()'
        retval = []
        if self.schuessler.is_data_empty():
            self.schuessler.set_data('schuessler', self.data_type)
        retval = self.schuessler.get_current_poem()

        #if not self.schuessler:
        #    if 'received_shi' in self.data_type:
        #        self.schuessler = readin_received_shi_schuessler_annotated_data()
        #    elif 'mirrors' in self.data_type:
        #        self.schuessler = readin_mirrors_schuessler_annotated_data()
        #    elif 'stelae' in self.data_type:
        #        self.schuessler = readin_stelae_schuessler_annotated_data()
        #        return []
        #        #self.stelae_indicies = list(self.schuessler.keys())
        #    else:
        #        origin = self.class_name + '::' + funct_name
        #        debug_msg('Unsupported data type: ' + self.data_type, origin, self.do_print_msg)
        #if 'stelae' in self.data_type:
        #    if self.current_poem < len(self.stelae_indicies):
        #        retval = self.schuessler[self.stelae_indicies[self.current_poem]]
        #elif self.current_poem in self.schuessler:
        #    retval = self.schuessler[self.current_poem]

        return retval

class state_memory:
    def __init__(self, filename):
        self.file = filename

    def remember_state(self, state):
        delete_file_if_it_exists(self.file)
        append_line_to_output_file(self.file, state)

    def recall_state(self):
        return readlines_of_utf8_file(self.file)[0]


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        ui_file = os.path.join(get_hanproj_dir(), 'annotator_comparison', 'annotator_comparison2.ui')
        if not file_does_exist(ui_file):
            debug_msg('ERROR: bad filename - ' + ui_file, 'Ui::__init__()', self.print_debug_msgs)
            return
        uic.loadUi(ui_file, self)
        self.class_name = 'Ui'
        self.print_debug_msgs = True
        self.do_print_debug_msg = True
        self.data_type_gb_memory = state_memory(self.get_data_type_gb_memory_filename())
        radio_button_name = self.data_type_gb_memory.recall_state()
        if not radio_button_name:
            radio_button_name = 'received_shi_rb'
        self.set_data_type_gb_rb_as_checked(radio_button_name)

        self.initialize_data_type_gb_connect_functions()
#        self.initialize_data_type_gb()
        self.p_data = poem_data(self.data_type_gb_memory.recall_state())
        self.initialize_buttons()
        self.load_current_poem()

        self.show()

    def get_data_type_gb_memory_filename(self):
        return os.path.join(get_hanproj_dir(), 'annotator_comparison', 'data_type_gb_memory.txt')

    def set_data_type_gb_rb_as_checked(self, rb_name):
        funct_name = 'set_data_type_gb_rb_as_checked()'
        if rb_name == 'received_shi_rb':
            self.received_shi_rb.setChecked(True)#x = 1
        elif rb_name == 'stelae_rb':
            self.stelae_rb.setChecked(True)
        elif rb_name == 'mirrors_rb':
            self.mirrors_rb.setChecked(True)
        else:
            msg = ' 尷尬 ERROR: rb_name should not be ' + rb_name + '!'
            origin = self.class_name + '::' + funct_name
            debug_msg(msg, origin, self.do_print_debug_msg)
        self.data_type_gb_memory.remember_state(rb_name)

    def next_button_push(self):
        self.p_data.increment_to_next_poem()
        self.load_current_poem()

    def prev_button_push(self):
#        debug_msg('prev_button_push() used, but not yet defined', 'prev_button_push', True)
        self.p_data.decrement_to_prev_poem()
        self.load_current_poem()

    def initialize_buttons(self):
        self.prev_button.clicked.connect(self.prev_button_push)
        self.next_button.clicked.connect(self.next_button_push)

    def initialize_data_type_gb_connect_functions(self):
        self.received_shi_rb.toggled.connect(self.on_selected)
        self.stelae_rb.toggled.connect(self.on_selected)
        self.mirrors_rb.toggled.connect(self.on_selected)

    def get_current_data_type(self):
        return self.data_type_gb_memory.recall_state()

    def on_selected(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            self.print_debug_msg("You have selected : " + radio_button.text())
            name = radio_button.objectName()
            self.data_type_gb_memory.remember_state(name)
            self.p_data.new_data_type(name)
            self.load_current_poem()

    def print_debug_msg(self, msg):
        self.textEdit.setText(msg)

    # data_type = 'naive', 'com_det' or 'schuessler'
    def get_rhyme_groups_from_poem(self, poem, line_delim='\n'):
        funct_name ='get_rhyme_groups_from_poem()'
        return get_rhyme_groups_from_annotated_poem(poem, line_delim)

    def load_current_poem(self):
        n_current_poem = self.p_data.get_current_naive_poem()
        #self.naive_annotator_te.setText('\n'.join(n_current_poem))
        self.add_poem_to_textEdit('\n'.join(n_current_poem), 'naive')
        n_marker2rw_list = self.get_rhyme_groups_from_poem('\n'.join(n_current_poem))

        cd_current_poem = self.p_data.get_current_com_det_poem()
        #self.com_det_annotator_te.setText('\n'.join(cd_current_poem))
        self.add_poem_to_textEdit('\n'.join(cd_current_poem), 'com_det')
        cd_marker2rw_list = self.get_rhyme_groups_from_poem('\n'.join(cd_current_poem))

        s_current_poem = self.p_data.get_current_schuessler_poem()#readin_received_shi_schuessler_annotated_data()
        #self.schuessler_annotator_te.setText('\n'.join(s_current_poem))
        self.add_poem_to_textEdit('\n'.join(s_current_poem), 'schuessler')
        s_marker2rw_list = self.get_rhyme_groups_from_poem('\n'.join(s_current_poem))

        n2cd_similarity = self.get_percentage_similarity_to_naive_annotator(cd_marker2rw_list, len(n_marker2rw_list['a']))
        n2s_similarity = self.get_percentage_similarity_to_naive_annotator(s_marker2rw_list, len(n_marker2rw_list['a']))
        self.update_n2s_tb(n2s_similarity)
        self.update_n2c_tb(n2cd_similarity)

    def update_n2s_tb(self, content):
        self.n2s_tb.clear()
        if content.strip():
            self.n2s_tb.setText(content)

    def update_n2c_tb(self, content):
        self.n2c_tb.clear()
        if content.strip():
            self.n2c_tb.setText(content)

    def update_s2c_tb(self, content):
        self.s2c_tb.clear()
        if content.strip():
            self.s2c_tb.setText(content)
    #
    # purpose:
    #   to calculate the % similarity to the naive annotator for the schuessler and com det annotators
    # INPUT:
    #   marker2rw_list is a dictionary where key = rhyme group marker, value = rhyme word list for that marker
    def get_percentage_similarity_to_naive_annotator(self, marker2rw_list, num_naive_rhymes):
        funct_name = 'get_percentage_similarity_to_naive_annotator()'
        #
        # Step 1: find the marker with the most rhyme words
        max_num_rws = -1
        marker_with_max = ''
        for m in marker2rw_list:
            if len(marker2rw_list[m]) > max_num_rws:
                max_num_rws = len(marker2rw_list[m])
                marker_with_max = m

        # Step 2: Calculate % similarity
        return str(int(round(100.0*float(max_num_rws)/float(num_naive_rhymes))))

    def add_poem_to_textEdit(self, poem, annotator_type):
        red_color = QColor(255, 0, 0)
        black_color = QColor(0, 0, 0)
        annotator = ''
        if annotator_type == 'naive':
            annotator = self.naive_annotator_te
        elif annotator_type == 'com_det':
            annotator = self.com_det_annotator_te
        elif annotator_type == 'schuessler':
            annotator = self.schuessler_annotator_te
        annotator.setText('')
        color = black_color
        poem = poem.split('\n')
        for line in poem: # line = 'Lu1983.016.1.2： 驂駕駟馬從梁α來'
            line = line.split('： ')
            left_side = line[0] # 'Lu1983.016.1.2： '
            annotator.setTextColor(black_color)
            annotator.insertPlainText(left_side)
            color_added = get_colors_for_poem_line(line[1])
            for ca in color_added:
                if ca[1] == 'red':
                    color = red_color
                elif ca[1] == 'black':
                    color = black_color
                annotator.setTextColor(color)
                annotator.insertPlainText(ca[0])
            annotator.insertPlainText('\n')

def trash_test_function():
    x = '總領從官柏梁a台' #'總a領從官柏梁κc台'
    colors = get_colors_for_poem_line(x)
    print('INPUT: ' + x)
    print('OUTPUT: ')
    for sect in colors:
        print(sect[1] + ': ' + sect[0])

def get_colors_for_poem_line(line, is_verbose=False):
    black_text = ''
    red_text = ''
    color_change = False
    retval = []
    black_text = []
    red_text = []
    prev_color = ''
    current_color = ''
    punctuation = ['。', '、', '，']
    for inc in range(0, len(line), 1):
#        print('(' + str(inc) + ') ' + line[inc])
        if is_hanzi(line[inc]) or line[inc] in punctuation:
            if not prev_color:
                prev_color = 'black'
            current_color = 'black'
            black_text.append(line[inc])
            if current_color != prev_color:
                if red_text:
                    retval.append((''.join(red_text), 'red'))
                    red_text = []
                prev_color = 'black'
        else:
            if not prev_color:
                prev_color = 'red'
            current_color = 'red'
            red_text.append(line[inc])
            if current_color != prev_color:
                if black_text:
                    retval.append((''.join(black_text), 'black'))
                    black_text = []
                prev_color = 'red'
        if inc == len(line) - 1:
            if black_text:
                retval.append((''.join(black_text), 'black'))
                black_text = []
            if red_text:
                retval.append((''.join(red_text), 'red'))
                red_text = []
    if is_verbose:
        print('INPUT: ' + line)
        print('OUTPUT: ')
        for sect in retval:
            print(sect[1] + ': ' + sect[0])

    return retval

#
# NOTE:
# this needs to be changed, but it the code that writes out the files need to be changed first.
# Write a function that takes annotator_type and data_type as input, and returns the filename:
#  {annotator_type}_annotated_{data_type}_poem_data.txt
an_poem2filename = {}
an_poem2filename['received_shi'] = {'naive':'naively_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt',
                            'schuessler':'schuessler_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt',
                            'com_det':'com_det_annotated_received-shi_data.txt'}
                            #'com_det':'com_det_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt'}
an_poem2filename['mirrors'] =  {'naive':'naively_annotated_kyomeishusei2015_han_mirror_data.txt',
                       'schuessler':'schuessler_annotated_kyomeishusei2015_han_mirror_data.txt',
                        'com_det':'com_det_annotated_mirrors_data.txt'}
                       #'com_det':'com_det_annotated_kyomeishusei2015_han_mirror_data.txt'}
an_poem2filename['stelae'] = {'naive':'naively_annotated_毛遠明 《漢魏六朝碑刻校注》.txt',
                      'schuessler':'schuessler_annotated_毛遠明 《漢魏六朝碑刻校注》.txt',#
                      'com_det':'com_det_annotated_stelae_data.txt'}
                      #'com_det':'com_det_annotated_毛遠明 《漢魏六朝碑刻校注》.txt'}
def get_annotated_poem_data_filename(annotator_type, data_type):
    funct_name = 'get_annotated_poem_data_filename()'
    retval = ''
    try:
        data_dir = data_type
        if data_type == 'received_shi':
            data_dir = data_dir.replace('_', '-')
        retval = os.path.join(get_hanproj_dir(), data_dir, an_poem2filename[data_type][annotator_type])
    except:
        x = 1
    return retval
# naively_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt
# schuessler_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt
# com_det_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt
def readin_annotated_poem_data(annotator_type, data_type):
    funct_name = 'readin_annotator_data()'
    retval = {}
    filename = get_annotated_poem_data_filename(annotator_type, data_type)
    if not if_file_exists(filename, funct_name):
        return retval
    data = readlines_of_utf8_file(filename)
    for d in data:
        #print(d)
        #continue
        splitter = ''
        if '：' in d:
            splitter = '： '
        elif ':' in d:
            splitter = ': '
        try:
            d = d.split(splitter)
        except ValueError:
            x = 1
        try:
            retval[d[0]] = d[1]
        except IndexError as ie:
            x = 1
    return retval

def test_readin_annotated_poem_data():
    funct_name = 'test_readin_annotated_poem_data()'
    #data = readin_annotated_poem_data('naive', 'received_shi')
    #data = readin_annotated_poem_data('schuessler', 'received_shi')
    data = readin_annotated_poem_data('com_det', 'received_shi')
    for k in data:
        print(k + '= ' + data[k])
    print(str(len(data)) + ' elements.')

def test_compare_data_sets():
    funct_name = 'test_compare_data_sets()'
    data_type = 'stelae' #'stelae'#'received_shi'
    compare_annotation_between_different_annotators(data_type)

def get_poem_base_id2poem_content_dict(poem_id2poem_line_d):
    funct_name = 'get_poem_base_id2poem_content_dict()'
    base_id = ''
    prev_base_id = ''
    poem = []
    data = poem_id2poem_line_d
    retval = {}
    for poem_id in data:
        poem_line = data[poem_id]
        poem_id = poem_id.split('.')
        base_id = poem_id[0] + '.' + poem_id[1]
        if base_id == prev_base_id:  # if we are still in the same poem
            poem.append(poem_line)
        else:  # we are entering a new poem
            # print previous poem
            #print(prev_base_id + ':\n\t' + '\n\t'.join(poem))
            if prev_base_id:
                retval[prev_base_id] = '\n'.join(poem)
            #print('*-' * 20)
            prev_base_id = base_id
            poem = []
            poem.append(poem_line)
    # grab the last item
    retval[prev_base_id] = '\n'.join(poem)
    #print('*-' * 20)
    return retval

def renumber_poems(data, data_type):
    if data_type == 'mirrors' or data_type == 'stelae':
        temp_d = {}
        for poem_id in data:
            new_poem_id = poem_id.split('.')
            new_poem_id = new_poem_id[0] + '.' + new_poem_id[1]
            if new_poem_id not in temp_d:
                temp_d[new_poem_id] = ''
            temp_d[new_poem_id] += data[poem_id]
        return temp_d
    return data

def compare_annotation_between_different_annotators(data_type):
    funct_name = 'compare_annotation_between_different_annotators()'
    n_data = readin_annotated_poem_data('naive', data_type)
    s_data = readin_annotated_poem_data('schuessler', data_type)
    cd_data = readin_annotated_poem_data('com_det', data_type)

    if data_type == 'received_shi':
        n_data = get_poem_base_id2poem_content_dict(n_data) # id2poem_d
        s_data = get_poem_base_id2poem_content_dict(s_data) # id2poem_d
        cd_data = get_poem_base_id2poem_content_dict(cd_data) # id2poem_d
        data_type4file = 'received-shi'
    else:
        data_type4file = data_type

    output_file = os.path.join(get_hanproj_dir(), data_type4file, 'annotator_comparison_for_' + data_type + '.txt')
    delete_file_if_it_exists(output_file)
    n_equal_s = False
    n_equal_cd = False
    s_equal_cd = False
    not_equal = '≠'
    delim = '\t'
    num_rhymes2data_d = {}
    result2num_instances_d = {}
    result2poem_id = {}
    r2n_index = ''
    no_rhymes = []
    s_data = renumber_poems(s_data, data_type)
    n_data = renumber_poems(n_data, data_type)
    cd_data = renumber_poems(cd_data, data_type)
    irregular_poems = []
    poem_line_delim = '。'
    for poem_id in s_data:
        s_poem_content = s_data[poem_id]
        if '。' not in s_poem_content:
            x = 1
        else:
            x = 1
        if '00058' in poem_id:
            x = 1
        if 'Mou2008.118.1.3' in poem_id:
            x = 1
        if '01925' in poem_id:
            x = 1
        # get_rhyme_groups_from_annotated_poem() # per poem; input = poem content; returns: dict[marker] = [rw words]
        s_m2rw_words_d = get_rhyme_groups_from_annotated_poem(s_poem_content, poem_line_delim)
        n_poem_content = n_data[poem_id]
        n_m2rw_words_d = get_rhyme_groups_from_annotated_poem(n_poem_content, poem_line_delim)
        cd_poem_content = cd_data[poem_id]
        cd_m2rw_words_d = get_rhyme_groups_from_annotated_poem(cd_poem_content, poem_line_delim)
        if not n_m2rw_words_d:
            line_out = 'N/A\tN/A\tN/A\t0'
            no_rhymes.append(poem_id)
            continue
        try:
            num_naive_rhymes = len(n_m2rw_words_d['a'])
        except KeyError as ke:
            x = 1
            irregular_poems.append(poem_id)
            continue
        s2n_percent = get_percentage_similarity_to_naive_annotator(s_m2rw_words_d, num_naive_rhymes)  # per poem
        cd2n_percent = get_percentage_similarity_to_naive_annotator(cd_m2rw_words_d, num_naive_rhymes)
        line_out = poem_id + delim
        if s2n_percent == '100':
            #n_equal_s = True
            line_out += 'N=S' + delim
            r2n_index += 'N=S; '
        else:
            line_out += 'N≠S (' + s2n_percent + ')' + delim
            r2n_index += 'N≠S; '
        if cd2n_percent == '100':
            line_out += 'N=C' + delim
            r2n_index += 'N=C; '
        else:
            line_out += 'N≠C (' + cd2n_percent + ')' + delim
            r2n_index += 'N≠C; '
        if s2n_percent == cd2n_percent:
            if s2n_percent == '100':
                line_out += 'S=C' + delim
                r2n_index += 'S=C; '
            else:
                s_equal_c = are_these_two_marker2rhyme_word_dictionaries_equal(s_m2rw_words_d, cd_m2rw_words_d)
                if s_equal_c:
                    line_out += 'S=C' + delim
                    r2n_index += 'S=C; '
                else:
                    line_out += 'S≠C' + delim
                    r2n_index += 'S≠C; '
        else:
            line_out += 'S≠C' + delim
            r2n_index += 'S≠C; '
        if r2n_index not in result2num_instances_d:
            result2num_instances_d[r2n_index] = []
        result2num_instances_d[r2n_index].append(num_naive_rhymes)

        if r2n_index not in result2poem_id:
            result2poem_id[r2n_index] = []
        result2poem_id[r2n_index].append(poem_id)
        r2n_index = ''
        line_out += str(num_naive_rhymes)
        if num_naive_rhymes not in num_rhymes2data_d:
            num_rhymes2data_d[num_naive_rhymes] = []
        num_rhymes2data_d[num_naive_rhymes].append(line_out)
        #print(poem_id + ': ' + line_out)
        max_k = -1
        for k in num_rhymes2data_d:
            if k > max_k:
                max_k = k
        #print('max_k=' + str(max_k))
    if 1:
        #for k in num_rhymes2data_d:
        for k in range(max_k, 1, -1):
            if k in num_rhymes2data_d:
                print('#Rhymes = ' + str(k))
                append_line_to_utf8_file(output_file, '#Rhymes = ' + str(k))
                for line in num_rhymes2data_d[k]:
                    print('\t' + line)
                    append_line_to_utf8_file(output_file, '\t' + line)
        print('*-' * 20)
        print('\t\tFor ' + data_type.capitalize() + ' data.')
        print('*-' * 20)
        for r2n_index in result2num_instances_d:
            msg = r2n_index + ' has ' + str(len(result2num_instances_d[r2n_index])) + ' instances, for a total of '
            msg += str(sum(result2num_instances_d[r2n_index])) + ' rhymes.'
            print(msg)
        print('*-' * 20)
        #result2poem_id[r2n_index].append(poem_id)
        for r2n_index in result2poem_id:
            msg = r2n_index + ' has ' + str(len(result2poem_id[r2n_index])) + ' poem_ids.'
            print(msg)
        print(str(len(no_rhymes)) + ' poems have no rhymes.')
        print('\t' + ', '.join(no_rhymes))
        print(str(len(irregular_poems)) + ' poems had irregularities and were not counted.')
        print('\t' + ', '.join(irregular_poems))
        #result2num_instances_d[r2n_index].append(num_naive_rhymes)

#
# Purpose:
#   given two dictionaries where key='marker', and value='rhyme words',
#   determine if they are the same or not.
#   SAME = if for each marker the group of rhyme words is exactly the same
#   DIFFERENT = not SAME
def are_these_two_marker2rhyme_word_dictionaries_equal(m2rw_a, m2rw_b):
    funct_name = 'are_these_two_marker2rhyme_word_dictionaries_equal()'
    retval = False
    # if the number of markers is different, then they are not the same
    if len(m2rw_a) != len(m2rw_b):
        return retval
    len2rw_a = convert_marker2rw_word_to_len2rw_word_dict(m2rw_a)
    len2rw_b = convert_marker2rw_word_to_len2rw_word_dict(m2rw_b)
    for num_rw in len2rw_a:
        try:
            list_of_rw_lists_a = len2rw_a[num_rw] # this is a list of lists
            list_of_rw_lists_b = len2rw_b[num_rw]
        except IndexError as ie:
            return retval
        except KeyError as ke:
            return retval
        if len(list_of_rw_lists_a) != len(list_of_rw_lists_b):
            return retval

        for rw_list_a in list_of_rw_lists_a:
            rw_list_a.sort()
            if rw_list_a not in list_of_rw_lists_b:
                return retval
    retval = True
    return retval

def test_print_out_poems_given_ids():
    funct_name = 'test_print_out_poems_given_ids()'
    data_type = 'received_shi' #Lu1983.539; 047
    print_out_poems_given_ids(data_type, ['Lu1983.047'])


if 0:
    #
    # INPUT: poem as single string (lines end in '\n')
    def is_poem_annotated(poem):
        return re.search(r'[a-zA-Zα-ωΑ-Ω]', poem)

    def does_line_have_rhyme_marker(line):
        return is_poem_annotated(line)

#
# INPUT: poem as single string (lines end in '\n')
# ASSUMPTION: if first line doesn't have a rhyme marker, then it's not in one_rhyme_per_line format
#             This assumption will be false if the first line really would have a rhyme, but it's not
#             marked due to an anomaly (like being a square -- i.e., unrecognizable character)
def is_poem_in_one_rhyme_per_line_format(poem):
    poem = poem.split('\n')
    return re.search(r'[a-zA-Zα-ωΑ-Ω]', poem[0])
#
# INPUT: poem as single string (lines end in '\n')
def format_poem_as_one_rhyme_per_line(poem):
    if not is_poem_annotated(poem):
        return poem # if there are no annotated rhymes, then there's no formatting to do
    if is_poem_in_one_rhyme_per_line_format(poem):
        return poem # if it's already in the desired format, then there's nothing to do
    inc = 0
    retval = []
    full_line = ''
    poem = poem.split('\n')
    for line in poem:
        inc += 1
        if not inc % 2:  # for even lines...
            full_line += line
            retval.append(full_line)
        else:  # for odd lines...
            full_line = line
    return '\n'.join(retval)

#
# INPUT: poem as single string (lines end in '\n')
# NOTE:
#   doesn't work on Schuessler Anntation. Would need to add
#   all of the extra letters in Schuessler's LHan
def remove_all_rhyme_markers_from_poem(annotated_poem):
    funct_name = 'remove_all_rhyme_markers_from_poem()'
    annotated_poem = annotated_poem.replace('(', '')
    annotated_poem = annotated_poem.replace(')', '')
    markers = re.findall(r'[a-zA-Zα-ωΑ-Ω]+', annotated_poem)
    markers = list(set(markers)) # get rid of dupes
    for m in markers:
        annotated_poem = annotated_poem.replace(m, '')
    return annotated_poem

def get_rhyme_markers_from_annotated_poem(annotated_poem):
    funct_name = 'get_rhyme_markers_from_annotated_poem()'
    poem = annotated_poem.split('\n')
    inc = 0
    retval = {}
    for line in poem:
        inc += 1
        result = re.search(r'[a-zA-Zα-ωΑ-Ω]+', line)
        start_pos = result.span()[0]
        stop_pos = result.span()[1]
        marker = line[start_pos:stop_pos]
        if inc not in retval:
            retval[inc] = ''
        retval[inc] = marker
    return retval

def get_lhan_from_schuessler_annotated_poem(annotated_poem):
    funct_name = 'get_lhan_from_schuessler_annotated_poem()'
    poem = annotated_poem.split('\n')
    inc = 0
    retval = {}
    for line in poem:
        inc += 1
        if '(' in line:
            lhan = line.split('(')[1]
            lhan = lhan.split(')')[0]
            if inc not in retval:
                retval[inc] = ''
            retval[inc] = lhan
    return retval

#
# INPUT: poem as single string (lines end in '\n')
def get_rhyme_words_from_naively_annotated_poem(annotated_poem):
    funct_name = 'get_rhyme_words_from_naively_annotated_poem()'
    poem = annotated_poem.split('\n')
    inc = 0
    retval = {}
    for line in poem:
        inc += 1
        if 'a' in line:
            line = line.split('a')[1]
            line = line[0:len(line)-1] # remove punctuation
            if len(line) > 1:
                for echar in exception_chars:
                    if echar in line:
                        line = line.replace(echar, '')
                        break
            if inc not in retval:
                retval[inc] = ''
            retval[inc] = line
    return retval

def print_out_poems_given_ids(data_type, poem_id_l):
    funct_name = 'print_out_poems_given_ids()'
    n_data = readin_annotated_poem_data('naive', data_type)
    s_data = readin_annotated_poem_data('schuessler', data_type)
    cd_data = readin_annotated_poem_data('com_det', data_type)
    rw2lhan_d = readin_most_complete_schuessler_data()
    if data_type == 'received_shi':
        n_data = get_poem_base_id2poem_content_dict(n_data) # id2poem_d
        s_data = get_poem_base_id2poem_content_dict(s_data) # id2poem_d
        cd_data = get_poem_base_id2poem_content_dict(cd_data) # id2poem_d

    n_equal_s = False
    n_equal_cd = False
    s_equal_cd = False
    not_equal = '≠'
    delim = '\t'
    num_rhymes2data_d = {}
    for poem_id in poem_id_l:
        #print(poem_id)
        #if '.084' in poem_id:
        #    x = 1
        s_poem_content = s_data[poem_id]
        # get_rhyme_groups_from_annotated_poem() # per poem; input = poem content; returns: dict[marker] = [rw words]
        s_m2rw_words_d = get_rhyme_groups_from_annotated_poem(s_poem_content)
        n_poem_content = n_data[poem_id]
        n_m2rw_words_d = get_rhyme_groups_from_annotated_poem(n_poem_content)
        cd_poem_content = cd_data[poem_id]
        cd_m2rw_words_d = get_rhyme_groups_from_annotated_poem(cd_poem_content)
        print('Naive Annotator:')
        n_poem_content = format_poem_as_one_rhyme_per_line(n_poem_content)
        s_poem_content = format_poem_as_one_rhyme_per_line(s_poem_content)
        cd_poem_content = format_poem_as_one_rhyme_per_line(cd_poem_content)
        deannotated = remove_all_rhyme_markers_from_poem(cd_poem_content)
        line_num2rw_d = get_rhyme_words_from_naively_annotated_poem(n_poem_content)
        phonological_data = ''
        for line_num in line_num2rw_d:
            rw = line_num2rw_d[line_num]
            phonological_data += '%' + rw + ': ' + ','.join(rw2lhan_d[rw]) + '\n'
        line_num2lhan_d = get_lhan_from_schuessler_annotated_poem(s_poem_content)
        line_num2s_m_d = get_rhyme_markers_from_annotated_poem(s_poem_content)
        line_num2cd_m_d = get_rhyme_markers_from_annotated_poem(cd_poem_content)
        if 1:
            print(n_poem_content)
            print('-' * 50)
            print('Schuessler Annotator:')
            print(s_poem_content)
            print('-' * 50)
            print('Com det Annotator:')
            print(cd_poem_content)
            print('-' * 50)
            print('Deannotated Com Det')
            print(deannotated)
        # table header
        labels = '\\textbf{Poem} & \\textbf{Rhyme Word} & \\textbf{LHan} & '
        labels += '\\textbf{\makecell[tl]{Schuessler\\\\Annotation}} & '
        labels += '\\textbf{\makecell[tl]{Community\\\\Annotation}}\\\\'
        table_header = ['% ' + poem_id,
                        '\\begin{table}[!ht]',
                        '\\begin{tabular}{ c c c c c}',
                        '\hline',
                        labels,
                        '\hline']
        print('\n')
        print('\n'.join(table_header))
        inc = 0
        deannotated = deannotated.split('\n')
        for line in deannotated:
            inc += 1
            cd_marker = line_num2cd_m_d[inc]
            s_marker = line_num2s_m_d[inc]
            rw = line_num2rw_d[inc]
            lhan = line_num2lhan_d[inc]
            msg = line + ' & ' + rw + ' & ' + lhan + ' & ' + s_marker + ' & ' + cd_marker + '\\\\'
            print(msg)
        table_footer = ['\hline', '\end{tabular}', '\end{table}']
        print('\n'.join(table_footer))
        print('\n')
        print(phonological_data)



def convert_marker2rw_word_to_len2rw_word_dict(m2rw_word_d):
    funct_name = 'convert_marker2rw_word_to_len2rw_word_dict()'
    retval = {}
    for m in m2rw_word_d:
        rw_list = m2rw_word_d[m]
        rw_list.sort()
        if len(rw_list) not in retval:
            retval[len(rw_list)] = []
        retval[len(rw_list)].append(rw_list)
    return retval

            #n_equal_cd = True

    #get_percentage_similarity_to_naive_annotator(marker2rw_list, num_naive_rhymes) # per poem

def investigate_stelae_data():
    data_type = 'stelae'
    n_data = readin_annotated_poem_data('naive', data_type)
    poems_in_data = []
    for n in n_data:
        print(n)
        n = n.split('.')
        poems_in_data.append(int(n[1]))
    print(str(len(list(set(poems_in_data)))) + ' poems in data.')


def investigate_mirror_data():
    data_type = 'mirrors'
    n_data = readin_annotated_poem_data('naive', data_type)
    poems_in_data = []
    for n in n_data:
        print(n)
        n = n.split('.')
        poems_in_data.append(int(n[1]))
    print(str(len(list(set(poems_in_data)))) + ' poems in data.')
    not_accounted_for = []
    not_accounted_for_str = []
    #for pid in poems_in_data:
    for inc in range(1,11817+1,1):
        if inc not in poems_in_data:
            not_accounted_for.append(inc)
            not_accounted_for_str.append(str(inc))
    for naf in not_accounted_for:
        print(str(naf))
    print(str(len(not_accounted_for)) + ' poems not accounted for.')
    print(', '.join(not_accounted_for_str))
# returns dictionary where:
#    key = rhyme group marker
#  value = list of rhyme words
#def get_rhyme_groups_from_annotated_poem(poem)
#n2s_similarity = self.get_percentage_similarity_to_naive_annotator(s_marker2rw_list, len(n_marker2rw_list['a']))

#
# purpose:
#   to calculate the % similarity to the naive annotator for the schuessler and com det annotators
# INPUT:
#   marker2rw_list is a dictionary where key = rhyme group marker, value = rhyme word list for that marker
def get_percentage_similarity_to_naive_annotator(marker2rw_list, num_naive_rhymes):
    funct_name = 'get_percentage_similarity_to_naive_annotator()'
    #
    # Step 1: find the marker with the most rhyme words
    max_num_rws = -1
    marker_with_max = ''
    for m in marker2rw_list:
        if len(marker2rw_list[m]) > max_num_rws:
            max_num_rws = len(marker2rw_list[m])
            marker_with_max = m

    # Step 2: Calculate % similarity
    return str(int(round(100.0*float(max_num_rws)/float(num_naive_rhymes))))

def annotate_possible_readings_for_poems():
    funct_name = 'annotate_possible_readings_for_poems()'
    s_data = readin_annotated_poem_data('com_det', 'stelae')
    rw2lhan_d = readin_most_complete_schuessler_data()
    poems_to_print = ['045', '060', '067', '133']
    for sd in s_data:
        tag = sd.split('.')[1]
        if does_line_have_rhyme_marker(s_data[sd]):
            rw, m = get_rhyme_word_and_marker_from_line_of_poem(s_data[sd])
            lhan = ''
            if rw in rw2lhan_d:
                lhan = rw2lhan_d[rw]
            if tag in poems_to_print:
                print(sd + ': ' + s_data[sd] + ' ' + ', '.join(lhan))
        else:
            if tag in poems_to_print:
                print(sd + ': ' + s_data[sd])
        #else:
        #    print(s_data[sd])

def remove_dupes_from_schuessler():
    funct_name = 'remove_dupes_from_schuessler()'
    rw2lhan_d = readin_most_complete_schuessler_data()
    entries_w_dupes = []
    for rw in rw2lhan_d:
        if len(rw2lhan_d[rw]) != len(list(set(rw2lhan_d[rw]))):
            print(rw + ': ' + ' '.join(rw2lhan_d[rw]))
            entries_w_dupes.append(rw)
    #print(str(len(entries_w_dupes)) + ' entries have dupes.')



run_gui = False
if run_gui:
    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        window = Ui()
        app.exec_()
else:
    if 0:
        test_compare_data_sets()
    #test_readin_annotated_poem_data()
    #test_print_out_poems_given_ids()

#remove_dupes_from_schuessler()
#annotate_possible_readings_for_poems()
#investigate_stelae_data()
#investigate_mirror_data()