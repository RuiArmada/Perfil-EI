#!/usr/bin/python3

from scapy.all import *

TCP_ = "TCP"
UDP_ = "UDP"

class Traceroute:

    TCP_PAYLOAD = None
    UDP_PAYLOAD = UDP(sport=RandShort())/DNS(qd=DNSQR(qname="1.1.1.1"))

    def __init__(self, hostname, maxttl=30,version=TCP_):
        self.sucess = False
        self.hostname = hostname
        self.ip = self.resolve_hostname(hostname)
        self.result = []
        self.ttl = maxttl
        self.version = version
        self.result = []
        self.unans = []
        self.sucess = False
        self.ip_raw_send()


    def resolve_hostname(self,hostname):
        try:
            resolved_addresses = socket.gethostbyname_ex(hostname)[2]
            return resolved_addresses
        except socket.gaierror:
            return []


    def to_dict(self):
        json_object = {}
        for field in self.__dict__:
            json_object[field] = self.__dict__[field]
        return json_object


    @staticmethod
    def from_dict(json_object):
        ping = Traceroute(json_object["hostname"])
        for field in json_object:
            setattr(ping, field, json_object[field])
        return ping


    def ip_raw_send(self):
        if self.hostname.count('.') == 3:
            self.ip = self.hostname
        max_ttl = self.ttl
        for ttl in range(1, max_ttl + 1):
            # Choose the packet type based on the use_tcp flag
            if self.version == TCP_:
                port = 80
                pkt = IP(dst=self.ip, ttl=ttl) / TCP(dport=port, flags="S")
            else:
                port = 5060
                pkt = IP(dst=self.ip, ttl=ttl) / UDP(dport=port, sport=RandShort()) / self.UDP_PAYLOAD
            
            # Send the packet and wait for a reply
            reply = sr1(pkt, verbose=0, timeout=1)
            if reply is None:
                self.sucess = False
                self.unans.append(ttl)
            else:
                # Check if the reply is from the target
                if reply.src in self.ip:
                    self.sucess = True
                    self.result.append(reply.src)
                    break
                else:
                    self.sucess = False
                    self.result.append(reply.src)
        else:
            self.sucess = False

        return self

    def __str__(self):
        string = "TRACEROUTE: {"

        for field in self.__dict__:
            string += f"{field}: {self.__dict__[field]}, "

        string = string[:-2]
        string += "}"
        return string
