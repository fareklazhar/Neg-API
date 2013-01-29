from socket import *

HOST = 'localhost'
PORT = 7070
BUFSIZ = 1024 
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)

print "test"
while True:
  print "test"
  data = "This is a pen."
  tcpCliSock.send(data)

  tcpCliSock.close()
  

  tcpCliSock = socket(AF_INET, SOCK_STREAM)
  tcpCliSock.connect(ADDR)
  print "OK"
  data = tcpCliSock.recv(BUFSIZ)

  if not data:
      break
  print data

tcpCliSock.close()
