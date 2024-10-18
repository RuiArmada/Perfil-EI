#!/usr/bin/python3

from scapy.all import *
import socket
import random

from utilities import Timestamp
from sockets import Payload

def create_payload(type_, tos=0):
    extra = Payload({"from_": socket.gethostname(),"timestamp":Timestamp.get_timestamp(), "tos":tos, "type_":type_})
    return extra.serialize()

def serialize_payload(data):
    data = Payload(data)
    return data.serialize()

class Packet:
    @staticmethod
    def send(address, data):
        if type(data) != dict or "type_" not in data:
            raise ValueError("Data must be a dictionary object with a 'type_' attribute or a Payload object.")
        if type(data) == dict:
            serialized_data = serialize_payload(data)
        else:
            raise ValueError("Data must be a dictionary object with a 'type_' attribute or a Payload object.")

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # The source port is set to 10000 and destination port is set to 4000
        sock.bind(('', 10000))  # Bind to the source port
        try:
            sock.sendto(serialized_data, (address, 4000))
        except Exception as e:
            print(f"Error sending packet to {address}")
        sock.close()
            
    @staticmethod
    def send_sip_invite(address):
        # DSCP for Expedited Forwarding
        dscp_ef = 46  # EF
        tos = dscp_ef << 2  # Shift left by 2 bits to fit into the 8-bit field
        sip_request = (
            f"INVITE sip:bot@mayorx.xyz SIP/2.0\n"
            f"Via: SIP/2.0/UDP {socket.gethostname()};branch=z9hG4bK-524287-1---3c4b757e34de6a70;rport\n"
            f"From: <sip:{socket.gethostname()}@mayorx.xyz>;tag=7743\n"
            f"To: sip:bot@mayorx.xyz\n"
            f"Call-ID: 9876543210@mayorx.xyz\n"
            f"CSeq: 1 INVITE\n"
            f"Content-Length: {len(create_payload('SIP'))}\n"
            f"\r\n"
        ).encode('utf-8') + create_payload('SIP', tos)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the IP TOS/DSCP value
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)
        try:
            sock.sendto(sip_request, (address, 53))
        except Exception as e:
            print(f"Error sending {e}")
            print(f"Error sending SIP request")
        sock.close()

    @staticmethod
    def send_http_get(address, port):
        http_request = (
            b"GET / HTTP/1.1\r\n"
            b"Host: " + socket.gethostname().encode() + b"\r\n"
            b"User-Agent: PythonSocket\r\n"
            b"\r\n"
        ) + create_payload('HTTP')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((address, port))
            sock.sendall(http_request)
        except Exception as e:
            print(f"Error sending {e}")
            print(f"Error sending HTTP request")
        sock.close()

    @staticmethod
    def send_rtp_packet(address):
        # DSCP for Expedited Forwarding
        dscp_ef = 46  # EF
        tos = dscp_ef << 2  # Shift left by 2 bits to fit into the 8-bit field
        rtp_packet = bytearray([
            0x80, 0x60, 0x03, 0xe8,  # Version, Payload Type, Sequence Number
            0x00, 0x00, 0x00, 0x64,  # Timestamp
            0x00, 0x00, 0x00, 0x01,  # SSRC
        ]) + create_payload('RTP', tos)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the IP TOS/DSCP value
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)
        try:
            sock.sendto(rtp_packet, (address, 53))
        except Exception as e:
            print(f"Error sending {e}")
            print(f"Error sending RTP packet")
        sock.close()

    @staticmethod
    def send_dns_request(address):
        dns_query = (
            b'\xaa\xaa'  # Transaction ID
            b'\x01\x00'  # Flags: Standard query
            b'\x00\x01'  # Questions: 1
            b'\x00\x00'  # Answers: 0
            b'\x00\x00'  # Authority RRs: 0
            b'\x00\x00'  # Additional RRs: 0
            b'\x07mayorx\x02xyz\x00'  # Query Name: mayorx.xyz
            b'\x00\x01'  # Type: A
            b'\x00\x01'  # Class: IN
        ) + create_payload('DNS')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(dns_query, (address, 53))
        except Exception as e:
            print(f"Error sending {e}")
            print(f"Error sending DNS request")
        sock.close()
