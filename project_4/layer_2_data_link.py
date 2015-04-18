# Layer_2_Ethernet
import socket
import re
import commands
import time
from struct import pack, unpack


class Ethernet:

    def __init__(self):
        # mac address is stored in ascii format
        self.src_mac = self._get_src_mac()
        self.dst_mac = self._get_dst_mac()

        # 0x0800 means IPv4
        self.frame_type = 0x0800

        # sockets for send and receive
        self.s_socket = socket.socket(socket.AF_PACKET,
                                      socket.SOCK_RAW)
        self.s_socket.bind(("eth0", 0))
        self.r_socket = socket.socket(socket.AF_PACKET,
                                      socket.SOCK_RAW,
                                      socket.htons(0x0800))

    """Public Function of Ethernet"""

    def send_frame(self, pkt):
        hdr = self._make_header()
        self.pkt = pkt
        self.s_socket.send(hdr + pkt)

    def receive_frame(self):
        frame = None

        while True:
            if frame is not None:
                break

            start = time.time()

            while frame is None:
                if time.time() - start > 60000:
                    self.s_socket.send(self.pkt)
                    break

                frame = self.r_socket.recvfrom(65535)[0]
                frame = self._parse_frame(frame)

        return frame

    """Private Function of Ethernet"""

    def _get_src_mac(self):
        cmd_result = commands.getoutput('/sbin/ifconfig')
        match = re.findall(r'HWaddr (.*)  ', cmd_result)[0]
        return match.replace(':', '').decode('hex')

    def _get_dst_mac(self):
        # get routher ip
        cmd_result = commands.getoutput('/sbin/route -n')
        rtr_ip = re.findall(r'0.0.0.0(.*)0.0.0.0', cmd_result)[0].strip()

        # get local ip
        cmd_result = commands.getoutput('/sbin/ifconfig')
        src_ip = re.findall(r'inet addr:(.*)  Bcast', cmd_result)[0]

        # create ARP packet
        eth_hdr = pack("!6s6s2s", '\xff\xff\xff\xff\xff\xff',
                                  self.src_mac,
                                  '\x08\x06')
        arp_hdr = pack("!2s2s1s1s2s", '\x00\x01', '\x08\x00',
                                      '\x06', '\x04',
                                      '\x00\x01')
        arp_sender = pack("!6s4s", self.src_mac,
                          socket.inet_aton(src_ip))
        arp_target = pack("!6s4s", '\x00\x00\x00\x00\x00\x00',
                          socket.inet_aton(rtr_ip))

        # send packet
        rawSocket = socket.socket(socket.PF_PACKET,
                                  socket.SOCK_RAW,
                                  socket.htons(0x0806))
        rawSocket.bind(('eth0', socket.htons(0x0806)))
        rawSocket.send(eth_hdr + arp_hdr + arp_sender + arp_target)

        # wait for response
        rawSocket = socket.socket(socket.PF_PACKET,
                                  socket.SOCK_RAW,
                                  socket.htons(0x0806))
        response = None

        while True:
            if response is not None:
                break

            start = time.time()

            while response is None:
                if time.time() - start > 100:
                    rawSocket.send(eth_hdr + arp_hdr + arp_sender + arp_target)
                    break

                response = rawSocket.recvfrom(2048)[0][6:12]
        return response

    def _make_header(self):
        return pack('!6s6sH', self.dst_mac, self.src_mac, self.frame_type)

    def _parse_frame(self, pkt):
        dst_mac, src_mac, frame_type = unpack('!6s6sH', pkt[:14])
        if src_mac == self.dst_mac and \
           frame_type == 0x0800:
            return pkt[14:]


def main():
    'do sth'
    return

if __name__ == '__main__':
    main()
