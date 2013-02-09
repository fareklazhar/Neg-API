import socket

def client(host, port):
    s = socket.socket()
    s.connect((host, port))
    s.send("c s    This    DT      B-NP    be      VBZ     B-VP    0       0       0       file    0       UNKNOWN_LABEL")
    print "OK"
    data = s.recv(1024)
    print "client: receive '%s'" % data
    s.close()

client("localhost",7000)
#client("127.0.0.1", 21567) 
