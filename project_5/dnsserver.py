import socket
from struct import pack, unpack

class DNS:
    # self.name = None

    def __init__(self):
        self.addr = None
        self.ID = None
        self.question= None
        port = 50000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))

    # Send query to server / reply to client 
    def send(self):
        msg = self.make()
        print type(msg)
        self.socket.sendto(msg, self.addr)

    # Recv query from client / reply from server
    def recv(self):
        print 'recving'
        data, addr = self.socket.recvfrom(2048)
        print data, addr
        print 'done recving'
        self.addr = addr
        self.parse(data)

    # Make message for sending 

    # +---------------------+
    # | Header     |
    # +---------------------+
    # | Question   | the question for the name server
    # +---------------------+
    # | Answer     | Answers to the question
    # +---------------------+
    # | Authority  | Not used in this project
    # +---------------------+
    # | Additional | Not used in this project

    #
    #                            1 1 1 1 1 1
    #        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # | ID |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |QR| Opcode |AA|TC|RD|RA| Z | RCODE |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # | QDCOUNT |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # | ANCOUNT |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # | NSCOUNT |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # | ARCOUNT |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    def make(self):
        header = []
        header.append(self.ID)
        header.append(pack('!H', 0b1000000110000000))
        header.append(pack('!HHHH', 1, 1, 0, 0))
        header = ''.join(header)

        host = ['cs5700cdn', 'example', 'com']
	
        query = self.question

        aname = pack('!H', 0xc00c)
        tp = pack('!H', 1)
        cls = pack('!H', 1)

	ttl = pack('!I', 600)
    	rlen = pack('!H', 4)

        ip = '1.2.3.4'
        ipaddr = pack('!4s', socket.inet_aton(ip))
        answer = aname + tp + cls + ttl + rlen + ipaddr

	return header + query + answer 

    # Extra name from query
    def parse(self, msg):
        self.ID = msg[0:2]
        self.question = msg[12:]
        header = msg[0:12]
        print self.ID

def main():
    dns = DNS()
    dns.recv()
    dns.send()

if __name__ == '__main__':
    main()
