import argparse
import sys
from collections import deque

class TrieNode:
    # Class-level counter to keep track of the unique numbers
    node_counter = 0

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.depth = 0
        self.parent = None  # Reference to the parent TrieNode

        # Assign a unique number to this node
        self.node_number = TrieNode.node_counter
        TrieNode.node_counter += 1

    def show_all_nodes(self, prefix=""):
        #print(f"Node {self.node_number}: {prefix}")

        for char, node in self.children.items():
            node.show_all_nodes(prefix + char)

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
                node.children[char].parent = node  # Set the parent reference
            node = node.children[char]
            node.depth = node.depth + 1
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    def search_by_node_number(self, node_number, node=None):
        if node is None:
            node = self.root

        if node.node_number == node_number:
            return node

        for child in node.children.values():
            # print(node.children.values())
            result = self.search_by_node_number(node_number, child)
            if result is not None:
                return result

        return None
    
    def bfs_build_failure(self):
        #failure = []
        failure = {}
        if not self.root:
            return

        queue = [(self.root, 0)]  # Using tuples to keep track of the node and its depth
        while queue:
            current_node, depth = queue.pop(0)


            # print("Node Number:", current_node.node_number, "| Depth:", depth)
            if depth <= 1:
                #failure.append({current_node.node_number: 0})
                failure[current_node.node_number] = 0
            if depth >= 1:
                if current_node.children != {}:
                    for child in current_node.children:
                        child_node = current_node.children[child]
                        c = child
                        u1 = failure[current_node.node_number]
                        while(c not in self.search_by_node_number(u1).children and self.search_by_node_number(u1).node_number != 0):
                            u1 = failure[u1]
                        if c in self.search_by_node_number(u1).children:
                            v1 = self.search_by_node_number(u1).children[c]
                            failure[child_node.node_number] = v1.node_number
                        else:
                            failure[child_node.node_number] = 0

            # Add children to the queue with their updated depth
            for char, child in current_node.children.items():
                queue.append((child, depth + 1))
        
        return failure
    
    def get_parent(self, node):
        return node.parent

def create_trie(search_items: list):

    trie = Trie()
    words = search_items
    for word in words:
        trie.insert(word[::-1])
    trie.root.show_all_nodes()

    return trie

def get_pmin(search_items: list):
    pmin = len(search_items[0])
    for search_item in search_items:
        if len(search_item) < pmin:
            pmin = len(search_item)
    return pmin

def HasChild(trie: Trie, u, letter):
    trieNode = trie.search_by_node_number(u)
    child_list = list(trieNode.children.keys())
    if letter in child_list:
        return True
    else:
        return False
    
def GetChild(trie: Trie, u, letter):
    trieNode = trie.search_by_node_number(u)
    # print(trieNode.children[letter].node_number)
    return trieNode.children[letter].node_number

def IsTerminal(trie: Trie, u):
    trieNode = trie.search_by_node_number(u)
    return trieNode.is_end_of_word

def build_horspool_table(pattern):
    table = {}
    for i, char in enumerate(pattern):
        table[char] = len(pattern) - i

    return table

def merge_dictionaries(list_of_dicts):
    big_dict = {}
    for dictionary in list_of_dicts:
        for key, value in dictionary.items():
            if key in big_dict:
                big_dict[key] = min(big_dict[key], value)
            else:
                big_dict[key] = value
    return big_dict

def build_depths(trie: Trie):
    depths = {}
    queue = [(trie.root, 0)]  # Using tuples to keep track of the node and its depth
    while queue:
        current_node, depth = queue.pop(0)
        depths[current_node.node_number] = depth

        # Add children to the queue with their updated depth
        for char, child in current_node.children.items():
            queue.append((child, depth + 1))
    return depths

