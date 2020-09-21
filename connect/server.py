import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ips = socket.gethostbyname_ex(socket.gethostname())
print(ips)
s.bind((socket.gethostname(), 5050))
s.listen()

while True:
    client_socket, address = s.accept()
    print(f'Connection from {address} has been established!')
    client_socket.send(b'Hello World!')

    msg = client_socket.recv(1024)
    print(msg.decode('utf-8'))
