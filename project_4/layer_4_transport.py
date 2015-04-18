# Layer_4_Transport
import random
import socket
import time
from struct import pack, unpack
from layer_3_networks import IP


class TCP:

    def __init__(self):
        # initialize port and ip
        self.src_port = 60000 + random.randrange(0, 1000)
        self.dst_port = 80
        self.src_ip = ''
        self.dst_ip = ''

        # TCP header fields
        self.seq = random.randrange(0, 1000000)
        self.ack_seq = 0
        self.data_offset = 5

        # flags
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0

        self.window = 4096
        self.c_wnd = 1
        self.urg_ptr = 0

        self.data = ''
        self.request = ''
        self.request = ''
        self.dataReceived = []

        # use IP in network layer
        self.ip = IP()

    """Public Function of HTTP """

    def set_ip_address(self, src_ip, dst_ip):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ip.set_ip_address(src_ip, dst_ip)

    def set_request(self, request):
        self.request = request

    def run(self):
        self._setup_connection()
        self._transmit_data()
        self._teardown_connection()

    def data_collected(self):
        return ''.join(self.dataReceived)

    """Private Function of HTTP """

    def _setup_connection(self):
        # client first send
        self.syn = 1
        self._send_segment()

        # receive from sever
        self._receive_segment()
        self.syn = 0
        self.ack = 1
        self.seq += 1
        self.ack_seq += 1

        # client second send
        self._send_segment()

    def _transmit_data(self):
        # send request, passed from HTTP
        self._send_request()
        self._receive_segment()

        # receive data from server
        while self.fin != 1:
            self._send_segment()
            self._receive_segment()

    def _teardown_connection(self):
        # receive FIN flag, tear down connection now
        self.ack_seq += 1
        self._send_segment()
        self._receive_segment()

    def _send_request(self):
        while len(self.request) > 0:
            wnd = min(self.window, self.c_wnd)
            self.data = self.request[:wnd]

            self._send_segment()
            self._receive_segment()

    def _send_segment(self):
        hdr = self._make_header()
        self.ip.send_packet(hdr + self.data)

    def _receive_segment(self):
        pkt = None
        while True:
            if pkt is not None:
                break

            start = time.time()

            while pkt is None:
                if time.time() - start > 60000:
                    self._send_segement()

                pkt = self.ip.receive_packet()
                pkt = self._parse_segment(pkt)

    def _make_header(self):

        #    0                   1                   2                   3
        #    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |          Source Port          |       Destination Port        |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |                        Sequence Number                        |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |                    Acknowledgment Number                      |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |  Data |           |U|A|P|R|S|F|                               |
        #   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
        #   |       |           |G|K|H|T|N|N|                               |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |           Checksum            |         Urgent Pointer        |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |                    Options                    |    Padding    |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #   |                             data                              |
        #   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #
        #                            TCP Header Format

        tcp_flags = self.fin
        tcp_flags += (self.syn << 1)
        tcp_flags += (self.rst << 2)
        tcp_flags += (self.psh << 3)
        tcp_flags += (self.ack << 4)
        tcp_flags += (self.urg << 5)

        offset_flags = (self.data_offset << 12) + 0 + tcp_flags

        tcp_header = pack('!HHLLHHHH',
                          self.src_port, self.dst_port,
                          self.seq,
                          self.ack_seq,
                          offset_flags, self.window,
                          0, self.urg_ptr)

        # pseudo header
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header) + len(self.data)
        
        psh = pack('!4s4sBBH',
                   socket.inet_aton(self.src_ip),
                   socket.inet_aton(self.dst_ip),
                   0,
                   protocol,
                   tcp_length)

        # get checksum
        chk = self._checksum(psh + tcp_header + self.data)

        # get REAL header
        tcp_header = pack('!HHLLHH',
                          self.src_port, self.dst_port,
                          self.seq,
                          self.ack_seq,
                          offset_flags, self.window) + pack('H', chk) + pack('!H', self.urg_ptr)

        return tcp_header

    def _parse_segment(self, packet):
        # unpack packet
        (src_port,
         dst_port,
         seq,
         ack_seq,
         offset_rsv, flags, windown,
         chk,
         urg_ptr) = unpack('!HHLLBBHHH', packet[0:20])

        hdr = pack('!HHLLBBHHH',
                   src_port,
                   dst_port,
                   seq,
                   ack_seq,
                   offset_rsv, flags, windown,
                   0,
                   urg_ptr)

        # pseudo header
        protocol = socket.IPPROTO_TCP
        tcp_length = len(hdr) + len(packet[20:])

        psh = pack('!4s4sHH',
                   socket.inet_aton(self.dst_ip),
                   socket.inet_aton(self.src_ip),
                   protocol,
                   tcp_length)

        # get checksum
        check = self._checksum(psh + hdr + packet[20:])
    
        flags = '{0:08b}'.format(flags)[2:]
        urg, ack, psh, rst, syn, fin = flags

        self.fin = int(fin)

        data_size = len(packet) - 20
        data = packet[20:]


        # change acknowledgement sequence
        if self.ack_seq == 0:
            self.ack_seq = seq
        elif self.ack_seq == seq:
            self.ack_seq += data_size

        # change sequence
        if self.seq + len(self.data) == ack_seq:
            data_len = len(self.data)
            wnd = min(self.window, self.c_wnd)
            self.data = ''
            self.request = self.request[wnd:]
            self.seq = ack_seq
            self.dataReceived.append(data)
            if self.c_wnd + data_len <= 1000:
                self.c_wnd += data_len
        else:
            self.c_wnd = 1

        # return packet of the src port
        if src_port == self.dst_port and \
           dst_port == self.src_port and \
           pack('!H', chk) == pack('H', check) :
            return packet

    def _checksum(self, msg):
        s = 0
        if len(msg) % 2 != 0:
            msg += pack('B', 0)

        for i in range(0, len(msg), 2):
            w = ord(msg[i]) + (ord(msg[i+1]) << 8)
            s = s + w

        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)

        s = ~s & 0xffff

        return s

if __name__ == '__main__':
    main()
