#! C:\Python36\
# -*- encoding: utf-8 -*-

import os
import copy
import llist
from llist import sllist,sllistnode
#import pygtrie
from anytree import Node, RenderTree, PreOrderIter, AsciiStyle

#from msvcrt import getch
utf8_bom_b = b'\xef\xbb\xbf'
from timeit import default_timer as timer
from datetime import timedelta
#test_data = {'深':['tśʰim', 'śim', 'śimᶜ'], '賢':['śimᴮ'], '神':['źin', 'hioŋ']}

#葚	dźimᴮ źimᴮ
def get_hanproj_dir():
    return os.path.join(get_soas_code_dir(), 'hanproj')

def get_hanproject_dir():
    return os.path.join(get_hanproj_dir(), 'hanproject')

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

class tree_node:
    def __init__(self, unique_id):
        self.clear()
        self.set_unique_id(unique_id)
        #self.set_zi(zi)
        #self.set_fayin(fayin)

    def set_unique_id(self, unique_id):
        self.unique_id = unique_id

    def get_unique_id(self):
        return self.unique_id

    def clear(self):
        #self.zi = None
        #self.fayin = None
        self.unique_id = None
        self.left_child = None
        self.left_sibling = None
        self.right_sibling = None
        self.parent_node = None

    def dump_node(self):
        msg = '-'*50 + '\n'
        msg += self.get_zi() + ': ' + self.get_fayin() + '\n'
        msg += '-'*50 + '\n'
        msg += '\tunique_id = ' + self.unique_id + '\n'
        msg += '\tleft_child = ' + str(self.get_left_child()) + '\n'
        msg += '\tleft_sibling = ' + str(self.get_left_sibling()) + '\n'
        msg += '\tright_sibling = ' + str(self.get_right_sibling()) + '\n'
        msg += '\tparent_node = ' + str(self.get_parent()) + '\n'
        msg += '-'*50 + '\n'
        return msg

    def reset_node(self, unique_id):
        self.clear()
        self.set_unique_id(unique_id)
        #self.set_zi(zi)
        #self.set_fayin(fayin)

    #def set_zi(self, zi):
    #    self.zi = zi

    #def set_fayin(self, fayin):
    #    self.fayin = fayin

    def set_left_child(self, child_node_unique_id):
        self.left_child = child_node_unique_id

    def set_right_sibling(self, sibling_node_unique_id):
        self.right_sibling = sibling_node_unique_id

    def set_left_sibling(self, sibling_node_unique_id):
        self.left_sibling = sibling_node_unique_id

    def set_parent(self, parent_node_unique_id):
        self.parent_node = parent_node_unique_id

    def get_zi(self):
        return self.unique_id.split(' ')[1]

    def get_fayin(self):
        return self.unique_id.split(' ')[2]

    def get_left_child(self):
        return self.left_child

    def get_right_sibling(self):
        return self.right_sibling

    def get_left_sibling(self):
        return self.left_sibling

    def get_parent(self):
        return self.parent_node

