import random
from B_tree import BTree


def node_init():
    ip = randIP()
    b_tree=BTree(4)

def randIP():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))