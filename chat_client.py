from socket import *
import os, sys

# 服务器地址
ADDR = ('192.168.1.21', 8888)


# 发送消息
def send_msg(s, name):
    while True:
        try:
            text = input("发言：")
        except KeyboardInterrupt:
            text = 'quit'
        if text == 'quit':
            msg = 'Q ' + name
            s.sendto(msg.encode(), ADDR)
            sys.exit("退出聊天室")
        msg = "C %s %s" % (name, text)
        s.sendto(msg.encode(), ADDR)


# 接收消息
def recv_msg(s):
    while True:
        data, addr = s.recvfrom(2048)
        # 服务端发送EXIT 表示让客户端退出
        if data.decode() == 'EXIT':
            sys.exit()
        print(data.decode() + "\n发言:", end=" ")


# 创建网络连接
def main():
    sockfd = socket(AF_INET, SOCK_DGRAM)
    while True:
        name = input("请输入你的姓名：")
        msg = "L " + name
        sockfd.sendto(msg.encode(), ADDR)
        # 等待回应
        data, addr = sockfd.recvfrom(1024)
        if data.decode() == "OK":
            print("您已进入聊天室")
            break
        else:
            print(data.decode())
    # 创建新的进程
    pid = os.fork()
    if pid < 0:
        sys.exit("Error:")
    elif pid == 0:
        send_msg(sockfd, name)
    else:
        recv_msg(sockfd)


if __name__ == '__main__':
    main()
