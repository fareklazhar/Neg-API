from socket import *
from time import ctime
import subprocess

HOST = '127.0.0.1'   # localhost
PORT = 21567         # choose a random port number
BUFSIZ = 1024        # set buffer size to 1K
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5) 

io = subprocess.Popen('./geniatagger', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#io.write("It is a pen.")
#print io.strip()


while True:
  print 'waiting for connection...'
  tcpCliSock, addr = tcpSerSock.accept()
  print '...connected from:', addr
  
  while True:
    data = tcpCliSock.recv(BUFSIZ)
    if not data:
      break
    print io.communicate(input="It is a pen.")[0]
    tcpCliSock.send('[%s] %s' % (ctime(), data))
    
    #print io.stdout.readlines()
       
  tcpCliSock.close()

tcpSerSock.close()  # never executed
