import socket
import threading

# 创建 TCP 服务器套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定服务器地址和端口号
SERVER_ADDRESS = ('localhost', 6000)
server_socket.bind(SERVER_ADDRESS)

# 开始监听客户端连接请求
server_socket.listen(5)

# 存储活动的客户端线程
threads = []

def handle_client():
    """
    处理客户端请求的线程函数
    """
    client_socket, client_address = server_socket.accept()
    threads.append(threading.current_thread())
    try:
        while True:
            # 接收客户端发送的数据
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received {data.decode('utf-8')} from {str(client_address[0]) + ':' + str(client_address[1])}")
            # 原样将收到的数据返回给客户端
            client_socket.sendall(data)
    except Exception as e:
        print(e)
    finally:
        # 关闭套接字并从线程列表中移除该线程
        client_socket.close()
        threads.remove(threading.current_thread())


client_handle = threading.Thread(target=handle_client)
client_handle.start()
try:
    # 在主线程等待管理员输入 stop 命令
    while True:
        command = input("Enter 'stop' to stop the server: \n")
        if command == "stop":
            # 首先关闭服务器套接字，停止接受更多的客户端连接
            server_socket.close()
            break
        else:
            print("Unknown command, please enter 'stop' to stop the server.")

    # 等待所有客户端线程执行完毕
    for thread in threads:
        thread.join()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    print("Shutting down the server...")

    # 关闭所有活动的客户端套接字
    for thread in threads:
        client_socket = thread.client_socket
        client_socket.close()

    # 清空线程列表
    threads.clear()

    # 关闭服务器套接字
    server_socket.close()