class fy_tree3:
    def __init__(self, data_d, run_debug=False):
        self.data_d = {key: value[:] for key, value in data_d.items()}
        self.current_node_key = None
        self.current_value = None

        self.node_inc = 0
        self.tree_d = {}
        self.root_key = '0 root_key root_value'
        self.node_storage = []
        self.temp_node = tree_node('')
        self.calculate_paths(run_debug)

    def calculate_paths(self, run_debug=False):
        if run_debug:
            start_time = timer()
        #
        # Add Root node
        #self.temp_node.set_unique_id(self.root_key)
        prev_node_key = self.root_key
        #self.node_storage.append(copy.deepcopy(self.temp_node))
        self.current_node_inc = 0
        self.paths_l = []
        temp_paths_l = []
        code_paths_traversed = []
        for zi in self.data_d:
            fayin_l = self.data_d[zi]  # data is like this: {'深': ['tśʰim', 'śim', 'śimᶜ'], '賢': ['śimᴮ'], '神': ['źin', 'hioŋ']}
            if not fayin_l:
                print('ERROR: ' + zi + ' is missing LHan!')
            num_sibs_this_depth = len(fayin_l)
            sib_inc = 0
            #code_paths_traversed = []
            for fy in fayin_l:
                self.current_node_inc += 1
                current_node_key = self.get_unique_key(self.current_node_inc, zi, fy)
                if prev_node_key == self.root_key:# path 1
                    self.paths_l.append([current_node_key])
                    if run_debug:
                        code_paths_traversed.append('if prev_node_key == self.root_key:# path 1')
                if num_sibs_this_depth == 1 and prev_node_key != self.root_key: # path 2
                    for p in self.paths_l:
                        p.append(current_node_key)
                        if run_debug:
                            if 'if num_sibs_this_depth == 1 and prev_node_key != self.root_key: # path 2' not in code_paths_traversed:
                                code_paths_traversed.append('if num_sibs_this_depth == 1 and prev_node_key != self.root_key: # path 2')
                else:
                    if sib_inc == 0 and prev_node_key != self.root_key:
                        temp_paths_l = copy.deepcopy(self.paths_l)
                        for p in self.paths_l:
                            p.append(current_node_key)
                            if run_debug:
                                if 'if sib_inc == 0 and prev_node_key != self.root_key: # path 3' not in code_paths_traversed:
                                    code_paths_traversed.append('if sib_inc == 0 and prev_node_key != self.root_key: # path 3')
                    else:
                        use_paths_l = copy.deepcopy(temp_paths_l)
                        for p in use_paths_l:
                            p.append(current_node_key)
                            self.paths_l.append(copy.deepcopy(p))
                            if run_debug:
                                if 'else: # path 4' not in code_paths_traversed:
                                    code_paths_traversed.append('else: # path 4')

                sib_inc += 1
            try:
                prev_node_key = current_node_key
            except UnboundLocalError as ule:
                x = 1
        if run_debug:
            end_time = timer()
            print('These code paths traversed:')
            for cpath in code_paths_traversed:
                print(cpath)
            print('Time elapsed:')
            print('\t' + str(timedelta(seconds= end_time - start_time)))
    #def dump_tree(self):
    #    for node in self.node_storage:
    #        print(node.dump_node())

    def get_unique_key(self, node_inc, zi, fayin):
        return str(node_inc) + ' ' + zi + ' ' + fayin

    def print_paths_l(self):
        for p in self.paths_l:
            print(' -> '.join(p))
        print(str(len(self.paths_l)) + ' paths.')

    def are_paths_unique(self):
        test_l = []
        retval = True
        for p in self.paths_l:
            if p not in test_l:
                test_l.append(p)
            else:
                retval = False
                break
        return retval

    #
    # OUTPUT should be of the form: [['fya1', 'fya2', 'fya3'], ['fyb1', 'byb2']]
    def get_list_of_raw_paths(self):
        output_line = ''
        retval = []
        for p in self.paths_l:
            output_line = ''
            for fy in p:
                fy = fy.split(' ')[2]
                output_line += fy + ' '
            output_line = output_line[0:len(output_line)-1] # remove last space
            retval.append(output_line)
        return retval

    def get_list_of_paths(self):
        retval = []
        for p in self.paths_l:
            current_path = []
            for fy in p:
                fy = fy.split(' ')[2]
                current_path.append(fy)
            retval.append(copy.deepcopy(current_path))
        return retval

