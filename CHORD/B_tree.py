class BTreeNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.data = []  # Store a tuple (key, array) as the data
        self.children = []


class BTree:
    def __init__(self, degree):
        self.root = BTreeNode()
        self.degree = degree

    def insert(self, key, array):
        root = self.root

        if len(root.data) == (2 * self.degree) - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, array)
        else:
            self._insert_non_full(root, key, array)

    def _insert_non_full(self, x, key, array):
        i = len(x.data) - 1

        if x.leaf:
            x.data.append((key, array))
            while i >= 0 and key < x.data[i][0]:
                x.data[i + 1] = x.data[i]
                i -= 1
            x.data[i + 1] = (key, array)
        else:
            while i >= 0 and key < x.data[i][0]:
                i -= 1

            i += 1
            if len(x.children[i].data) == (2 * self.degree) - 1:
                self._split_child(x, i)
                if key > x.data[i][0]:
                    i += 1

            self._insert_non_full(x.children[i], key, array)

    def _split_child(self, x, i):
        degree = self.degree
        y = x.children[i]
        z = BTreeNode(leaf=y.leaf)
        x.children.insert(i + 1, z)
        x.data.insert(i, y.data[degree - 1])
        z.data = y.data[degree:]
        y.data = y.data[:degree - 1]

        if not y.leaf:
            z.children = y.children[degree:]
            y.children = y.children[:degree]
