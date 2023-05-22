from socket import socket, AF_INET, SOCK_STREAM

if __name__ == "__main__":
    configs_file = open("configs")
    configs = eval("".join(configs_file.readlines()))
    tcp_socket_server = socket(AF_INET, SOCK_STREAM)
    address = ('localhost', 6000)
    tcp_socket_server.bind(address)
    tcp_socket_server.listen(128)
    while True:
        client_socket, client_addr = tcp_socket_server.accept()
        client_socket.send(configs["START"].encode('utf-8'))
        while True:
            recv_data = client_socket.recv(2048)
            if recv_data:
                print("We got:", recv_data.decode('utf-8'))
                client_socket.send('Copy that'.encode('utf-8'))
            else:
                client_socket.close()
                break
    tcp_socket_server.close()