class fy_tree2:
    def __init__(self, data_d):
        self.data_d = {key: value[:] for key, value in data_d.items()}
        #self.create_depth2data_d()
        #self.create_depth2num_nodes_d()
        #self.root_node = None
        #self.first_born_key = None
        self.current_node_key = None
        self.current_value = None

        self.node_inc = 0
        self.tree_d = {}
        self.root_key = '0 root_key root_value'
        self.node_storage = []
        self.temp_node = tree_node('')
        self.build_tree()

    def get_unique_key(self, node_inc, zi, fayin):
        return str(node_inc) + ' ' + zi + ' ' + fayin

    def get_paths_of_max_length(self):
        #self.node_storage
        x =1

    def print_paths_l(self):
        for p in self.paths_l:
            print(' -> '.join(p))
        print(str(len(self.paths_l)) + ' paths.')

    def build_tree(self):
        #
        # Add Root node
        self.temp_node.set_unique_id(self.root_key)
        prev_node_key = self.root_key
        self.node_storage.append(copy.deepcopy(self.temp_node))
        self.current_node_inc = 0
        self.paths_l = []
        temp_paths_l = []
        for zi in self.data_d:
            fayin_l = self.data_d[zi]  # data is like this: {'深': ['tśʰim', 'śim', 'śimᶜ'], '賢': ['śimᴮ'], '神': ['źin', 'hioŋ']}
            if not fayin_l:
                print('ERROR: ' + zi + ' is missing LHan!')
            num_sibs_this_depth = len(fayin_l)
            sib_inc = 0
            for fy in fayin_l:
                self.current_node_inc += 1
                current_node_key = self.get_unique_key(self.current_node_inc, zi, fy)
                if prev_node_key == self.root_key:
                    self.paths_l.append([current_node_key])
                if num_sibs_this_depth == 1:
                    for p in self.paths_l:
                        p.append(current_node_key)
                else:
                    if sib_inc == 0 and prev_node_key != self.root_key:
                        temp_paths_l = copy.deepcopy(self.paths_l)
                        for p in self.paths_l:
                            p.append(current_node_key)
                    else:
                        use_paths_l = copy.deepcopy(temp_paths_l)
                        for p in use_paths_l:
                            p.append(current_node_key)
                            self.paths_l.append(copy.deepcopy(p))
                self.temp_node.reset_node(current_node_key)
                if sib_inc == 0:
                    # set current node as previous node's left child
                    prev_node = self.node_storage[self.current_node_inc-1]
                    prev_node.set_left_child(current_node_key)
                    # set previous node to parent of current node
                    self.temp_node.set_parent(prev_node.get_unique_id())
                elif sib_inc <= (num_sibs_this_depth-1): # if not right most or left most node at this depth
                    # set previous node as the left sibling of the current node
                    prev_node = self.node_storage[self.current_node_inc-1]
                    self.temp_node.set_left_sibling(prev_node.get_unique_id())
                    # set current node as the right sibling of the previous node
                    prev_node.set_right_sibling(current_node_key)
                else:
                    print('build_tree() ERROR: Not supposed to be here error!')
                self.node_storage.append(copy.deepcopy(self.temp_node))
                sib_inc += 1
            prev_node_key = current_node_key

    def dump_tree(self):
        for node in self.node_storage:
            print(node.dump_node())


