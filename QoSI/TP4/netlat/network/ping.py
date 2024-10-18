#!/usr/bin/python3

from pythonping import ping
import pickle

class Ping:
    def __init__(self, hostname, count=10, request = False):
        self.sucess = False
        self.request = request
        self.rtt_avg = 0
        self.rtt_max = 0
        self.rtt_min = 0
        self.packets_sent = 0
        self.packets_returned = 0
        self.packet_loss = 0
        self.hostname = hostname
        self.count = count
        if not request:
            self.ping(hostname, count)

    def ping(self, hostname, count=10):
        try:
            response_list = ping(hostname, count=count)
            self.sucess = True
            self.rtt_avg = response_list.rtt_avg
            self.rtt_max = response_list.rtt_max
            self.rtt_min = response_list.rtt_min
            self.packets_sent = response_list.stats_packets_sent
            self.packets_returned = response_list.stats_packets_returned
            self.packet_loss = response_list.stats_packets_sent - response_list.stats_packets_returned

        except Exception as e:
            pass
        return self


    def to_dict(self):
        json_object = {}
        for field in self.__dict__:
            json_object[field] = self.__dict__[field]
        return json_object


    @staticmethod
    def from_dict(json_object):
        ping = Ping(json_object["hostname"], request=True)
        for field in json_object:
            setattr(ping, field, json_object[field])
        return ping


    def encode(self):
        json_object = {}
        for field in self.__dict__:
            json_object[field] = self.__dict__[field]
        return pickle.dumps(json_object)


    @staticmethod
    def decode(bits):
        json_object = pickle.loads(bits)
        ping = Ping(json_object["hostname"], request=True)
        for field in json_object:
            ping.__dict__[field] = json_object[field]
        return ping

    def __str__(self):
        string = "PING: {"
        for field in self.__dict__:
            string += f"{field}: {self.__dict__[field]}, "
        string = string[:-2]
        string += "}"
        return string

