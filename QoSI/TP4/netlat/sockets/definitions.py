class Definitions:
    C2_SERVER_ = "mayorx.xyz"
    C2_SERVER_IP = "94.61.65.80"
    SERVER = 0
    CLIENT = 1
    PORTS_TO_MONITOR = [8080, 53, 5004, 5060]
    DATA_PORT = 4000
    TCP = 0
    UDP = 1
    PAYLOAD_START = b"\x80\x04"
    
    class Messages:
        PING_REQUEST = "PING_REQUEST"
        PING_RESPONSE = "PING_RESPONSE"
        NETWORK_SHAPPING = "NETWORK_SHAPPING"
        TRACEROUTE = "TRACEROUTE"

