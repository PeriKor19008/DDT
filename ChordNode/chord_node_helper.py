import math
import requests
from routes import Routes
import socket
from chord_node_log import ChordNodeLog

loger = ChordNodeLog()
class ChordNodeHelper:


    def __init__(self):
        self.collision_counter: int = 0

    def get_back_references(self, node):
        r = (node.position - node.predecessor.position) % node.chord_size
        references = []
        references.append(node.predecessor.position)

        for i in range(int(math.sqrt(node.chord_size))):
            references.append((node.position - (2 ^ i)) % node.chord_size)
        j= len(references)
        for i in range(j):
            for k in range(r):
                references.append(references[i]-k)
        print("REFRENCIS:")
        for r in references:
            print(str(r))
        return set(references)


    def is_between(self,f:int,s:int,target:int,chord_size:int) -> bool:
        distance_clockwise = (target-f) % chord_size
        distance_counterclockwise = (s-target) % chord_size

        distance_f2s = (s-f) % chord_size

        return distance_clockwise < distance_f2s and distance_counterclockwise < distance_f2s


    def get_successors(self, position, node):
        suc_list = []

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
        i = 1
        while i < node.chord_size:
            pre = node.lookup((position - i) % node.chord_size)
            if pre.position != position:
                return pre
            i = i + 1



    # Added argument "collision",default: False, for re-calculating position
    def hash(self, string: str, chord_size: int, collision=False) -> int:
        h = 0
        for i in string:
            h = ord(i) * 7 + h
        result = h % chord_size
        print("----------------------------------------------"
              + "\nHASH\n"
              + "string:" + str(string) + "  result:" + str(result))
        
        # If the hash is called with true statement then change the hashing
        # Not sure if its correct to multiply by 11
        # Tested adding 11 and gave position 5960
        if collision:
            new_position = h*(11 + self.collision_counter)  % chord_size
            self.collision_counter += 1
            return new_position
        
        self.collision_counter = 0

        return h % chord_size

    def lookup_back_references(self, references, node):
        nodes = []
        print("\n\n\nLOG")
        loger.log_routes(node)
        print("\n\n\nLOG")
        for r in references:
            tmp = node.lookup(r)
            print("of node " + str(node.position) + " for refrence:" + str(r) + " the result was:" + str(tmp.ip) + " at " +str(tmp.position))
            nodes.append(tmp.ip)

        print("\n\n\nback refrences of node:" + str(node.position))
        for n in set(nodes):
            print(n)

        return set(nodes)

    def get_ip(self) -> str:
        name = socket.gethostname()
        return socket.gethostbyname(name) + ":5000/"