def build_s1(trie: Trie, pmin, set1):
    s1 = {}
    depths = build_depths(trie)
    for trie_node in range(len(depths)):
        minimum = pmin
        if trie_node != 0:
        #     #for child in set1[trie_node]:
            if trie_node in set1.keys():
                for child in set1[trie_node]:
                    if depths[child]- depths[trie_node] < minimum:
                        #print(child, trie.search_by_node_number(child).depth)
                        minimum = depths[child]- depths[trie_node]
            else:
                minimum = pmin
        else:
            minimum = 1
        s1[trie_node] = minimum
    
    return s1 

def build_s2(trie: Trie, pmin, set2):
    s2 = {}
    depths = build_depths(trie)
    #for trie_node in set2:
    for trie_node in range(len(build_depths(trie))):
        if trie_node != 0:
            if trie_node in set2.keys():
                minimum = s2[trie.get_parent(trie.search_by_node_number(trie_node)).node_number]
                child = set2[trie_node]
                if depths[child]- depths[trie_node] < minimum:
                    #print(child, trie.search_by_node_number(child).depth)
                    minimum = depths[child]- depths[trie_node]
            else:
                minimum = s2[trie.get_parent(trie.search_by_node_number(trie_node)).node_number]
        else:
            minimum = pmin
        s2[trie_node] = minimum
    
    return s2 
def main():
    if len(sys.argv) < 3:
        print("Please provide the filename and search item(s) as arguments.")
        sys.exit(1)

    verbose = True
    if sys.argv[1] == "-v":
        verbose = False
        search_items = sys.argv[2:-1]
    else:
        search_items = sys.argv[1:-1]

    filename = sys.argv[-1]

    try:
        trie = create_trie(search_items)
        d = deque()

        pmin = get_pmin(search_items)
        i = pmin - 1
        j = u = 0
        m = ''

        with open(filename, "r") as file:
            t = file.read()

        # == Make data ==
        # rt
        list1 = []
        for search_item in search_items:
            list1.append(build_horspool_table(search_item))
        #print(list1)

        rt = merge_dictionaries(list1)
        #print(rt)

        # failure
        failure = trie.bfs_build_failure()
        set_temp = []
        unique_values = []
        for val in failure.values():
            if val not in unique_values and val != 0:
                unique_values.append(val)
        #print(unique_values)

        for val in unique_values:
            temp = []
            for key in failure:
                if failure[key] == val:
                    temp.append(key)
            set_temp.append(temp)
        #print(set_temp)

        i = 0
        set1 = {key: [] for key in unique_values}
        set1_cp = {key: [] for key in unique_values}
        for temp_list in set_temp:
            for item in temp_list:
                #print(item)
                #print(type(set1))
                set1[unique_values[i]].append(item)
                set1_cp[unique_values[i]].append(item)
            i = i + 1
        # print(set1)

        set2 = {}
        for key in set1_cp:
            for node_number in set1_cp[key]:
                if IsTerminal(trie, node_number):
                    set2[key] = node_number
                    set1_cp[key].remove(node_number)

        s1 = build_s1(trie, pmin, set1)
        s2 = build_s2(trie, pmin, set2)
        #print("s1",s1,"\n", "s2", s2)

        # end making tables

        i = 0
        while(i < len(t)):
            while(HasChild(trie, u, t[i-j])):
                u = GetChild(trie, u, t[i-j])
                m = m + t[i-j]
                j = j + 1
                if IsTerminal(trie, u):
                    d.append([m[::-1], i-j+1])

            if j > i:
                j = i
            
            s = min(int(s2[u]), max(int(s1[u]), int(rt[t[i-j]])-j-1))

            i = i + s
            j = 0
            u = 0
            m = ''
        
        if not verbose:
            for i in range(len(build_depths(trie))):
                print("{}: {},{}".format(i, s1[i], s2[i]))
        for i in range(len(d)):
            #print(d[i][0], ":", d[i][1])
            print("{}: {}".format(d[i][0], d[i][1]))

    except FileNotFoundError:
        print("File", filename, "not found.")
    except IOError:
        print("Error reading the file", filename)

if __name__ == "__main__":
    main()