#! C:\Python36\
# -*- encoding: utf-8 -*-
# this code comes from https://towardsdatascience.com/implementing-the-general-tree-and-depth-first-search-dfs-in-python-from-scratch-b3187e9e117d
class Node(object):
    def __init__(self,val):
        self.val = val
        self.next = None

    def get_data(self):
        return self.val

    def set_data(self,val):
        self.val = val

    def get_next(self):
        return self.next

    def set_next(self,next):
        self.next = next


class LinkedList(object):
    def __init__(self,*values):
        self.count = len(values) - 1
        self.head = Node(values[0])
        node = self.head
        for idx, val in enumerate(values):
            if idx == 0:
                continue
            else:
                tempnode = Node(val)
                node.set_next(tempnode)
                node = node.get_next()


    def get_count(self):
        return self.head

    def insert(self,data):
        new_node = Node(data)
        new_node.set_next(self.head)
        self.head = new_node
        self.count +=1

    def insert_at(self,idx,val):
        if idx > self.count +2:
            return

        if idx == 0:
            self.insert(val)
        else:
            tempIdx = 0
            node = self.head
            while tempIdx < idx -1:
                node = node.get_next()
                tempIdx += 1
            continuation = node.get_next()
            insertion = Node(val)
            node.set_next(insertion)
            node.get_next().set_next(continuation)
            self.count += 1

    def find(self,val):
        item = self.head
        while item != None:
            if item.get_data() == val:
                return item
            else:
                item = item.get_next()

        return None

    def deleteAt(self,idx):
        if idx > self.count+1:
            return
        if idx == 0:
            self.head = self.head.get_next()
        else:
            tempIdx = 0
            node = self.head
            while tempIdx < idx -1:
                node = node.get_next()
                tempIdx +=1
            node.set_next(node.get_next().get_next())
            self.count -= 1

    def dump_list(self):
        tempnode = self.head
        while (tempnode != None):
            print("Node: ",tempnode.get_data())
            tempnode = tempnode.get_next()


    def swap(self,idx_a,idx_b):
        if idx_a == idx_b:
            return
        elif idx_a > idx_b:
            idx_2,idx_1 = idx_a,idx_b
        else:
            idx_2,idx_1 = idx_b,idx_a

        node = self.head
        tempIdx = 0

        while tempIdx < idx_2:
            if tempIdx != idx_1:
                node = node.get_next()
                tempIdx += 1
            else:
                elem_1 = node.get_data()
                node = node.get_next()
                tempIdx += 1
        elem_2 = node.get_data()

        self.deleteAt(idx_1)
        self.deleteAt(idx_2-1)
        self.insert_at(idx_1,elem_2)
        self.insert_at(idx_2,elem_1)

    def move_min(self,sorted_idx):
        temp_idx = 0
        node = self.head
        selection = self.head.get_data()
        while temp_idx <= self.count:

            if temp_idx <= sorted_idx:
                node = node.get_next()
                temp_idx += 1

            elif temp_idx == sorted_idx +1:
                selection = node.get_data()
                selected_idx = temp_idx
                node = node.get_next()
                temp_idx += 1

            else:
                if node.get_data() < selection:
                    selection = node.get_data()
                    selected_idx = temp_idx
                try:
                    node = node.get_next()
                    temp_idx +=1
                except:
                    break

        self.deleteAt(selected_idx)
        self.insert_at(sorted_idx, selection)
        return sorted_idx + 1

    def selection_sort(self):
        """
        Note, move_min() method assumes that the element at first index is already sorted. As such, after
        iteratively calling move_min(), the first element will be moved to the final index. Logic must be
        built in to ID the final element and move it to its appropriate home.
        """

        # part 1: sorts elements, pushing first element to last position
        sorted_idx = 0
        while sorted_idx < self.count:
            sorted_idx = self.move_min(sorted_idx)


        # part 2: identifies final element and relocates appropriately
        temp_idx = 0
        node = self.head
        while temp_idx < self.count:
            node = node.get_next()
            temp_idx += 1
        final_elem = node.get_data()
        final_idx = temp_idx

        temp_idx = 0
        node = self.head
        while temp_idx < self.count:
            if node.get_data() < final_elem:
                temp_idx += 1
                node = node.get_next()
            else:
                self.deleteAt(final_idx)
                self.insert_at(temp_idx,final_elem)
                break


if __name__ == '__main__':
    t1 = LinkedList(4,2,1,0,3)
    t1.selection_sort()
    t1.dump_list()