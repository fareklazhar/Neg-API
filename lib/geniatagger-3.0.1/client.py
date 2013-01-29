import socket

def client(host, port):
    s = socket.socket()
    s.connect((host, port))
    s.send("I am a man")
    print "OK"
    data = s.recv(1024)
    print "client: receive '%s'" % data
    s.close()

#client("localhost",7070)
client("127.0.0.1", 21567) 
