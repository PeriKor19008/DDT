from datetime import datetime

class ChordNodeLog:
    def log(self, mess: str, ip: str) -> None:
        file = open("/log/log.txt", 'a')
        time = datetime.now()

        if "bootstrap" in mess:
            file.write(ip + "----" + mess + "-----" + time.strftime("%Y-%m-%d %H:%M:%S") + '\n'
                       + "-------" + "\n"
                       + "--------" + "\n"
                       + "success on join\n\n\n")
        else:
            file.write(ip + "----" + mess + "-----" + time.strftime("%Y-%m-%d %H:%M:%S") + '\n'
                       + "-------" + "\n"
                       + "--------" + "\n")

    def log_routes(self, node) -> None:
            print("--------------------------------------------------------\n")
            print("self position ="+ str(node.position) +"\nself ip =" + str(node.ip))
            print("SUCCESSORS \n")
            for succ in node.successors:
                print("succ position: "+str(succ.position)+"---succ ip: "+succ.ip+"\n")
            print("SUCCESSORS \n------\n\n\nPREDECESSORS\n")

            print("pre position: " + str(node.predecessor.position) + "---pre ip: " + node.predecessor.ip + "\n")
            print("PREDECESSORS\n-----\n\n\nROUTING TABLE\n")
            if node.routing_table:
                for route in node.routing_table:
                    print("route position: "+str(route.position)+"---route ip: "+route.ip+"\n")
            print("--------------------------------------------------------\n")

