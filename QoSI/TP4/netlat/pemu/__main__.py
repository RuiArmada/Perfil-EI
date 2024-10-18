#!/usr/bin/python3

from pemu import Packet
from network import Ping
from sockets import Definitions


if __name__ == '__main__':
    Packet.send_http_get(Definitions.C2_SERVER_, 8080)

    Packet.send_sip_invite(Definitions.C2_SERVER_)
    
    Packet.send_dns_request(Definitions.C2_SERVER_)
    
    Packet.send_rtp_packet(Definitions.C2_SERVER_)

    ping = Ping("www.google.com", request=True).to_dict()
    ping['type_'] = Definitions.Messages.PING_REQUEST
    ping['from_'] = "zephyrus"
    Packet.send(Definitions.C2_SERVER_, ping )

    response = Ping("www.google.com").to_dict()
    response['type_'] = Definitions.Messages.PING_RESPONSE
    response['from_'] = "zephyrus"
    Packet.send(Definitions.C2_SERVER_, response)
    
    Packet.send(Definitions.C2_SERVER_, {"type_": "UDP", "data": "Test Packet", "from_": "zephyrus"})



