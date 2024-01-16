import math
import requests
from routes import Routes
import socket

class ChordNodeHelper:

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
                n = node.lookup((1 + suc_list[-1].position) % node.chord_size)
                if any(suc.position == n.position for suc in suc_list):
                    n = suc_list[i-1]
                suc_list.append(n)
        return suc_list

    def get_predecessor(self, position, node):
        pre_list = []
        if node.successors[0].ip == node.ip:

            tmp = node.successors[0]
            tmp.position = node.position
            pre_list = [tmp] * node.successor_num
            return pre_list

        for i in range(int(math.log2(node.chord_size))):
            if not pre_list:
                pre_list.append(node.lookup((position-(i+1)) % node.chord_size))
            else:
                for j in range(node.chord_size):
                    n = node.lookup(((pre_list[-1].position)-1+j) % node.chord_size)
                    if not any(pre.position == n.position for pre in pre_list):
                        pre_list.append(n)

        return pre_list

    def hash(self, string: str, chord_size: int) -> int:
        h = 0
        for i in string:
            h = ord(i) * 7 + h
        result = h % chord_size
        print("----------------------------------------------"
              + "\nHASH\n"
              + "string:" + str(string) + "  result:" + str(result))
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