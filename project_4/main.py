# Main Function
import sys
import re
import commands
from urlparse import urlparse
from layer_5_application import *

def main():
    # Get url from input
    try:
        url = sys.argv[1]
        p = urlparse(url)
        if not p.scheme:
            url = 'http://' + url
            p = urlparse(url)
    except Exception, msg:
        print msg, "EXIT PROGRAM"
        sys.exit()

    # Get src_ip and dest_ip
    src_ip = re.findall(r'inet addr:(.*)  Bcast', commands.getoutput('/sbin/ifconfig'))[0]
    dest_ip = socket.gethostbyname(p.netloc)

    # Execute program
    http = HTTP()
    http.set_arguments(src_ip, dest_ip, p)
    http.run()

if __name__ == '__main__':
    main()