class fy_tree:
    def __init__(self, data_d):
        self.data_d = {key: value[:] for key, value in data_d.items()}
        self.create_depth2data_d()
        self.create_depth2num_nodes_d()
        #self.tree = []
        self.setup_data_dict_indicies()
        self.root_node = None
        self.first_born_key = None
        self.current_node_key = None
        self.current_value = None

        self.node_inc = 0
        self.tree_d = {}
        self.root_key = '0 root_key root_value'
        self.temp_node = tree_node('')
        self.build_tree() # sets self.root_node and self.first_born_key
        self.current_value = self.tree_d[self.current_node_key].get_unique_id() # general_tree_node.value
        self.start = self.current_value # general_tree_node.value
        self.path = sllist(self.root_node.get_unique_id())
        self.child_path = sllist(self.root_node.get_unique_id())
        self.visited_nodes = sllist(self.root_node.get_unique_id())

    #
    # creates a dictionary, self.depth2num_nodes_d, where you can enter a depth, and it tells you how many
    #  nodes are at that depth
    def create_depth2num_nodes_d(self):
        self.depth2num_nodes_d = {}
        self.depth2num_nodes_d[0] = 1 # root node
        depth = 0
        for k in self.data_d:
            depth += 1
            num_nodes_at_prev_depth = self.depth2num_nodes_d[depth-1]
            num_fayin_at_current_depth = len(self.data_d[k])
            self.depth2num_nodes_d[depth] = num_fayin_at_current_depth * num_nodes_at_prev_depth

    def get_num_nodes_at_depth(self, depth):
        retval = -1
        try:
            retval = self.depth2num_nodes_d[depth]
        except IndexError as ie:
            x = 1
        return retval

    def get_data_d_entry_given_depth(self, depth):
        retval = ''
        try:
            retval = self.depth2data_d[depth]
        except IndexError as ie:
            x = 1
        return retval

    def create_depth2data_d(self):
        self.depth2data_d = {}
        #for inc in range(1, len(self.data_d), 1):
        inc = 0
        for k in self.data_d:
            inc += 1
            self.depth2data_d[inc] = {}
            self.depth2data_d[inc][k] = self.data_d[k]

    def dump_tree(self):
        funct_name = 'dump_tree()'
        print(funct_name + ' called.\n')
        for k in self.tree_d:
            print(self.tree_d[k].dump_node())

    def print_tree(self):
        for k in self.tree_d:
            print(self.tree_d[k].get_unique_id())

    def get_current_node(self):
        return self.tree_d[self.current_node_key]

    def get_node(self, unique_id):
        retval = None
        if unique_id in self.tree_d:
            retval = self.tree_d[unique_id]
        return retval

    def reset_search_parameters(self):
        self.current_node_key = self.first_born_key
        self.current_value = self.get_current_node().get_unique_id() # general_tree_node.value
        self.start = self.current_value # general_tree_node.value

    def set_first_born(self, new_node, parent_node): # increments node inc
        if self.first_born_key == None and parent_node == self.get_root_node_key():
            self.first_born_key = str(self.get_current_node_inc()) + ' ' + new_node.get_zi() + ' ' + new_node.get_fayin()
            self.current_node_key = self.first_born_key
            new_node.set_parent(self.get_root_node_key())
            self.tree_d[self.first_born_key] = copy.deepcopy(new_node)
            root = self.get_root_node().set_left_child(self.first_born_key)
            return self.first_born_key
            #new_node.set_unique_id(self.first_born_key)
            #self.add_node(new_node, parent_node)

    def get_root_node_key(self):
        return self.root_key

    def get_root_node(self):
        retval = None
        if self.tree_d:
            retval = self.tree_d[self.root_key]
        return retval

    def add_node(self, new_node, parent_key, node_inc): # increments node inc
        if self.first_born_key == None:
            return self.set_first_born(new_node, parent_key) # returns first born key

        k = str(node_inc) + ' ' + new_node.get_zi() + ' ' + new_node.get_fayin()
        if k not in self.tree_d: # k should NOT be in the dictionary; it should be UNIQUE (self.node_inc ensures that)
            new_node.set_unique_id(k)
            new_node.set_parent(parent_key)
            self.tree_d[k] = copy.deepcopy(new_node)
        else:
            print('add_node() ERROR: ' + k + ' is already in self.tree_d! That\'s not supposed to happen!')
        return k

    def get_next_node_inc(self):
        self.node_inc += 1
        return self.node_inc

    def get_current_node_inc(self):
        return self.node_inc

    def add_root_node(self):
        # since the first character in the chain may hae multiple pronunciations, can't make it the root
        # so, we're using a root with fake data
        new_node = tree_node(self.root_key)
        if self.root_key not in self.tree_d: # k should NOT be in the dictionary; it should be UNIQUE (self.node_inc ensures that)
            new_node.set_unique_id(self.root_key)
            self.tree_d[self.root_key] = copy.deepcopy(new_node, None) # 'None' = no parent
            self.root_node = self.get_root_node()

    def is_there_a_child(self, current_depth):
        retval = False
        if current_depth < len(self.data_d):
            retval = True
        return retval

    #def given_current_depth_get_child_key(self, current_depth):
        #current_key = self.ind2key_d[current_depth]
    #    retval = -1
    #    if current_depth < len(self.data_d) - 1 and current_depth > -1:
    #        current_char = self.data_d[current_depth]
    #        retval = self.ind2key_d[current_depth + 1]
    #    return retval

    # these are used to speed up lookups
    def setup_data_dict_indicies(self):
        # prepare additional dictionaries
        self.key2ind_d = dict()
        self.ind2key_d = dict()
        for ind, key in enumerate(self.data_d):
            self.key2ind_d[key] = ind  # dictionary index_of_key
            self.ind2key_d[ind] = key  # dictionary key_of_index

    def set_parent_and_child_relations(self, zi, fayin, parent_key, current_depth): # calls add_node()
        parent_inc = self.get_next_node_inc()
        parent_uniq_id = str(parent_inc) + ' ' + zi + ' ' + fayin
        self.temp_node.reset_node(parent_uniq_id)
        self.temp_node.set_parent(parent_key)  # node level function

        if self.is_there_a_child(current_depth):
            parent_data = self.get_data_d_entry_given_depth(current_depth)
            parent_col_pos = parent_data[zi].index(fayin)
            parent_num_nodes = self.get_num_nodes_at_depth(current_depth)#len(parent_data[zi]) # number of nodes at parent's depth
            child_data = self.get_data_d_entry_given_depth(current_depth+1)
            child_zi = str(next(iter(child_data)))
            #child_fy_l_len = len(child_data[child_zi])
            child_num_nodes = self.get_num_nodes_at_depth(current_depth+1) # number of nodes at childs's depth
            #child_inc = parent_inc + parent_num_nodes - parent_col_pos + (parent_col_pos)*child_num_nodes
            if parent_num_nodes == child_num_nodes:
                child_inc = parent_inc + child_num_nodes
            #elif parent_num_nodes > child_num_nodes:
            else:
                child_inc = parent_inc + parent_num_nodes - (parent_col_pos + 1) + child_num_nodes*parent_col_pos + 1
            child_key = str(child_inc) + ' ' + child_zi + ' ' + child_data[child_zi][0]
            #child_key = self.given_current_depth_get_child_key(current_depth)
            self.temp_node.set_left_child(child_key)
        return self.add_node(self.temp_node, parent_key, parent_inc)

    def build_tree(self):
        self.add_root_node()
        parent_key = self.get_root_node_key()
        temp_node = tree_node('')
        prev_node_id = self.get_root_node_key()

    def build_tree_old(self):
        self.add_root_node()
        parent_key = self.get_root_node_key()
        left_tnode = tree_node('')
        right_tnode = tree_node('')
        current_depth = 1 # since root is 0, and we're already past the root
        prev_node_id = self.get_root_node_key()
        for zi in self.data_d:
            fayin_l = self.data_d[zi] # data is like this: {'深': ['tśʰim', 'śim', 'śimᶜ'], '賢': ['śimᴮ'], '神': ['źin', 'hioŋ']}
            if not fayin_l:
                print('ERROR: ' + zi + ' is missing LHan!')
            first_fy = fayin_l[0]
            last_fy = fayin_l[len(fayin_l) - 1]
            fy_inc = 0
            #
            # TO DO:
            #  - the problem seems to be this
            #    we should be incrementing via number of nodes per depth
            #    but we're going by fayin
            #  - FIX!!
            # IMPORTANT: use a linked list when building the tree to keep track of where you've been
            for fy in fayin_l: # each zi may have multiple pronunciations
                # add node
                current_node_id = self.set_parent_and_child_relations(zi, fy, parent_key, current_depth) # calls add_node()
                #left_node = self.get_node(current_node_id)
                if not first_fy:
                    #
                    # set sibling relationships
                    self.tree_d[prev_node_id].set_right_sibling(current_node_id)
                    self.tree_d[current_node_id].set_left_sibling(prev_node_id)
                else:
                    x = 1
                fy_inc += 1
                prev_node_id = current_node_id
                #print(zi + ': ' + ','.join(self.data_d[zi]))
            current_depth += 1

