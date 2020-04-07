# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8081)
#WINDOW SIZE
N = 4




base = 0

# Receive packets from the sender
def receive(sock, filename):
    global base
    global N
    
   # fill your code here
    try:
        f = open(filename, 'wb')
    except IOError:
        print('could not open: ', filename)
        return

    while(base < base + N -1):
        pkt, address = udt.recv(sock)
        print('Receiving packet from ', address)
        if not pkt:
            break
        seq_num, data = packet.extract(pkt)
        print('We just received sequence number ', seq_num, '\n')
        print(data , '\n')
        if seq_num == base:
    	    ack_pkt = packet.make(seq_num)
    	    print('made an ack packet and read to send! \n')
    	    udt.send(ack_pkt, sock, address) 
    	    base = base+1
    	    f.write(data)
    f.close()


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