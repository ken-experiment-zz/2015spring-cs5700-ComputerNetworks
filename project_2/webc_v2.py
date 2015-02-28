import socket
import threading
import time
import re
import sys

class myflag: 
    def __init__(self) :
        self.isPrinted = False

def loggin() :
    get = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 
    get.connect(("cs5700sp15.ccs.neu.edu", 80))
    header = 'GET /accounts/login/ HTTP/1.0\r\n'
    header += 'Connection: keep-alive\r\n'
    header += '\r\n'
    get.send(header)
    data = recv_timeout(get)
    get.close()
    
    cookie = re.findall(r'Set-Cookie: (.*?)=(.*?);', data)
    csrf = re.findall(r"name='csrfmiddlewaretoken' value=\'(.*?)\'", data)

    global username
    global password

    body = "POST /accounts/login/ HTTP/1.0\r\n"
    body += "Accept: text/html,application/xhtml+xml,"
    body += "application/xml;q=0.9,image/webp,*/*;q=0.8\r\n" 
    body += "Accept-Encoding: gzip, deflate\r\n"
    body += "Accept-Language: en\r\n"
    body += "Cache-Control: max-age=0\r\n"
    body += "Connection: keep-alive\r\n"
    body += "Content-Length: 96\r\n"
    body += "Content-Type: application/x-www-form-urlencode\r\n"
    body += "Cookie: " + cookie[0][0] + "=" + cookie[0][1] + "; "
    body += cookie[1][0] + "=" + cookie[1][1] + "\r\n"
    body += "Host :cs5700sp15.ccs.neu.edu\r\n"
    body += "Origin: http://cs5700sp15.ccs.neu.edu\r\n"
    body += "User-Agent: HTTPTool/1.0\r\n"
    body += "\r\n"
    body += "username=" + username + "&password=" + password + "&csrfmiddlewaretoken="
    body += csrf[0] + "&next=\r\n\r\n"
    post = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    post.connect(("cs5700sp15.ccs.neu.edu", 80))
    post.send(body)
    data = recv_timeout(post)
    post.close()

    sid = re.findall(r'Set-Cookie: (.*?)=(.*?);', data)

    global sid_key
    global sid_value
    sid_key = sid[0][0]
    sid_value = sid[0][1]
    
    data = _data("/fakebook/")

    return data

def _data (path) :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("cs5700sp15.ccs.neu.edu", 80))
    s.send(_body(path))
    _data = recv_timeout(s)
    s.close()
    return _data

def _body (path) :
    _body = "GET " + path + " HTTP/1.0\r\n"
    _body += "Cookie: " + sid_key + "=" + sid_value + "\r\n"
    _body += "\r\n"
    return _body
    
def recv_timeout(the_socket,timeout=0.5):
    the_socket.setblocking(0)
    total_data=[];
    data='';
    begin=time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return ''.join(total_data)

def process() :
    flag = []
    data = loggin()

    url = re.findall(r"<li>.*?<a href=\"(.*?)\">", data)
    visit = []

    threadLock = threading.Lock()
    threads = []

    mf = myflag()
    for i in range(1, 40) :
        thread = myThread(i, threadLock, url, visit, flag, mf)
        thread.start()
        threads.append(thread)

    for t in threads :
       t.join() 

class myThread (threading.Thread):
    def __init__(self, threadID, lock, url, visit, flag, mf) :
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.lock = lock
        self.url = url
        self.visit = visit
        self.flag = flag
        self.mf = mf

    def run(self) :
        global num
        while len(self.flag) < 5 :
            self.lock.acquire()
            try :
                while len(self.url) <= 0 :
                    self.lock.release()
                    time.sleep(1)
                    self.lock.acquire()

                path = self.url.pop()

                self.visit.append(path)
                num += 1
                print "num: " + str(num)
            finally :
                self.lock.release()

            data= _data(path)

            self.lock.acquire()
            _flag = re.findall(r".*FLAG: (.*?)<.*", data)
            if _flag :
                self.flag.append(_flag[0])
                print _flag[0]
            friends = re.findall( r"\"(/fakebook/.*?)\">", data)
            #print friends
            for t in friends :
                if t not in self.visit and t not in self.url :
                    self.url.append(t)
            #print "url: " + str(len(self.url))
            self.lock.release()

        self.lock.acquire()
        if not self.mf.isPrinted :
            self.mf.isPrinted = True
            print self.flag
        self.lock.release()

if __name__ == "__main__" :
    sid_key = ""
    sid_value = ""
    username = sys.argv[1]
    password = sys.argv[2]
    num = 0

    process()