class linked_list: # this class just wraps the llist library's sllist ( - a singly linked list) structure
                   # https://ajakubek.github.io/python-llist/index.html
    def __init__(self):
        self.linked_list = sllist()

    def print(self):
        for value in self.linked_list:
            print(value)

    def find(self, node_value): # return True if a node has that value, False otherwise
        x = 1
    def add_node(self, new_node):
        self.linked_list.append(new_node)

    def get_node_at(self, node_pos):
        try:
            node = self.linked_list.nodeat(node_pos)
            retval = node.value
        except IndexError as ie:
            retval = None
        return retval

    def insert_after(self, value, node_pos):
        self.linked_list.insertafter(value, self.linked_list.nodeat(node_pos))

    def insert_before(self, value, node_pos):
        self.linked_list.insertbefore(value, self.linked_list.nodeat(node_pos))

    def append_left(self, new_node): # Add new_node to the left side of the list and return inserted sllistnode.
        self.linked_list.appendleft(new_node)

    def append_right(self, new_node): # Add new_node to the right side of the list and return inserted sllistnode.
        self.linked_list.appendright(new_node)

    def clear_list(self): # Remove all nodes from the list.
        self.linked_list.clear()

    def remove_node_at(self, node_pos):
        node = self.linked_list.nodeat(node_pos)
        self.linked_list.remove(node)

    def get_first_node(self):
        node = self.linked_list.first
        return node.value

    def get_last_node(self):
        node = self.linked_list.last
        return node.value

    def pop(self): # Remove and return an element’s value from the right side of the list.
        return self.linked_list.pop()

    def pop_right(self): # Remove and return an element’s value from the right side of the list.
        return self.linked_list.popright()

    def pop_left(self): # Remove and return an element’s value from the left side of the list.
        return self.linked_list.popleft()

def test_linked_list():
    funct_name = 'test_linked_list()'
    test_data = {'深': ['tśʰim', 'śim', 'śimᶜ'], '賢': ['śimᴮ'], '神': ['źin', 'hioŋ']}
    #node1 = tree_node()
    #tree = fy_tree(test_data)
    lk_list = sllist()
    for zi in test_data:
        for fy in test_data[zi]:
            node = tree_node(zi, fy)
            lk_list.append(node)
            print(zi + ': ' + fy)
    n = lk_list.pop()
    print('n.get_zi() = ' + n.get_zi() + ', n.get_fayin() = ' + n.get_fayin() )
    l = len(lk_list)
    print('\nLinked list: ')
    for inc in range(0, l, 1):
        n = lk_list.nodeat(inc)
        print(n.value.get_zi() + ': ' + n.value.get_fayin())


