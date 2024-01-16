from b_tree_new import BTree
import requests
import math
import json
from chord_node_helper import ChordNodeHelper

helper = ChordNodeHelper()

class ChordNode:

    def __init__(self, size):

        self.chord_size: int = size
        self.successor_num = int(math.log2(self.chord_size))
        self.ip = None
        self.position: int = None

        self.predecessors = [[None] * 2 for _ in range(self.successor_num)]
        self.successors = [[None] * 2 for _ in range(self.successor_num)]
        self.routing_table = []
        self.btree: BTree = BTree(False)

    
    def initialize(self, flask_ip):
        self.ip = flask_ip
        self.position = helper.hash(self.ip, self.chord_size)
        powers_of_2 = [2 ** i for i in range(self.successor_num)]
        # First column is the position added by the power of two
        for i in range(self.successor_num):
            self.successors[i][0] = (self.position + powers_of_2[i]) % 16
            self.predecessors[i][0] = (self.position - powers_of_2[i]) % 16

        print("Successors: " + str(self.successors))
        print("======")
        print("Predecessors: " + str(self.predecessors))

        return "initialized\n"
    
    def first(self):
        for i in range(self.successor_num):
            self.successors[i][1] = self.position
            self.predecessors[i][1] = self.position
        print(self.successors)
        print(self.predecessors)
        return "first node joined\n"
    
    def join(self, host):
        response = requests.post(host + "/receive_info", json={"pos": self.position})
        # Process the response if needed
        return "bootstrap(data)"

    def receive_info(self, position):
            temp_suc = []
            temp_pre = []

            for i in range(self.successor_num):
                if self.position < position <= self.successors[i][0]:
                    self.successors[i][1] = position
                    temp_suc = self.successors[i][1]
                    break
                if self.predecessors[i][0] < position <= self.position:
                    self.predecessors[i][1] = position
                    temp_pre =  self.predecessors[i][1]
                    break

            print(self.successors)
            print(self.predecessors)

            result = {
                "successors": temp_suc,
                "predecessors": temp_pre
            }

            return json.dumps(result)