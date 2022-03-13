"""
ftp 文件服务器
并发网络功能训练
"""
import sys
from threading import Thread
import os
from socket import *
from time import sleep

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)
FTP = "/home/kaka/ftp_dir/"


# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self, connfd, path):
        self.connfd = connfd
        self.path = path

    def do_list(self):
        files = os.listdir(self.path)
        if not files:
            self.connfd.send("该文件为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
        fs = ' '
        for file in files:
            if file[0] != "." and os.path.isfile(self.path + file):
                fs += file + "\n"
        # 一次发送避免tcp沾包
        self.connfd.send(fs.encode())

    def do_get(self, filename):
        try:
            fd = open(self.path + filename, "rb")
        except Exception:
            self.connfd.send(b'file not exist')
            return
        else:
            self.connfd.send(b"ok")
            sleep(0.1)
            # begin send file content
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)

    def do_put(self, filename):
        if os.path.exists(self.path + filename):
            self.connfd.send(b"file exist")
            return
        self.connfd.send(b'ok')
        fd = open(self.path + filename, "wb")
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':

                break
            fd.write(data)
        fd.close()


def handle(connfd):
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + "/"
    ftp = FtpServer(connfd, FTP_PATH)
    while True:
        # 接受客户端请求
        data = connfd.recv(1024).decode()
        # 如果客户端口返回data为空
        if data[0] == "Q" or not data:
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0] == "P":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)


def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(3)
    print("FTP Server is running....")
    while True:
        try:
            connfd, addr = sockfd.accept()
        except KeyboardInterrupt:
            sys.exit("退出服务器")
        except Exception as e:
            print(e)
            continue
        print("链接的客户端：", addr)

        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)
        client.start()


if __name__ == "__main__":
    main()
