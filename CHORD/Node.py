from BTree import BTree
from Networking import randIP
class ChordNode:
    ip:str
    chord_position:int
    data:BTree
    successors=[]
    routingTable=[]
    chord_size:int

    def __init__(self,bootstrap_node=None):
        self.ip=randIP.generate_random_ip()
        if not (bootstrap_node is None):
            bootFlag=self.bootstap(bootstrap_node)
            if bootFlag:
                print("node"+ self.ip+"added to chord on position"+self.chord_position)

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

    def key_lookup(self,key):
        # find node that has or will save the key
        self.hash_function_key()
        #lookup node that hash func returns

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