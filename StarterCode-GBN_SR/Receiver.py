# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)


# Receive packets from the sender
def receive(sock, filename):
   # fill your code here
    try:
        f = open(filename, 'wb2')
    except IOError:
        print('could not open: ', filename)
        return
    
    n=0

    while True:
        p = udt.rcv(sock)
        if not p:
            break
        sequence_num = packet.extract(p)
        data = packet.extract(p)

        if sequence_num == n:
    	    p = packet.make(n)
    	    print('received packet')
    	    address = udt.rcv(sock)
    	    udt.send(p,sock,address) 
    	    n = n+1
    	    f.write(data)
        else:
            p = packet.make(n-1)
            udt.send(p,sock,address)

    file.close


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    filename = sys.argv[1]
    receive(sock, filename)
    sock.close()