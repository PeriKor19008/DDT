import json

class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.owned_data = set()
        self.backup_data = set()
        self.t = t

    def owned(self, data):
        for d in data:
            self.owned_data.add(d)

    def insert(self, data):
        if self.search(data["Name"]) is not None:
            print("Data already exists in the tree.")
            return

        if len(self.root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)
        self._insert_non_full(self.root, data)

    def _insert_non_full(self, node, data):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(data)
            node.keys.sort(key=lambda x: x["Education"])
            return

        while i >= 0 and data["Education"] < node.keys[i]["Education"]:
            i -= 1
        i += 1

        if len(node.children[i].keys) == (2 * self.t) - 1:
            self.split_child(node, i)
            if data["Education"] > node.keys[i]["Education"]:
                i += 1

        self._insert_non_full(node.children[i], data)

    def split_child(self, parent, index):
        t = self.t
        child = parent.children[index]
        new_child = BTreeNode(child.leaf)
        parent.keys.insert(index, child.keys[t - 1])
        parent.children.insert(index + 1, new_child)
        new_child.keys = child.keys[t: (2 * t) - 1]
        child.keys = child.keys[:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        result = []
        i = 0
        while i < len(node.keys) and key > node.keys[i]["Education"]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]["Education"]:
            result.append(node.keys[i])
            # Search for more matches to the left
            j = i - 1
            while j >= 0 and node.keys[j]["Education"] == key:
                result.insert(0, node.keys[j])
                j -= 1
            # Search for more matches to the right
            j = i + 1
            while j < len(node.keys) and node.keys[j]["Education"] == key:
                result.append(node.keys[j])
                j += 1
            return result
        if node.leaf:
            return None
        return self._search(node.children[i], key)


    def delete(self, key):
        if self.search(key) is None:
            print("Data not found in the tree.")
            return
        self._delete(self.root, key)

    def _delete(self, node, key):
        t = self.t
        i = 0
        while i < len(node.keys) and key > node.keys[i]["Education"]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]["Education"]:
            if node.leaf:
                del node.keys[i]
            else:
                self.delete_internal_node(node, i)
        else:
            if node.leaf:
                print("Data not found in the tree.")
                return
            flag = True if i == len(node.keys) else False
            if len(node.children[i].keys) < t:
                self.fill(node, i)
            if flag and i > len(node.keys):
                self._delete(node.children[i - 1], key)
            else:
                self._delete(node.children[i], key)

    def delete_internal_node(self, node, i):
        if len(node.children[i].keys) >= self.t:
            pred = self.get_pred(node.children[i])
            node.keys[i] = pred
            self._delete(node.children[i], pred["Education"])
        elif len(node.children[i + 1].keys) >= self.t:
            succ = self.get_succ(node.children[i + 1])
            node.keys[i] = succ
            self._delete(node.children[i + 1], succ["Education"])
        else:
            self.merge(node, i)

    def get_pred(self, node):
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def get_succ(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]

    def fill(self, node, i):
        if i != 0 and len(node.children[i - 1].keys) >= self.t:
            self.borrow_from_prev(node, i)
        elif i != len(node.keys) and len(node.children[i + 1].keys) >= self.t:
            self.borrow_from_next(node, i)
        else:
            if i != len(node.keys):
                self.merge(node, i)
            else:
                self.merge(node, i - 1)

    def borrow_from_prev(self, node, i):
        child = node.children[i]
        sibling = node.children[i - 1]

        child.keys.insert(0, node.keys[i - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

        node.keys[i - 1] = sibling.keys.pop()

    def borrow_from_next(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]

        child.keys.append(node.keys[i])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

        node.keys[i] = sibling.keys.pop(0)

    def merge(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]

        child.keys.append(node.keys[i])
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)

        del node.keys[i]
        node.children.remove(sibling)

    def print_tree(self):
        self._print_tree(self.root, 0)

    def _print_tree(self, node, depth):
        if node is not None:
            for i in range(len(node.keys)):
                self._print_tree(node.children[i], depth + 1)
                print(" " * (4 * depth) + json.dumps(node.keys[i], indent=4))
            self._print_tree(node.children[-1], depth + 1)