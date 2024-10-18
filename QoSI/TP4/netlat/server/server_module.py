import os
import threading

from sockets import *
from spawner import DigitalOceanSpawner
from utilities import Timestamp


class Server():
    def __init__(self, interface, launch_options, spawn=False):

        def validate_path(path):
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
 
        self.start_time = Timestamp.get_formatted().replace(" ","_").replace(":","h")
        validate_path("logs/")
        self.log = open(f"logs/log_server_{self.start_time}.txt", "w")
        self.__log__(f"Server started at {self.start_time}")
        self.__log__(f"Server configuration: {interface} {launch_options} {spawn}")
        self.interface = interface
        self.launch_options = launch_options
        self.spawn_droplets = spawn
        self.threads = []
        self.filter = Filter()

        self.threads.append(threading.Thread(name="Packet_Filter",target=self.filter.filter_packet, args=(self.interface,)))

        self.socks = {}
        for port in Definitions.PORTS_TO_MONITOR:
            if port == 8080:
                protocol = Definitions.TCP
            else:
                protocol = Definitions.UDP

            self.socks[port] = Sopc(port,protocol)
            self.threads.append(threading.Thread(name=f"Socket_port_{port}",target=self.save_information,args=(self.socks[port],)))

        self.data_port = Sopc(Definitions.DATA_PORT, Definitions.UDP)
        self.threads.append(threading.Thread(name="Save_data",target=self.save_data))

    def __log__(self, message):
        self.log.write(f"{Timestamp.get_timestamp()} - {message}\n")
        self.log.flush()

    def run(self):
        for thread in self.threads:
            self.__log__(f"Starting thread {thread.name}")
            thread.start()
        if self.spawn_droplets:
            self.__log__(f"Spawning droplets")
            self.spawner = DigitalOceanSpawner(self.launch_options)
        else:
            self.spawner = None

    def save_information(self,socket):
        while True:
            payload, key, timestamp = socket.recv()
            self.__log__(f"Received information packet from {key}")
            sucess = False
            start_index_my_payload = payload.find(Definitions.PAYLOAD_START)
            payload = payload[start_index_my_payload:]
            try:
                data = Payload.deserialize(payload)
                key = ((data.from_,key[0][1]),("server",key[1][1]))
                sucess = True
                self.__log__(f"Deserialized payload from {key}")
            except Exception as e:
                error = "Could not deserialize payload because of: " + str(e)
                self.__log__(f"Could not deserialize payload from {key}")
                self.__log__(error)
            if sucess:
                Save.process_packet(payload, key, timestamp,self.filter)
                self.__log__(f"Processed packet from {key}")

    def save_data(self):
        while True:
            payload,_,_ = self.data_port.recv()
            self.__log__(f"Received misc data packet")
            sucess = False
            start_index_my_payload = payload.find(Definitions.PAYLOAD_START)
            payload = payload[start_index_my_payload:]
            try:
                _ = Payload.deserialize(payload)
                self.__log__(f"Deserialized data payload")
                sucess = True
            except Exception as e:
                error = "Could not deserialize payload because of: " + str(e)
                self.__log__(f"Could not deserialize data payload")
                self.__log__(error)
            if sucess:
                Save._data(payload)
                self.__log__(f"Saved data payload")
