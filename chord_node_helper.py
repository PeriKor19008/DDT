import math
import requests
from routes import Routes
import socket

class ChordNodeHelper:



    def lookup_inner(self, key: int, node):
        closest_successor = node.successors[0]
        print("closest succesesor"+str(closest_successor.position))
        for n in node.predecessors + node.successors:
            if n.position == key:
                return [n, True]

        f = Routes(node.position, node.ip)
        for suc in node.successors:

            if self.is_between(f.position, suc.position, key, node.chord_size):
                return [suc, True]


        print("node routing"+str(node.routing_table[0].position))
        for r in range(len(node.routing_table)):
            print("r position"+str(node.routing_table[r].position))

            if node.routing_table[r].position == key:
                print("a")
                return [r, False]
            if (node.routing_table[r].position > closest_successor.position) and (node.routing_table[r].position > key):
                closest_successor = r
                print("b")
                return [closest_successor, False]


        return [closest_successor, False]








    def  get_back_references(self,node):
        r = (node.position - node.predecessors[0].position) % node.chord_size
        references = []

        for i in range(int(math.sqrt(node.chord_size))):
            references.append((node.position - (2 ^ i)) % node.chord_size)
        j= len(references)
        for i in range(j):
            for k in range(r):
                references.append(references[i]-k)

        return set(references)


    def is_between(self,f:int,s:int,target:int,chord_size:int) -> bool:
        distance_clockwise = (target-f) % chord_size
        distance_counterclockwise = (s-target) % chord_size

        distance_f2s = (s-f) % chord_size

        return distance_clockwise < distance_f2s and distance_counterclockwise < distance_f2s


    def get_successors(self, position, node):
        suc_list = []
        if node.successors[0].ip == node.ip:

            tmp = node.successors[0]
            tmp.position = node.position
            suc_list = [tmp] * node.successor_num
            return suc_list

        for i in range(node.successor_num):
            if not suc_list:
                suc_list.append(node.lookup((position+i+1) % node.chord_size))
            else:
                suc_list.append(node.lookup((1 + suc_list[-1].position) % node.chord_size))
        return suc_list

    def get_predecessor(self, position, node):
        pre_list = []
        if node.successors[0].ip == node.ip:

            tmp = node.successors[0]
            tmp.position = node.position
            pre_list = [tmp] * node.successor_num
            return pre_list

        for i in range(node.chord_size):
            if pre_list:
                pre_list.append(node.lookup((position-(i+1)) % node.chord_size))
            else:
                pre_list.append(node.lookup((pre_list[-1].position-1) % node.chord_size))
        return pre_list

    def hash(self, string: str, chord_size: int) -> int:
        h = 0
        for i in string:
            h = ord(i) * 7 + h
        return h % chord_size

    def lookup_back_references(self, references, node):
        nodes = []
        for r in references:
            tmp = node.lookup(r)
            nodes.append(tmp.ip)
        return set(nodes)

    def get_ip(self) -> str:
        name = socket.gethostname()
        return socket.gethostbyname(name) + ":5000/"