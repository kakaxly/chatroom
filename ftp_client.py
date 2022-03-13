import sys
from socket import *
from time import sleep

ADDR = ("192.168.1.15", 8888)


# 具体功能
class Ftpclient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  # 请求列表
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("thanks for using")

    def do_get(self, filename):
        # handle file download function
        self.sockfd.send(("G " + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "ok":
            fd = open(filename, "wb")
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    print("%s downloaded" % filename)
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        try:
            f = open(filename, "rb")
        except Exception:
            print("file not exist")
            return
        filename = filename.split("/")[-1]
        self.sockfd.send(("P " + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'ok':
            sleep(0.1)
            while True:
                data = f.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b"##")
                    print("%s upload completed" % filename)
                    f.close()
                    break
                self.sockfd.send(data)
        else:
            print(data)


def request(sockfd):
    ftp = Ftpclient(sockfd)
    while True:
        print("\n==========命令选项============")
        print("***************List***************")
        print("*************get file*************")
        print("*************put file*************")
        print("***************quit***************")

        cmd = input("输入命令：")
        if cmd.strip() == "List":
            ftp.do_list()
        elif cmd.strip() == "quit":
            ftp.do_quit()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)


def main():
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("链接服务器失败")
    else:
        print("""
                 ***********************
                    Data File Image
                 ***********************
        """)
        while True:
            cls = input("请输入文件种类：")
            if cls not in ["Data", "File", "image"]:
                print("Sorry input Error!!")
            break
        sockfd.send(cls.encode())
        request(sockfd)  # 发送具体请求


if __name__ == "__main__":
    main()
