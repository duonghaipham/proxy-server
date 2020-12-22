from socket import socket, error, AF_INET, SOCK_STREAM
from threading import Thread

HOST = "127.0.0.1"  # dia chi localhost
PORT = 8888         # port proxy lang nghe
SIZE = 1048576      # kich thuoc chunk cua moi lan nhan du lieu tu server
TIMES = 10          # so ket noi toi da

def Forbid(server, site):
    """Tra ve mot trang html trong truong hop dia chi web hien tai bi cam"""
    msg = (b"HTTP/1.1 403 Forbidden\r\n\r\n<html>\r\n<title>403 Forbidden</title>\r\n<body>\r\n"
          b"<h1>Error 403: Forbidden</h1>\r\n<p>You don\'t have permission to access / on this server.</p>\r\n"
          b"</body>\r\n</html>\r\n")    # trang html in ra trinh duyet
    server.send(msg)
    print("Blocked " + site)
    server.close()

def Process(request):
    """Tra ve dia chi web server va port tuong ung"""
    lines = request.decode("utf-8").split("\n") # tach goi tin http request ra thanh tung dong
    host = lines[1].split(" ")[1]   # lay dia chi cua trang web
    host = host[:len(host) - 1]     # xoa \r

    if host.find(":") != -1:        # neu co : (tuc la co port chi dinh)
        port = int(host.split(":")[1])
        host = host[:host.find(":")]
    else:                           # neu khong thi dung default port (80)
        port = 80
    return host, port

def IsBlocked(host):
    """Kiem tra host co bi cam hay khong"""
    fileInput = open("blacklist.conf", "r")
    blockedSites = fileInput.read().split("\n") # doc het tat ca cac dong trong file blacklist.conf

    for site in blockedSites:   # duyet qua danh sach cac dia chi web vua doc
        if site.find(host) != -1:
            return True         # tim thay host co trong blacklist
    return False

def Get(request, server):
    """Proxy nhan request tu client, chuyen tiep len server (neu khong bi chan)"""
    client = socket(AF_INET, SOCK_STREAM)
    try:
        host, port = Process(request)   # lay dia chi web va port tuong ung

        if IsBlocked(host):             # trang web bi cam
            Forbid(server, host)
        else:
            client.connect((host, port))
            client.sendall(request)     # gui request tu proxy cho server
            Post(client, server)        # goi ham de nhan ket qua response
            print("Received from " + host)
    except error:
        client.close()
        server.close()
    except:
        pass

def Post(client, server):
    """Proxy nhan response tu server, chuyen tiep cho trinh duyet"""
    while True:
        response = client.recv(SIZE)    # nhan het tat ca cac chunk cua trang web
        if len(response) > 0:           # neu chunk con hop le thi chuyen tiep xuong cho trinh duyet
            server.send(response)
        else:
            break
    client.close()
    server.close()

if __name__ == "__main__":
    """Dieu khien luong thuc thi cho chuong trinh"""
    try:
        s = socket(AF_INET, SOCK_STREAM)    # tao socket
        s.bind((HOST, PORT))
        s.listen(TIMES)
        print("Proxy address: " + HOST)
        print("Proxy port: " + str(PORT))
        print("Maximum connections: " + str(TIMES))
        print("SET UP PROXY SERVER SUCCESSFULLY")
        print("PROXY SERVER IS WORKING", end = "\n\n")
    except error as error:
        print("Loading error: {}".format(error))

    try:
        while True:
            server, address = s.accept()
            request = server.recv(SIZE)
            Thread(target = Get, args = (request, server)).start()  # tao luong thuc thi cho request moi

    except KeyboardInterrupt:
        print("interrupted")
        pass
    s.close()