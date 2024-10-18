from scapy.all import sniff, DNS, DNSQR  # Import IP here
import threading

# DNS Sniffer class
class DNS_Sniffer(threading.Thread):
    def __init__(self, interface="eth0",debug=False):
        super(DNS_Sniffer, self).__init__()
        self.interface = interface
        self.dns_dict = set()
        self.debug = debug

    def dns_packet(self, packet):
        if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:  # DNS queries only
            if packet[DNSQR].qname.endswith(b".media."):
                # write ip to dictionary
                self.dns_dict.add(packet[DNSQR].qname.decode())
                if self.debug:
                    print(f"DNS Query: {packet[DNSQR].qname.decode()}")

    def capture_dns(self):
        sniff(filter="port 53", prn=self.dns_packet, iface=self.interface, store=False)

    def run(self):
        self.capture_dns()
