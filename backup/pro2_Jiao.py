#!/usr/bin/python

from bs4 import BeautifulSoup
import urlparse
import socket
import re
import threading
import time
#  Set the startingpoint for the spider and initialize 
# the a mechanize browser object
url = "/fakebook/"

# create lists for the urls in que and visited urls
urls = [url]
visited = [url]
secrets = []

hostname = "cs5700sp15.ccs.neu.edu"
username = "001712481"
password = "OB1MA8UL"
url_lock = threading.Lock()
visited_lock = threading.Lock()
secret_lock = threading.Lock()

def length_urls():
  url_lock.acquire()
  len_urls = len(urls)
  url_lock.release()
  return len_urls

def pop_first_url():
  url_lock.acquire()
  first_url = urls.pop(0)
  url_lock.release()
  return first_url

def append_url(url):
  url_lock.acquire()
  urls.append(url)
  url_lock.release()

def in_visited(url):
  visited_lock.acquire()
  isInVis = url in visited
  visited_lock.release()
  return isInVis

def append_visited(url):
  visited_lock.acquire()
  visited.append(url)
  visited_lock.release()

def in_secrets(secret):
  secret_lock.acquire()
  isInSec = secret in secrets
  secret_lock.release()
  return isInSec

def append_secret(secret):
  secret_lock.acquire()
  secrets.append(secret)
  secret_lock.release()  


def get(url, csrftoken, sessionid):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((hostname, 80)) # connect
  print "get Method"
  
  s.sendall("GET {url} HTTP/1.1 \r\n"
            "Host: cs5700sp15.ccs.neu.edu \r\n"
            "Connection: keep-alive \r\n"
            "Cookie: csrftoken={csrftoken}; sessionid={sessionid} \r\n"
            "\r\n".format(url=url,csrftoken=csrftoken,sessionid=sessionid))
  
  total_data=[]
  while True:
        rdata = s.recv(1024)
#         print rdata
        if not rdata: break
        total_data.append(rdata)
  
  return ''.join(total_data)

def post( username, password,csrftoken,sessionid):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 80)) # connect
    data = str("username="+username+"&password="+password+"&csrfmiddlewaretoken="+csrftoken+"&next=/fakebook/")

    print data
    suc = s.send("POST /accounts/login/ HTTP/1.1 \r\n" # send headers
              "Host: {hostname} \r\n"
              "Connection: keep-alive \r\n"
              "Content-Length: {len} \r\n"
              "Content-Type : application/x-www-form-urlencoded\r\n"
              "Cookie: csrftoken={csrftoken}; sessionid={sessionid} \r\n"
              "\r\n".format(hostname=hostname, len=len(data), 
                            csrftoken=csrftoken, sessionid=sessionid))
    s.sendall(data) # send data
    print suc
    
    total_data=[]
    while True:
        rdata = s.recv(1024)
        print rdata
        if not rdata: break
        total_data.append(rdata)

    print total_data

    return ''.join(total_data)

#

# Since the amount of urls in the list is dynamic
#   we just let the spider go until some last url didn't
#   have new ones on the webpage
def crawling(thread_id,csrftoken_id,session_id):
  while length_urls() >0:
      url_0 = pop_first_url()
      
      print "\nthread_id{thread_id}********************\n".format(thread_id =thread_id)
      print "begin crawling : "+url_0
      
      try:
          htmltext = get(url_0, csrftoken_id, session_id)
      except:
          print url_0
      
      soup = BeautifulSoup(htmltext)
      
#       urls.pop(0)
#       print len(urls)
      
      for tag in soup.findAll("h2", { "class" : "secret_flag" }):
        secret = tag.contents[0].split(":")[1].strip()
        if not in_secrets(secret):
          append_secret(secret)
      
      for tag in soup.findAll("a", href = True):
          if url in tag['href'] and not in_visited(tag['href']):
              append_url(tag['href'])
              append_visited(tag['href'])
      
      print "len urls: "+str(len(urls))
      print urls
      print "len visited: "+str(len(visited))
      print visited
      print "secrets: "
      print secrets

if __name__ == '__main__':
  recv = get( "/accounts/login/", "", "")
  session_id = re.search(r"\bsessionid=(\w*)\b", recv).group(0).split('=')[1]
  csrftoken_id = re.search(r"\bcsrftoken=(\w*)\b", recv).group(0).split('=')[1]
  print session_id
  print csrftoken_id
  
  recv = post(username, password,csrftoken_id,session_id)
  #session_id = re.search(r"\bsessionid=(\w*)\b", recv).group(0).split('=')[1]
  
  threads = []
  for i in range(100):
    t = threading.Thread(target=crawling, args=(i, csrftoken_id,session_id))
    threads.append(t)
    t.start()
    time.sleep(5)
