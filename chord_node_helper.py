import math
import requests
from routes import Routes
from chord_node import ChordNode
import socket

class ChordNodeHelper:



    def lookup_inner(self, key: int, node: ChordNode):
        closest_successor = -1

        for pr in node.predecessors:
            if pr.position == key:
                return [pr, True]

        if node.routing_table != None:
            for r in node.routing_table:
                if r.position == key:
                    return [r, False]
                if (r.position > closest_successor.position) and (r.position < key):
                    closest_successor = r

        f = Routes(node.position, node.ip)
        for suc in node.successors:

            if suc.position == key:
                return [suc, True]
            if self.is_between(f.position, suc.position, key, node.chord_size):
                return [f, True]
            f = suc
            if closest_successor == -1:
                closest_successor = suc

            if (suc.position > closest_successor.position) and (suc.position < key):
                closest_successor = suc

        return [closest_successor, False]




    def  get_back_references(self,node):
        r = (node.position - node.predecessors[0]) % node.chord_size
        references = []

        for i in range(math.sqrt(node.chord_size)):
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


    def get_successors(self, position, node: ChordNode):
        suc_list = []
        if node.successors[0].ip == node.ip:
            node.position = self.hash_ip(node.ip, node.chord_size)
            tmp = node.successors[0]
            tmp.position = node.position
            suc_list.append(tmp)
            return suc_list

        for i in range(node.successor_num):
            if suc_list:
                suc_list.append(self.lookup((position+i+1) % node.chord_size, node))
            else:
                suc_list.append(self.lookup((1 + suc_list[-1]) % node.chord_size, node))
        return suc_list

    def get_predecessor(self, position, node: ChordNode):
        pre_list = []
        if node.successors[0].ip == node.ip:
            node.position = self.hash_ip(node.ip, node.chord_size)
            tmp = node.successors[0]
            tmp.position = node.position
            pre_list.append(tmp)
            return pre_list

        for i in range(node.chord_size):
            if pre_list:
                pre_list.append(self.lookup((position-(i+1)) % node.chord_size, node))
            else:
                pre_list.append(self.lookup((pre_list[-1]-1) % node.chord_size, node))
        return pre_list

    def hash_ip(self, ip: str, chord_size: int) -> int:
        h = 0
        for i in ip:
            h = ord(i) * 7 + h
        return h % chord_size

    def lookup_back_references(self, references, node: ChordNode):
        nodes = []
        for r in references:
            nodes.append(self.lookup(r, node))
        return set(nodes)

    def get_ip(self) -> str:
        name = socket.gethostname()
        return socket.gethostbyname(name) + ":5000/"