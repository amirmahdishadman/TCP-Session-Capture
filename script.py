import os
import subprocess
import sys
import re
import bt2
import datetime
import json
import ast
import matplotlib.pyplot as plt
import numpy as np

# trace = str((subprocess.run(["babeltrace2","-v","convert",sys.argv[1]],capture_output=True)).stdout)[2:].split("\\n")[:-1]

def network_headder_to_json(network_headder):
    network_headder_str=str(network_headder)
    network_headder_str=network_headder_str.replace("\'","\"")
    network_headder_str=network_headder_str.replace(" (_tcp)","")#6
    network_headder_str=network_headder_str.replace(" (_udp)","")#17
    network_headder = json.loads((network_headder_str))
    return network_headder

connecting=[]
connections=[]

trace=bt2.TraceCollectionMessageIterator(sys.argv[1])
for msg in trace:
    if type(msg) is bt2._EventMessageConst:
        ns_from_origin = msg.default_clock_snapshot.ns_from_origin
        dt = datetime.datetime.fromtimestamp(ns_from_origin / 1e9)
        try:
            if((msg.event.name)=="net_if_receive_skb"):
                if(msg.event.payload_field['network_header_type']==1):
                    if(msg.event.payload_field['network_header']!={}):
                        json_network_headder=network_headder_to_json(msg.event.payload_field['network_header'])
                        if(json_network_headder["transport_header"]["flags"]==2):
                            connecting.append({'connection_number':"connection "+str(len(connecting)+len(connections)+1),'cilent_ip':json_network_headder["saddr"],'server_ip':json_network_headder["daddr"],'client_port':json_network_headder["transport_header"]["source_port"],"status":"syn",'server_port':json_network_headder["transport_header"]["dest_port"],"syn-time":dt})
                            # print(connecting)

            if((msg.event.name)=="net_dev_queue"):
                if(msg.event.payload_field['network_header_type']==1):
                    if(msg.event.payload_field['network_header']!={}):
                        json_network_headder=network_headder_to_json(msg.event.payload_field['network_header'])
                        if(json_network_headder["transport_header"]["flags"]==18):
                            my_connecting = next((index for (index, d) in enumerate(connecting) if d["client_port"] == json_network_headder["transport_header"]["dest_port"] and d["server_port"] == json_network_headder["transport_header"]["source_port"]), None)
                            connecting[my_connecting]["status"]="syn -> syn-ack"
                            connecting[my_connecting]["syn-ack-time"]=dt
                            # print(connecting)

            if((msg.event.name)=="net_if_receive_skb"):
                if(msg.event.payload_field['network_header_type']==1):
                    if(msg.event.payload_field['network_header']!={}):
                        json_network_headder=network_headder_to_json(msg.event.payload_field['network_header'])
                        if(json_network_headder["transport_header"]["flags"]==16):
                            my_connecting = next((index for (index, d) in enumerate(connecting) if d["client_port"] == json_network_headder["transport_header"]["source_port"] and d["server_port"] == json_network_headder["transport_header"]["dest_port"]), None)
                            connecting[my_connecting]["status"]="syn -> syn-ack -> ack"
                            connecting[my_connecting]["ack-time"]=dt
                            # print(connecting)
                            connections.append(connecting[my_connecting])
                            del connecting[my_connecting]
                            # print(connecting)
                            # print(connections)
        except:
            pass



print("list of in 3way handshake connections: #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#\n")
for item in connecting:
    print(item)
    print("\n------------------------------------------------\n")



print("list of established connections: #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#\n")
for item in connections:
    print(item)
    print("\n------------------------------------------------\n")



min=int(min([float('%02d.%d'%(item["syn-time"].second,item["syn-time"].microsecond)) for item in connections]))
max=int(max([float('%02d.%d'%(item["ack-time"].second,item["ack-time"].microsecond)) for item in connections]))


species = (item["connection_number"] for item in connections)
penguin_means = {
    'syn': [float('%02d.%d'%(item["syn-time"].second,item["syn-time"].microsecond)) for item in connections],
    'syn-ack': [float('%02d.%d'%(item["syn-ack-time"].second,item["syn-ack-time"].microsecond)) for item in connections],
    'ack': [float('%02d.%d'%(item["ack-time"].second,item["ack-time"].microsecond)) for item in connections],
}
x = np.arange(len(connections))
multiplier = 0
width = 0.3
fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in penguin_means.items():
    offset = width * multiplier
    rects = ax.barh(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1


ax.set_xlabel('time(sec)')
ax.set_title('connections')
ax.set_yticks(x + width, species)
ax.legend(loc='upper left')
ax.set_xlim(min, max)
plt.show()



# penguin_means = {
#     'Bill Depth': (18.35, 18.43, 14.98),
#     'Bill Length': (38.79, 48.83, 47.50),
#     'Flipper Length': (189.95, 195.82, 217.19),
# }

  # the label locations
  # the width of the bars






# Add some text for labels, title and custom x-axis tick labels, etc.

# for msg in bt2.TraceCollectionMessageIterator(sys.argv[1]):
#     if type(msg) is bt2._EventMessageConst:
#         print(msg.event.name)



# connections=[]



# syn_list=[]
# syn_ack_list=[]
# ack_list=[]

# for item in trace:
#     is_syn = re.search("^.*net_if_receive_skb.*flags = 0x2.*$", item)
#     if(is_syn): 
#         syn_list.append(item)

#     is_syn_ack = re.search("^.*net_dev_queue.*flags = 0x12.*$", item)
#     if(is_syn_ack): 
#         syn_ack_list.append(item)

#     is_ack = re.search("^.*net_if_receive_skb.*flags = 0x10.*$", item)
#     if(is_ack): 
#         ack_list.append(item)

# print("syn-list:\n\n")
# print(syn_list)

# print("\n-------------------------------------------------\n")
# print("syn-ack-list:\n\n")

# print(syn_ack_list)

# print("\n-------------------------------------------------\n")

# print("ack-list:\n\n")

# print(ack_list)



# for item in trace:
#     if "net_if_receive_skb" in item:
#         print(item)