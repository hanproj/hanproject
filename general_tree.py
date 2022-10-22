#! C:\Python36\
# -*- encoding: utf-8 -*-
# This code comes from https://towardsdatascience.com/implementing-the-general-tree-and-depth-first-search-dfs-in-python-from-scratch-b3187e9e117d
# Except for the class general_tree_node

from linked_list import LinkedList
class general_tree_node:
    def __init__(self, value):
        self.child_node = None
        self.parent_node = None
        self.value = value
        self.right_sib_node = None
        self.left_sib_node = None

    def get_child(self):
        return self.child_node

    def get_parent(self):
        return self.parent_node

    def get_value(self):
        return self.value

    def get_left(self):
        return self.left_sib_node

    def get_right(self):
        return self.right_sib_node

    def set_child(self, child_node):
        self.child_node = child_node

    def set_parent(self, parent_node):
        self.parent_node = parent_node

    def set_value(self, value):
        self.value = value

    def set_left(self, left_sibling_node):
        self.left_sib_node = left_sibling_node

    def set_right(self, right_sibling_node):
        self.right_sib_node = right_sibling_node

class GeneralTree():
    """
    Parameters:
    @root: root node
    @first_born: leftmost child of root node
    @current_node: initalized as first born
    @current-value: initialized as value of first born (current node)
    @visited: Linked list of all values which have previously been visited
    @path: FULL path, traversing siblings, from root to search value (LL)
    @child_path: path, sibling traversal not captured, more closely resembles typical tree design/behavior (LL)

    Methods:
    @check_visited: Determines if a tree node has been visited yet to prevent cyclical movements
    @check_child_path: Determines if a tree node is already captured in child_path
    @depth_first_traversal: Explores entire tree via depth first protocol
    @depth_first_search: Captures all necessary node traversals required to move from root to search value
        including sibling node traversals
    @child_depth_first_search: modification to @depth_first_search such that sibling traversals are eliminated.
        This more closely mimics general tree behavior. In a file system, for example, traversing siblings is
        not necessary. This method allows for the correct capture of path.
    """

    def __init__(self, root=None):
        self.root = root # general_tree_node()
        self.first_born = self.root.get_child() # general_tree_node()
        self.current_node = self.first_born # general_tree_node()
        self.current_value = self.current_node.get_value() # general_tree_node.value
        self.start = self.current_value # general_tree_node.value
        self.visited = LinkedList(self.root.get_value()) # linked list of nodes that are general_tree_node.value
        self.path = LinkedList(self.root.get_value()) # linked list of nodes that are general_tree_node.value
        self.child_path = LinkedList(self.root.get_value()) # linked list of nodes that are general_tree_node.value

    def check_visited(self, val):
        if self.visited.find(val):
            return True
        else:
            return False

    def check_child_path(self, val):
        if self.child_path.find(val):
            return True
        else:
            return False

    def depth_first_traversal(self):

        if self.current_value == self.root.get_value():
            self.visited.insert_at(idx=1, val=self.start)

            # copy self.visited then reset for future method calls
            self.completed_visited = self.visited
            self.current_node = self.first_born
            self.current_value = self.current_node.get_value()
            self.start = self.current_value
            self.visited = LinkedList(self.root.get_value())

            return self.completed_visited.dump_list()

        else:
            # ==== tree traversal logic ====
            # If the current NODE has a CHILD that has NOT been visited, set the child node as the current NODE
            #    and recursively call this function
            if self.current_node.get_child() and self.check_visited(self.current_node.get_child().get_value()) == False:
                # parent -> child (not yet visited)
                self.current_node = self.current_node.get_child()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
            # If there is a sibling NODE to the RIGHT, and it has NOT been visited, set the RIGHT NODE as the current
            #    node and recursively call this function
            elif self.current_node.get_right() and self.check_visited(
                    self.current_node.get_right().get_value()) == False:
                # sibling -> right_sibling (not yet visited)
                self.current_node = self.current_node.get_right()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
            # If there is NO NODE to the RIGHT, but there IS a NODE to the LEFT, then set the LEFT NODE as current,
            #   and recursively call this function
            elif self.current_node.get_right() == None and self.current_node.get_left():
                # right_most_sibling -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()
            # If there is a NODE to the LEFT, and the NODE to the RIGHT has been visited, then set the NODE to the
            #   LEFT as current, and recursively call this function
            elif self.current_node.get_left() != None and self.check_visited(
                    self.current_node.get_right().get_value()) == True:
                # sibling (not left-most or right-most) -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()
            # OTHERWISE: you're at the LEFT most sibling, so go back to the PARENT node (which has already been visited)
            else:
                # left_most_sibling -> parent (already visited)
                self.current_node = self.current_node.get_parent()
                self.current_value = self.current_node.get_value()

                # ==== recursively apply logic ====
            self.depth_first_traversal()

    def depth_first_search(self, search_val):
        self.search_val = search_val

        if self.current_value == search_val or self.current_value == self.root.get_value():
            self.visited.insert_at(idx=1, val=self.start)
            self.path.insert_at(idx=1, val=self.start)

            if self.check_visited(self.search_val) == True:
                condition = 1
            else:
                condition = 0

            # copy self.path and reset for future method calls
            self.completed_path = self.path
            self.current_node = self.first_born
            self.current_value = self.current_node.get_value()
            self.start = self.current_value
            self.visited = LinkedList(self.root.get_value())
            self.path = LinkedList(self.root.get_value())

            if condition == 1:
                return self.completed_path.dump_list()
            else:
                print("Value not found")

        else:
            # ==== tree traversal logic ====
            if self.current_node.get_child() and self.check_visited(self.current_node.get_child().get_value()) == False:
                # parent -> child (not yet visited)
                self.current_node = self.current_node.get_child()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
                self.path.append(self.current_value)

            elif self.current_node.get_right() and self.check_visited(
                    self.current_node.get_right().get_value()) == False:
                # sibling -> right_sibling (not yet visited)
                self.current_node = self.current_node.get_right()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
                self.path.append(self.current_value)

            elif self.current_node.get_right() == None and self.current_node.get_left():
                # right_most_sibling -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()

            elif self.current_node.get_left() != None and self.check_visited(
                    self.current_node.get_right().get_value()) == True:
                # sibling (not left-most or right-most) -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()
                self.path.deleteAt(idx=self.path.count)

            else:
                # left_most_sibling -> parent (already visited)
                self.current_node = self.current_node.get_parent()
                self.current_value = self.current_node.get_value()
                self.path.deleteAt(idx=self.path.count)

                # ==== recursively apply logic ====
            self.depth_first_search(search_val=self.search_val)

    def child_depth_first_search(self, search_val):
        self.search_val = search_val

        if self.current_value == search_val or self.current_value == self.root.get_value():
            self.visited.insert_at(idx=1, val=self.start)
            self.path.insert_at(idx=1, val=self.start)

            if self.check_visited(self.search_val) == True:
                condition = 1
            else:
                condition = 0

            # copy self.path and reset for future method calls
            self.completed_child_path = self.child_path
            self.current_node = self.first_born
            self.current_value = self.current_node.get_value()
            self.start = self.current_value
            self.visited = LinkedList(self.root.get_value())
            self.child_path = LinkedList(self.root.get_value())

            if condition == 1:
                return self.completed_child_path.dump_list()
            else:
                print("Value not found")

        else:
            # ==== tree traversal logic ====
            if self.current_node.get_child() and self.check_visited(self.current_node.get_child().get_value()) == False:
                # parent -> child (not yet visited)
                if self.check_child_path(self.current_node.get_value()) == False:
                    self.child_path.append(self.current_value)
                self.current_node = self.current_node.get_child()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
                self.child_path.append(self.current_value)

            elif self.current_node.get_right() and self.check_visited(
                    self.current_node.get_right().get_value()) == False:
                # sibling -> right_sibling (not yet visited)
                self.child_path.deleteAt(idx=self.child_path.count)
                self.current_node = self.current_node.get_right()
                self.current_value = self.current_node.get_value()
                self.visited.append(self.current_value)
                self.child_path.append(self.current_value)

            elif self.current_node.get_right() == None and self.current_node.get_left():
                # right_most_sibling -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()

            elif self.current_node.get_left() != None and self.check_visited(
                    self.current_node.get_right().get_value()) == True:
                # sibling (not left-most or right-most) -> left_sibling (already visited)
                self.current_node = self.current_node.get_left()
                self.current_value = self.current_node.get_value()
                self.child_path.deleteAt(idx=self.child_path.count)

            else:
                # left_most_sibling -> parent (already visited)
                self.current_node = self.current_node.get_parent()
                self.current_value = self.current_node.get_value()
                self.child_path.deleteAt(idx=self.child_path.count)

                # ==== recursively apply logic ====
            self.child_depth_first_search(search_val=self.search_val)


if __name__ == '__main__':
    a1 = general_tree_node(value='a1')
    b1 = general_tree_node(value='b1')
    b2 = general_tree_node(value='b2')
    b3 = general_tree_node(value='b3')
    a1.set_child(b1)
    b1.set_parent(a1)
    b1.set_right(b2)
    b2.set_left(b1)
    b2.set_right(b3)
    b3.set_left(b2)

    c1 = general_tree_node(value='c1')
    c1.set_parent(b3)
    b3.set_child(c1)

    d1 = general_tree_node(value='d1')
    d1.set_parent(b1)
    b1.set_child(d1)

    r = GeneralTree(root=a1)
    r.depth_first_search(search_val='c1')
    r.child_depth_first_search(search_val='c1')