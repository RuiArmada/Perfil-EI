#from netlat.sockets import C2_SERVER
import threading
import sockets 

if __name__ == "__main__":
    print("NetLat v0.1")
    print(sockets.Definitions.C2_SERVER)
    # Usage example
    socket_s = sockets.Sopc(8080, sockets.Definitions.TCP)
    filter = sockets.Filter()
    thread = threading.Thread(target=filter.filter_packet(), args=())
    thread.start()
