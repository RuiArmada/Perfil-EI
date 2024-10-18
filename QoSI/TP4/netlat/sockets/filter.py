from scapy.all import sniff, IP, TCP, UDP
from sockets import Definitions, Payload

class Filter:
    def __init__(self):
        self.packet_info = {}
        
    def handle_packet(self,packet):
        if packet.haslayer(IP) and (packet.haslayer(TCP) or packet.haslayer(UDP)):
            try:
                payload_data = bytes(packet[TCP].payload) if packet.haslayer(TCP) else bytes(packet[UDP].payload)
                starting_byte = payload_data.find(Definitions.PAYLOAD_START)
                payload_data = payload_data[starting_byte:]
                payload = Payload.deserialize(payload_data)
            except:
                payload = None
            if payload:
                packet_ports = (packet[TCP].sport, packet[TCP].dport) if packet.haslayer(TCP) else (packet[UDP].sport, packet[UDP].dport)
                # Store packet data or summary for later use
                key = (payload.from_, packet_ports[1], "server", packet_ports[0])
                self.packet_info[key] = packet

    def filter_packet(self, interface="lo"):
        # Define the ports you're interested in
        port_filter = " or ".join([f"port {port}" for port in Definitions.PORTS_TO_MONITOR])
        # Start sniffing with filter
        sniff(filter=port_filter, prn=self.handle_packet,iface=interface)
