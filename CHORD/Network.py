from Node import ChordNode

class Network_Handler:

    nodes=[]
    def __init__(self):
        print("Network is running")

    def make_node(self):
        self.nodes.append(ChordNode(self))

    def get_node_via_ip(self,ip):
        node: ChordNode
        for node in self.nodes:
            if node.get_ip()==ip:
                return ip

        return -1
    def send_message(self,sender:ChordNode,dst_ip:str,message):
        dst_node:ChordNode=self.get_node_via_ip(dst_ip)
        if dst_node != -1:
            dst_node.receive_message(sender.get_ip(),message)


