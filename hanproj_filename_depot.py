#! C:\Python36\
# -*- encoding: utf-8 -*-

#
# PURPOSE:
# Anything related to input or output files for Hanproj belongs here, to keep everything in the same place

import os


class filename_depot:
    def __init__(self, is_verbose=False):
        self.class_name = 'filename_depot'
        #self.absolute_path = os.path.dirname(__file__)
        self.absolute_path = os.getcwd()
        #print(self.absolute_path) # on my machine: D:\Ash\SOAS\code\hanproj\hanproject
        if '\\' in self.absolute_path:
            self.dir_delim = '\\'
        elif '/' in self.absolute_path:
            self.dir_delim = '/'
        else:
            self.dir_delim = ''
            print('filename_depot: ERROR: unknown type of directory delimiter. Expect chaos!')

    def directory_tests(self):
        print('self.absolute_path: ' + self.absolute_path)
        print('self.get_hanproj_dir() returns ' + self.get_hanproj_dir())
        print('self.get_mirrors_dir() returns ' + self.get_mirrors_dir())
        print('self.get_stelae_dir() returns ' + self.get_stelae_dir())
        print('self.get_received_shi_dir() returns ' + self.get_stelae_dir())

    def get_hanproj_dir(self):
        base_path = self.absolute_path.split(self.dir_delim)
        return self.dir_delim.join(base_path[0:len(base_path)-1])

    def get_mirrors_dir(self):
        return os.path.join(self.get_hanproj_dir(), 'mirrors')

    def get_stelae_dir(self):
        return os.path.join(self.get_hanproj_dir(), 'stelae')

    def get_soas_data_dir(self): # this isn't going to work for the repository; need to move the data
        return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'data')

    def get_received_shi_dir(self):
        return os.path.join(self.get_hanproj_dir(), 'received-shi')

    def get_received_bronzes_dir(self):
        return os.path.join(self.get_hanproj_dir(), 'bronzes')

    def get_schuesslerhanchinese_dir(self): # this isn't going to work for the repository; need to move the data
        return os.path.join(self.get_soas_code_dir(), 'schuesslerhanchinese')

    def get_soas_code_dir(self): # this isn't going to work for the repository; need to move the data
        return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

    def get_parsed_mao_2008_stelae_data_file(self):
        return os.path.join(self.get_stelae_dir(), 'parsed_毛遠明 《漢魏六朝碑刻校注》.txt')

    def get_mao_2008_stelae_data_input_file1(self):
        base_dir = os.path.join(self.get_stelae_dir(), 'raw', 'txt')
        return os.path.join(base_dir, '毛遠明 《漢魏六朝碑刻校注》第一冊.txt')

    def get_mao_2008_stelae_data_input_file2(self):
        base_dir = os.path.join(self.get_stelae_dir(), 'raw', 'txt')
        return os.path.join(base_dir, '毛遠明 《漢魏六朝碑刻校注》第二冊.txt')

    def get_mao_2008_stelae_data_naive_annotator_output_file(self):
        return os.path.join(self.get_stelae_dir(), '毛遠明 《漢魏六朝碑刻校注》-naive-annotator.txt')

    def get_filename_for_combined_data_community_detection(self):
        return os.path.join(self.get_hanproj_dir(), 'combo', 'com_det_for_combined_data_output.txt')

    def get_phonological_data_dir(self):
        return os.path.join(self.get_hanproj_dir(), 'phonological_data')
    #
    # NOTE:
    #  for now using existing filenames. For the re-write, these will be standardized.
    #  -> similar to get_filename_for_annotated_network_data(self) below.
    def get_output_filename_for_poem_marking_annotation(self, data_type, annotator_type, test_mode=False):
        funct_name = 'get_output_filename_for_poem_marking_annotation()'
        retval = ''
        if data_type == 'received_shi':
            if annotator_type == 'naive':
                retval = os.path.join(self.get_received_shi_dir(), 'naively_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')
            elif annotator_type == 'schuessler':
                retval = os.path.join(self.get_received_shi_dir(), 'schuessler_annotated_Lu_1983_先秦漢魏晉南北朝詩.txt')
        elif data_type == 'stelae':
            if annotator_type == 'naive':
                retval = os.path.join(self.get_stelae_dir(), 'naively_annotated_毛遠明 《漢魏六朝碑刻校注》.txt')
            elif annotator_type == 'schuessler':
                retval = os.path.join(self.get_stelae_dir(), 'schuessler_annotated_毛遠明 《漢魏六朝碑刻校注》.txt')
        elif data_type == 'mirrors':
            if annotator_type == 'naive':
                retval = os.path.join(self.get_mirrors_dir(), 'naively_annotated_kyomeishusei2015_han_mirror_data.txt')
            elif annotator_type == 'schuessler':
                retval = os.path.join(self.get_mirrors_dir(), 'schuessler_annotated_kyomeishusei2015_han_mirror_data.txt')
        if test_mode:
            retval = retval.replace('.txt', '_test_mode.txt')
        return retval

    #rnet_filename = os.path.join(get_hanproj_dir(), 'received-shi', 'received_shi_pre_com_det_rnetwork.txt')
    #
    # This is for networks (network_type = 'graph' or 'network')
    def get_filename_for_annotated_network_data(self, network_type, annotator_type, data_type):
        funct_name = 'get_filename_for_annotated_network_data()'
        data_type = self.modify_data_type_for_filename(data_type)
        filename = annotator_type + '_annotated_' + data_type + '_' + network_type + '_data.txt'
        return os.path.join(self.get_hanproj_dir(), data_type, filename)

    def get_filename_for_com_det_network_data(self, network_type, annotator_type, data_type):
        funct_name = 'get_filename_for_com_det_network_data()'
        data_type = self.modify_data_type_for_filename(data_type)
        filename = 'com_det_' + annotator_type + '_annotated_' + data_type + '_' + network_type + '_data.txt'
        return os.path.join(self.get_hanproj_dir(), data_type, filename)

    def get_filename_for_temp_naively_annotated_data(self, data_type):
        data_type = self.modify_data_type_for_filename(data_type)
        return os.path.join(self.get_hanproj_dir(), data_type, 'temp_naive_annotated_' + data_type + '_data.txt')

    def modify_data_type_for_filename(self, data_type):
        if data_type == 'received_shi':
            data_type = 'received-shi'
        return data_type

    #'node_id2cluster_no.txt'
    def get_filename_for_node_id2cluster_no(self):
        return 'node_id2cluster_no.txt'
    # This is for annotating poems
    def get_output_filename_for_annotated_poems(self, annotator_type, data_type):
        #'naively_annotated_kyomeishusei2015_han_mirror_data.txt'
        data_type = self.modify_data_type_for_filename(data_type)
        filename = annotator_type + '_annotated_' + data_type + '_data.txt'
        return os.path.join(self.get_hanproj_dir(), data_type, filename)

def quick_test():
    filename_storage = filename_depot()
    filename_storage.directory_tests()

#quick_test()