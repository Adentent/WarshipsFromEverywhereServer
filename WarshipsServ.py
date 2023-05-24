import socket
import threading
import uuid
import re


# 读取用户文件
user_file = open("users", "r")
users = eval("".join(user_file.readlines()))
user_file.close()
user_file = open("users", "w+")
# print("".join(user_file.readlines()))

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


def get_mac_address():
    """
    获取一台电脑唯一的Mac并得到所有的数字
    返回26减去这个数字对26取余加1的结果的字符串形式
    AES加密的秘钥
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return 26 - (int("".join(re.findall(r"[0-9]", ":".join([mac[e:e + 2] for e in range(0, 11, 2)])))) % 26 + 1)


def caesar_cipher(a):
    b = ""
    for i in range(len(a)):
        if ord('a') <= ord(a[i]) <= ord('z'):
            # print(chr((ord(a[i])+get_mac_address()-ord('a'))%26+ord('a')),end="")
            b += chr((ord(a[i]) + get_mac_address() - ord('a')) % 26 + ord('a'))
        elif ord('A') <= ord(a[i]) <= ord('Z'):
            # print(chr((ord(a[i])+get_mac_address()-ord('A'))%26+ord('A')),end="")
            b += chr((ord(a[i]) + get_mac_address() - ord('A')) % 26 + ord('A'))
        elif ord('0') <= ord(a[i]) <= ord('9'):
            # print(chr((ord(a[i])+get_mac_address()-ord('0'))%10+ord('0')),end="")
            b += chr((ord(a[i]) + get_mac_address() - ord('0')) % 10 + ord('0'))
        else:
            # print(a[i], end="")
            b += a[i]
    return b


def caesar_decipher(b):
    a = str()
    for p in b:
        if "a" <= p <= "z":
            # print(chr(ord("a") + (ord(p) - ord("a") - get_mac_address()) % 26), end='')
            a += chr(ord("a") + (ord(p) - ord("a") - get_mac_address()) % 26)
        elif "A" <= p <= "Z":
            # print(chr(ord("A") + (ord(p) - ord("A") - get_mac_address()) % 26), end='')
            a += chr(ord("A") + (ord(p) - ord("A") - get_mac_address()) % 26)
        elif "0" <= p <= "9":
            # print(chr(ord("0") + (ord(p) - ord("0") - get_mac_address()) % 10), end='')
            a += chr(ord("0") + (ord(p) - ord("0") - get_mac_address()) % 10)
        else:
            # print(p, end='')
            a += p
    return a


def handle_client():
    """
    处理客户端请求的线程函数
    """
    global users
    while True:
        client_socket, client_address = server_socket.accept()
        threads.append(threading.current_thread())
        try:
            # 请求登陆
            ask_for_passwd, ask_for_username = "Password: ", "Username: "
            ask_for_req = "Login/Sign up(1 for Login, 2 for Sign up): "
            wrong_passwd = "Wrong password.\nYou are kicked from the server!"
            successfully_login = "Logged in successfully."
            successfully_sign_up = "Signed up successfully."
            no_such_user = "No such user.\nYou are kicked from the server!"
            no_such_req = "No such request.\nYou are kicked from the server!"
            client_socket.sendall(ask_for_req.encode('utf-8'))
            req = client_socket.recv(1024).decode('utf-8')
            client_socket.sendall(ask_for_username.encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8')
            client_socket.sendall(ask_for_passwd.encode('utf-8'))
            password = client_socket.recv(1024).decode('utf-8')
            if req != '1' and req != '2':
                client_socket.sendall(no_such_req.encode('utf-8'))
                raise Exception("No such request")
            elif req == '1' and username not in users:
                client_socket.sendall(no_such_user.encode('utf-8'))
                raise Exception("No such user")
            elif req == '1' and password == caesar_decipher(users[username]):
                client_socket.sendall(successfully_login.encode('utf-8'))
            elif req == '2':
                users[username] = caesar_cipher(password)
                client_socket.sendall(successfully_sign_up.encode('utf-8'))
            else:
                client_socket.sendall(wrong_passwd.encode('utf-8'))
                raise Exception("Wrong password")
            # 开始正常交互
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

    user_file.write(str(users))
    user_file.close()
