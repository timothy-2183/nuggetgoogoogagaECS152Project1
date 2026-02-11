import socket
import time

receiverip = "127.0.0.1"
receiverport = 5001
packet_sz = 1024
sequence_id_size = 4
data_sz = packet_sz-sequence_id_size
tp = []
ppd = []

cwnd = 1
ssthresh = 128

def send():
    starttp = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    # we always start from packet 0
    seqnum = 0
    unacked = {} #we're using a dictionary for tcp to track the individual time of the packets.
    more = True
    with open('file.mp3', 'rb') as f:
        while more or len(unacked)>0:
            while len(unacked) < cwnd:
                chunk = f.read(packet_sz-sequence_id_size)
                if not chunk:
                    more = False
                    break
                packet = seqnum.to_bytes(sequence_id_size, 'big') + chunk
                sock.sendto(packet, (receiverip, receiverport))
                unacked[seqnum] = (packet, time.time())
                seqnum+=len(chunk)
            # send everything, if success update the required stuff
            try:
                ackpacket, _ = sock.recvfrom(packet_sz)
                acknum = int.from_bytes(ackpacket[:sequence_id_size], 'big')
                rm_unacked = [pack for pack in unacked if pack + len(unacked[pack][0])-sequence_id_size <= acknum]
                for pack in rm_unacked:
                    ppd.append(time.time()-pack[1])
                    del unacked[pack]
                if cwnd < ssthresh:
                    cwnd=cwnd*2
                else: 
                    #bigger than ssthresh, but no congestion yet
                    cwnd+=1
            except socket.timeout:
                #congestion, drop everything
                ssthresh = max(cwnd//2,1) #check just in case it congests at like 1 lol
                cwnd = 1 
                #Stop here from last time, add an iterator to go through all of the previous packages
    eof_packet = seqnum.to_bytes(sequence_id_size, 'big')
    fin_received = False
    while not fin_received:
        sock.sendto(eof_packet,(receiverip, receiverport))
        print("exit")    
        try:
            packet, _ = sock.recvfrom(packet_sz)
            msg = packet[sequence_id_size:]
            if msg == b'fin': 
                fin_received = True
        except socket.timeout:
            pass
    finack = seqnum.to_bytes(sequence_id_size, 'big') + b'==FINACK=='
    sock.sendto(finack, (receiverip, receiverport))
    sock.close()
    
    endtp= time.time()
    tp.append(endtp-starttp)
def main():
    send()
    avgtp = sum(tp)/len(tp)
    avgppd = sum(ppd)/len(ppd)
    print(f"{avgtp:.7f}")
    print(f"{avgppd:.7f}")
    print(f"{0.3*avgtp/1000 + 0.7/avgppd:.7f}")

if __name__ == "__main__": main()