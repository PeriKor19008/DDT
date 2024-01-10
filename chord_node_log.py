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
        file = open("/log/log"+node.ip.replace(".","_").replace(":","_").replace("/" , "_")+"_routes.txt", 'w')
        file.write("SUCCESSORS \n")
        for succ in node.successors:
            file.write("succ position: "+str(succ.position)+"---succ ip: "+succ.ip+"")
        file.write("SUCCESSORS \n------\n\n\nPREDECESSORS\n")
        for pre in node.predecessors:
            file.write("pre position: "+str(pre.position)+"---pre ip: "+pre.ip)
        file.write("PREDECESSORS\n-----\n\n\nROUTING TABLE\n")
        for route in node.routing_table:
            file.write("route position: "+str(route.position)+"---route ip: "+route.ip)

