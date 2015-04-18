# Layer_5_Application
import re
from layer_4_transport import *

class HTTP:
    def __init__(self):
        # an object, with url parsed
        self.parsed_url = ''

        # use TCP to send request
        self.tcp = TCP()

    """Public Function of HTTP """
    def set_arguments(self, src_ip, dst_ip, p):
        self.parsed_url = p
        self.tcp.set_ip_address(src_ip, dst_ip)

    def run(self):
        self._set_request()
        self.tcp.run()
        self._parse_data()

    """Private Function of HTTP """
    def _set_request(self):
        hdr = []
        hdr.append('GET ' + self.parsed_url.path+ ' HTTP/1.1\r\n')
        hdr.append('Host: ' + self.parsed_url.netloc + ':80\r\n')
        hdr.append('Connection: keep-alive\r\n')
        hdr.append('\r\n')
        self.tcp.set_request(''.join(hdr))

    def _parse_data(self):
        data = self.tcp.data_collected()
        seperate_index = data.find('\r\n\r\n')
        http_reponse = data[:seperate_index]
        version, status = re.findall(r'HTTP/(.*?) OK', http_reponse)[0].split()
        if status != '200':
            sys.exit()

        content = data[seperate_index+4:]
        if 'Transfer-Encoding: chunked' in http_reponse:
            content = self._decode_data(content)

        self.writeHTML(content)

    def _decode_data(self, data):
        new_data = []
        next_offset = data.find('\r\n')

        while data[:next_offset] != '':
            length = int(data[:next_offset], 16)
            data = data[next_offset+2:]
            new_data.append(data[:length])
            data = data[length+2:]

            next_offset = data.find('\r\n')

        return ''.join(new_data)

    def writeHTML(self, content):
        if not self.parsed_url.path or self.parsed_url.path.endswith('/'):
            filename = 'index.html'
        else:
            filename = self.parsed_url.path.split('/').pop()

        with open(filename, 'w') as f:
            f.write(content)
        print 'done'

if __name__ == '__main__':
    main()
