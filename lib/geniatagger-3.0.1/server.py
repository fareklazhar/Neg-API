import socket, threading

def server(host, port):
    s = socket.socket()
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept() 
    data = conn.recv(1024)
    print "server: receive '%s'" % data
    conn.send(data.upper())
    conn.close()
    s.close()
class Server(threading.Thread):
  def run(self):
    server("localhost", 7070)

s = Server()
s.start()
