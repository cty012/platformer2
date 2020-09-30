import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.1.36.11', 5050))

msg = s.recv(1024)
print(msg.decode('utf-8'))
s.send(b'Bye World!')
s.close()
