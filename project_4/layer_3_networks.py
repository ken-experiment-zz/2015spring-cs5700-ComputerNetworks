# Layer_3_Networks
import socket
import time
from struct import pack, unpack
from layer_2_data_link import Ethernet


class IP:

    def __init__(self):
        # IP addr initialzation
        # 00.00.00.00 format
        self.src_ip = ''
        self.dst_ip = ''
        
        # packet
        self.pkt = ''

        # use Ethernet
        self.ethernet = Ethernet()

    """Public Function of IP"""

    def set_ip_address(self, src_ip, dst_ip):
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def send_packet(self, pkt):
        self.pkt = pkt
        hdr = self._make_header(pkt)
        self.ethernet.send_frame(hdr + pkt)

    def receive_packet(self):
        pkt = None
        while True:
            if pkt is not None:
                break

            start = time.time()

            while pkt is None:
                if time.time() - start > 60000:
                    self.send_packet(self.pkt)

                pkt = self.ethernet.receive_frame()
                pkt = self._parse_packet(pkt)

        return pkt

    """Private Function of IP"""

    def _make_header(self, pkt):
        # ip header fields
        ihl = 5
        ver = 4
        ihl_ver = (ver << 4) + ihl
        tos = 0
        tot_len = len(pkt) + 20
        pkt_id = 22345
        frag_off = 0
        ttl = 255
        proto = socket.IPPROTO_TCP
        check = 0
        saddr = socket.inet_aton(self.src_ip)
        daddr = socket.inet_aton(self.dst_ip)

        # the ! in the pack format string means network order
        header = pack('!BBHHHBBH4s4s',
                      ihl_ver, tos,
                      tot_len,
                      pkt_id,
                      frag_off,
                      ttl, proto,
                      0,             # checksum is 0
                      saddr,
                      daddr)

        check = self._checksum(header)

        header = pack('!BBHHHBBH4s4s',
                      ihl_ver, tos,
                      tot_len,
                      pkt_id,
                      frag_off,
                      ttl, proto,
                      check,
                      saddr,
                      daddr)

        return header

    def _parse_packet(self, packet):
        # take first 20 characters for the ip header
        header = packet[:20]

        # now unpack them :)
        iph = unpack('!BBHHHBBH4s4s', header)

        protocol = iph[6]
        chk = iph[7]
        src_addr = socket.inet_ntoa(iph[8])
        dst_addr = socket.inet_ntoa(iph[9])

        new_hdr = pack('!BBHHHBBH4s4s', iph[0], iph[1], iph[2], iph[3], iph[4], iph[5], iph[6], 0, socket.inet_aton(src_addr), socket.inet_aton(dst_addr))
        check = self._checksum(new_hdr)

        # return packet to TCP
        if protocol == 6 and \
           src_addr == self.dst_ip and \
           dst_addr == self.src_ip and \
           chk == check:
            return packet[20:]

    def _checksum(self, msg):
        s = 0
        for i in range(0, len(msg), 2):
            w = ord(msg[i]) + (ord(msg[i+1]) << 8)
            s = self._carry_around_add(s, w)
        s = ~s & 0xffff
        s1 = (s << 8) & 0xffff
        s2 = (s >> 8) & 0xffff
        return s1 + s2

    def _carry_around_add(self, a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)


def main():
    return

if __name__ == '__main__':
    main()
