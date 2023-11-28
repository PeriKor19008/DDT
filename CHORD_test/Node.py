from B_tree import BTree
import random


class ChordRoutes:
    def __init__(self,ip,position,last_com):
        self.ip=ip
        self.position=position
        self.last_com=last_com

class ChordNode:
    ip:str
    chord_position:int
    data:BTree
    successors=[]
    routingTable=[]
    chord_size:int




    def bootstap(self, node: 'ChordNode'):
        data=node.insert_new_node(self.ip)
        self.chord_position=data[0]
        self.successors=data[1]
        self.chord_size=data[2]
        self.routingTable=self.init_routing_table()
        return 1


    def  hash_function_node(self,ip):
        h=0
        i=1
        for n in ip:
            h= h+n+(i*7)
            i=i+1
        return h % self.chord_size


    def hash_function_key(self):
        # hash func for key
        return -1

    def lookup(self,position):
        return -1

    def insert_data(self,key):
        # insert data to appropriate node
        self.key_lookup(key)
        #inset data to node returned

    def retrieve_data(self, key):
        # retrieve data from node that stores it
        self.key_lookup(key)
        #retrive data from node returned

    def store_data(self,key):
        # store data in local BTree
        # back up data to appropriate node
        return -1

    def get_stored_data(self,key):
        # return data stored in local BTree
        return -1

    def successors_maintance(self):
        # periodically run or provoked adhoc
        # update the successors list
        return -1

    def update_routing_table(self):
        # update the routing table
        return -1

    def init_routing_table(self):
        return -1

    def insert_new_node(self,ip):

        data=[]
        #hash ip of node to find its position
        data.append(self.hash_function_node(ip))
        #find its successors
        data.append(self.get_successors_of_node(data[0]))
        data.append(self.chord_size)

    # send data to node
        return data

    def depart_chord(self):
        # controlled departure from chord
        return -1

    def get_successors_of_node(self):
        successors=[]
        return successors


    def randIP(self):
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))









