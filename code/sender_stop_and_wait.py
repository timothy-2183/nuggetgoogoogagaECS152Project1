import socket
import time
# create socket outside because we can always reuse, also set timeout.

receiverip = "127.0.0.1"
receiverport = "5001"
packet_sz = 1024 # we read 1024 bytes
sequence_id_size = 4
tp = []
ppd = []

def send():
    starttp = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    with open('docker\file.mp3', 'read') as f:
        # we always start from packet 0
        seqnum = 0
        while True:
            chunk = f.read(packet_sz) 
            if not chunk:
                break
            # as of right noe we have the individual chunks of the data in 1024 bytes, now we can send
            packet = sequence_id_size.to_bytes(sequence_id_size, 'big') + chunk
            ackget =  False
            startppd = time.time()
            while not ackget:
                #send here regardless of outcome
                sock.sendto(packet,(receiverip, receiverport))
                try:
                    #wait until u receive something
                    ackpacket, _ = sock.recvfrom(packet_sz)
                    acknum = int.from_bytes(ackpacket[:sequence_id_size], 'big')
                    #if correct, u just add smth more if not then just do nothing because the while will just retransmit
                    if acknum == (seqnum + len(chunk)):
                        ackget = True
                        seqnum += len(chunk)
                        endppd = time.time()
                        ppd.append(endppd-startppd)
                    
                except socket.timeout:
                    pass
    sock.close()
    endtp= time.time()
    tp.append(endtp-starttp)
def main():
    for _ in range(10):
        send()
    avgtp = sum(tp)/len(tp)
    avgppd = sum(ppd)/len(ppd)
    print(avgtp)
    print(avgppd)
    print(0.3*avgtp/1000 + 0.7/avgppd)