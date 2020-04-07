import socket
import sys
import _thread
import time
import udt
import os
import packet

from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8081)
SENDER_ADDR = ('localhost', 0)
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5
#WINDOW_SIZE
N = 4 

# You can use some shared resources over the two threads
# Shared resources across threads
base = 0
next_seq_num = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)


# Need to have two threads: one for sending and another for receiving ACKs

# Send thread
def send(sock, file):
    sndpkt = []
    seq_num = 0
    next_seq_num = 0
    byte_index = 0
    global base
    try:
        with open(file, "rb") as data:
            byte_length = os.path.getsize(file)
            while byte_index <= byte_length:
                sndpkt.append(packet.make(seq_num, data.read(PACKET_SIZE)))
                seq_num += 1
                byte_index += PACKET_SIZE
    except IOError:
        print("File does not exist", file)
        return
    n = slide_window(len(sndpkt))
    _thread.start_new_thread(receive, (sock, ))
    while base < len(sndpkt):
        mutex.acquire()
        while(next_seq_num < base + n):
            udt.send(sndpkt[next_seq_num], sock, RECEIVER_ADDR)
            print("Sending packet number ", next_seq_num)
            next_seq_num += 1
        if not timer.running():
            timer.start()    
        while(timer.running() and not timer.timeout()):
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()
        if(timer.timeout()):
            timer.stop()
            next_seq_num = base
        else:
            n = slide_window(len(sndpkt))
        mutex.release()

    udt.send(packet.make_empty(), sock, RECEIVER_ADDR)
    data.close()




# Receive thread
def receive(sock):
	# Fill out the code here
    global base 
    while True:
        pkt, address = udt.recv(sock)
        ack_num, ack = packet.extract(pkt)

        print('Received ACK' , ack_num)
        if(ack_num >= base):
            mutex.acquire()
            base = ack_num + 1
            print('Base updated' , base)
            timer.stop()
            mutex.release()


def slide_window(packets):
    global base
    return min(N, packets - base)


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)
    filename = sys.argv[1]
    send(sock, filename)
    sock.close()