#def test_pygtrie():
#    print('\nDictionary test')
#    print('===============\n')
#
#    t = pygtrie.CharTrie()
#    t['cat'] = True
#    t['caterpillar'] = True
#    t['car'] = True
#    t['bar'] = True
#    t['exit'] = False

#    print('Start typing a word, "exit" to stop')
#    print('(Other words you might want to try: %s)\n' % ', '.join(sorted(
#        k for k in t if k != 'exit')))

#    text = ''
#    while True:
#        ch = getch()
#        if ord(ch) < 32:
#            print('Exiting')
#            break

#        text += ch
#        value = t.get(text)
#        if value is False:
#            print('Exiting')
#            break
#        if value is not None:
#            print(repr(text), 'is a word')
#        if t.has_subtrie(text):
#            print(repr(text), 'is a prefix of a word')
#        else:
#            print(repr(text), 'is not a prefix, going back to empty string')
#            text = ''

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

def readin_debug_data_for_multi_fayin_path_stuff(filename=''):
    funct_name = 'readin_debug_data_for_multi_fayin_path_stuff()'
    if not filename:
        filename = 'fayin_path_test_data.txt'
    input_file = os.path.join(get_hanproject_dir(), filename)
    #print('input_file = ' + input_file)
    input_lines_l = readlines_of_utf8_file(input_file)
    zi2fayin_d = {}
    fayin_l = []
    for ill in input_lines_l:
        if '\t' in ill:
            ill = ill.split('\t')
            zi = ill[0]
            fy_l = ill[1]
            zi2fayin_d[zi] = fy_l.split(' ')
        else:
            fayin_l.append(ill)
    return zi2fayin_d, fayin_l

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

def get_list_of_fayin_paths(zi2fayin_d):
    tree = fy_tree3(zi2fayin_d)
    return tree.get_list_of_paths()

def test_tree_structure():
    funct_name = 'test_tree_structure()'
    #尋	zim
    # ./hanproject/fayin_path_test_data_lu1983_027.txt
    zi2fayin_d, fayin_l = readin_debug_data_for_multi_fayin_path_stuff('fayin_path_test_data_lu1983_038.txt')
    #zi2fayin_d = {'陰' : ['Ɂim', 'Ɂimᶜ'], '深': ['tśʰim', 'śim', 'śimᶜ'], '賢': ['śimᴮ'], '神': ['źin', 'hioŋ'], '陰' : ['Ɂim', 'Ɂimᶜ']}
    run_debug = True
    tree = fy_tree3(zi2fayin_d, run_debug) # calculate paths is called from inside the constructor

    print('starting library call:')
    start_time = timer()
    root_node = create_tree(zi2fayin_d)
    pad_list = given_root_node_get_list_of_possible_paths(root_node)
    end_time = timer()
    print('\tEnd library call.')
    print('\tTime elapsed:')
    print('\t\t' + str(timedelta(seconds=end_time - start_time)))

    #tree.print_tree()
    #tree.dump_tree()
    #tree.print_paths_l()
    raw_paths = tree.get_list_of_raw_paths()
    if 0:
        for rp in raw_paths:
            print(' '.join(rp))
    print('Paths should be ' + str(len(zi2fayin_d)) + ' deep.')
    if tree.are_paths_unique():
        print('\tAll paths are unique! They REALLY are special!')
    else:
        print('\tSome paths repeat!')

    if 0:
        print('Compare output to this:')
        for fy in fayin_l:
            print(fy)

    if set(fayin_l) == set(raw_paths):
        print('INPUT and OUTPUT are equal!')
    else:
        print('We have issues!')
        fl = set(fayin_l)
        rp = set(raw_paths)
        df = fl.difference(rp)
        inte = fl.intersection(rp)
        if 0:
            print('The difference between the two sets:')
            for l in df:
                print(l)
            print('The intersection between the two sets:')
            for l in inte:
                print(l)
            print(str(len(df)) + ' lines are different, while ' + str(len(inte)) + ' are the same.')
    x = 1
#test_pygtrie()
#test_tree_structure()
#test_linked_list()