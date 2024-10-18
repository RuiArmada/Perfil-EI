import time
from sniffing import DNS_Sniffer

if __name__ == "__main__":
    ## if this module is run as a script it will run in debug mode
    debug = True

    interface = input("Enter the interface to sniff on: ")
    dns_sniffer = DNS_Sniffer(interface,debug)
    dns_sniffer.start()
