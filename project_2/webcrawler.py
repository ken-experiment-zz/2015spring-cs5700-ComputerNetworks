import socket
import time
import re

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
    body += "username=001729585&password=QHKMF05I&csrfmiddlewaretoken="
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
    global flag
    data = loggin()
    retrieve_flag(data)

    url = re.findall(r"<li>.*?<a href=\"(.*?)\">", data)
    
    visit = []
    while len(flag) < 5 :
        path = url.pop()
        visit.append(path)

        data= _data(path)
        retrieve_flag(data)
        
        ne = [path+"friends/1/"]
        while ne :
            data = _data(ne[0])
            retrieve_flag(data)

            tmp = re.findall(r"<li>.*?<a href=\"(.*?)\">", data)
            for t in tmp :
                if t not in visit and t not in url:
                    url.append(t)

            ne = re.findall(r".*<a href=\"(.*?)\">next<.*", data)
        print "url length: " + str(len(url)) + " visit: " + str(len(visit))

    print flag

def retrieve_flag (data) :
    global flag

    _flag = re.findall(r".*FLAG: (.*?)<.*", data)

    if _flag and _flag[0] not in flag:
        flag.append(_flag[0])
        print flag

if __name__ == "__main__" :
    sid_key = ""
    sid_value = ""
    flag = []

    process()
