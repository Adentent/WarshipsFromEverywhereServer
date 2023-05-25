import socket
import threading
import uuid
import re
from random import randint


all_the_codes_used = {}
# 读取用户文件
user_file = open("users", "r")
lines = "".join(user_file.readlines())
if lines == '':
    users = {}
else:
    users = eval(lines)
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
        try:
            client_socket, client_address = server_socket.accept()
        # except OSError as e:
        except OSError:
            # print(e)
            return
        threads.append(threading.current_thread())
        try:
            # 请求登陆
            ask_for_passwd, ask_for_username = "Password: ", "Username: "
            ask_for_req_begin = "Login/Sign up(1 for Login, 2 for Sign up): "
            wrong_passwd = "Wrong password.\nYou are kicked from the server!"
            successfully_login = "Logged in successfully."
            successfully_sign_up = "Signed up successfully."
            no_such_user = "No such user.\nYou are kicked from the server!"
            no_such_req = "No such request.\nYou are kicked from the server!"
            client_socket.sendall(ask_for_req_begin.encode('utf-8'))
            req = client_socket.recv(1024).decode('utf-8')
            client_socket.sendall(ask_for_username.encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8')
            client_socket.sendall(ask_for_passwd.encode('utf-8'))
            password = client_socket.recv(1024).decode('utf-8')
            if (not req) or (not username) or (not password):
                raise Exception("No input\nClient offline")
            elif req != '1' and req != '2':
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
            tst = client_socket.recv(1024)
            client_socket.sendall(tst)

            print(client_address, "start common communicate!")
            # 开始正常交互
            while True:
                code = randint(10000, 99999)
                if code not in all_the_codes_used.keys():
                    all_the_codes_used[code] = -1
                    break
            # TODO: 完成all_the_codes_used实质性内容(记住了这是个字典)
            ask_for_req_begin = "Warships from Everywhere"
            ask_for_req_mid = "Lobby"  # -> User state
            ask_for_req_end = "$"
            help_document = """\
Hi player!
Welcome to the lobby of Warships from Everywhere.
As you can see,
There is a lovely console in front of your eyes (yes, lovely).
            
Here are the optional commands:
help - Show this;
start - Start a new game;
join - Join a game by using codes.
            
Want to leave?
Just type nothing and press Enter!
            
If you understand,
Press Enter!\n"""
            start_a_new_game = "\
We generated a unique code for you and here it is: %s\n\
Copy that to your friend so that they can play with you!" % code
            waiting = "Waiting for your friend..."
            finish_matching = "Your friend (now your enemy) arrived!\nFire!"
            war_finished = "Got back to the Lobby!"
            join_code_input = "Input your code here: (ask your friend for it)\n"
            while True:
                ask_for_req = ask_for_req_begin + " - " + ask_for_req_mid + " " + ask_for_req_end + " "
                # 向客户端发送数据
                client_socket.sendall(ask_for_req.encode('utf-8'))
                # 接收客户端发送的数据
                req = client_socket.recv(1024)
                if not req:
                    break
                # print(f"Received {req.decode('utf-8')} from {str(client_address[0]) + ':' + str(client_address[1])}")
                if ask_for_req_mid == "Lobby":  # 玩家处在Lobby
                    if req == "help":
                        client_socket.sendall(help_document.encode('utf-8'))
                        client_socket.recv(512)
                        client_socket.sendall(b"__CONSOLE__")
                        client_socket.recv(512)
                    elif req == "start":
                        ask_for_req_mid = "Waiting Line"
                        client_socket.sendall(start_a_new_game.encode('utf-8'))
                        client_socket.recv(512)
                        client_socket.sendall(b"__KEEP_WAITING__")
                        client_socket.recv(512)
                        client_socket.sendall(waiting.encode('utf-8'))
                        client_socket.recv(512)
                        while all_the_codes_used[code] != 0:
                            continue
                        client_socket.sendall(finish_matching.encode('utf-8'))
                        client_socket.recv(512)
                        all_the_codes_used[code] = 1
                        # TODO: 完成实质性游戏内容
                        client_socket.sendall(war_finished.encode('utf-8'))
                        client_socket.recv(512)
                        ask_for_req_mid = "Lobby"
                        all_the_codes_used[code] = -1
                    elif req == "join":
                        client_socket.sendall(join_code_input.encode('utf-8'))
                        code = client_socket.recv(512).decode('utf-8')
                        if code.isdigit():
                            if 10000 <= int(code) <= 99999:
                                code = int(code)
                                all_the_codes_used[code] = 0
                        # TODO: 完成非法输入相关内容
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
