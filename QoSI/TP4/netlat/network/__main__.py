#!/usr/bin/python3
from network import Ping, Traceroute, TCP_, UDP_, public_ip


if __name__ == '__main__':
    ping = Ping("mayorx.xyz")
    print(ping)

    traceroute = Traceroute("www.example.com")
    print(traceroute)

    traceroute = Traceroute("mayorx.xyz", version = UDP_)
    print(traceroute)

    public_ip = public_ip()
    print(public_ip)



