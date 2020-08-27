import sys
sys.path.append(".")

from opcua import Client
import yaml

if __name__ == '__main__':
    client = Client("opc.tcp://192.168.3.81:49380/freeopcua/server/")
    # client = Client("opc.tcp://192.168.3.81:49380/")
    try:
        client.connect()
        root = client.get_root_node()
        print("Objects node is: ", root)
        print("Children of root are: ", root.get_children())
        obj = client.get_objects_node().get_children()
        ooo = []
        for a in obj:
            if a!='':
                b = a.get_children()
                ooo.extend(b)
            else:
                ooo.append(a)
        print(ooo, len(ooo))
    finally:
        client.disconnect()
