import socket
import signal
import threading
import time

class Server:
    def __init__(self, config):
        self.config = config

        # Create a TCP socket and don`t wait for natural timeout
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port   
        self.serverSocket.bind((self.config['HOST_NAME'], self.config['BIND_PORT']))
        
        # become a server socket
        self.serverSocket.listen(10)

        # setup whitelist and blacklist functionalities
        self.whitelist = []
        self.blacklist = []

        self.usingWhitelist = self.readWhitelist()
        self.usingBlacklist = self.readBlacklist()

    def readWhitelist(self): # check out and fill in whitelist
        try:
            with open("Whitelist.txt", 'r') as a:
                for line in a:
                    self.whitelist.append(line)
                if len(self.whitelist) > 0:
                    print("Whitelist.txt found and ready to use.")
                    return True
                else:
                    print("Whitelist.txt found, but empty.")
                    return False
        except:
            print("Whitelist.txt not found.")
            return False

    def readBlacklist(self): # check and fill in blacklist
        try:
            with open("Blacklist.txt", 'r') as a:
                for line in a:
                    self.blacklist.append(line[:-1])
                if len(self.blacklist) > 0:
                    print("Blacklist.txt found and ready to use.")
                    return True
                else:
                    print("Blacklist.txt found, but empty.")
                    return False
        except:
            print("Blacklist.txt not found.")
            return False

    def start(self):
        if not self.usingBlacklist and not self.usingWhitelist:
            print("CAUTION: Server is running without filtering.")

        while True:
            # establish connection
            (clientSocket, clientAddr) = self.serverSocket.accept()

            clientName = clientAddr[0] + ':' + str(clientAddr[1])

            # allocate threads to deal with individual connections
            t = threading.Thread(target=self.requestHandler, args=(clientSocket, clientName), daemon=True)
            t.start()

    def requestHandler(self, clientConn, clientName):
        # get the request from browser
        request = clientConn.recv(self.config['MAX_REQUEST_LEN'])

        # parse the first line
        first_line = request.decode().split('\n')[0]

        # get url
        url = first_line.split(' ')[1]

        http_pos = url.find("://") # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of url

        port_pos = temp.find(":") # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:

            # default port 
            port = 80 
            webserver = temp[:webserver_pos] 

        else: # specific port 
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        if self.usingWhitelist: # filter out according to whitelist
            if webserver in self.whitelist:
                pass
            else:
                with open("serverlog.txt", 'a') as logWriter:
                    logWriter.write("Access denied on {} from {} to {}: host not in whitelist.\n".format(time.asctime(), clientName, webserver))
                clientConn.send("Oops. Host address not in whitelist!".encode())
                clientConn.close()
                return

        if self.usingBlacklist: # filter out according to blacklist
            if webserver in self.blacklist:
                with open("serverlog.txt", 'a') as logWriter:
                    logWriter.write("Access denied on {} from {} to {}: host is blacklisted.\n".format(time.asctime(), clientName, webserver))
                clientConn.send("Oops. Host address is blacklisted!".encode())
                clientConn.close()
                return
            else:
                pass

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.settimeout(self.config['CONNECTION_TIMEOUT'])
        s.connect((webserver, port))
        s.sendall(request)

        try:
            with open("temp.txt", 'w') as a:
                while True:
                    # receive data from web server
                    data = s.recv(self.config['MAX_REQUEST_LEN'])
                    # send the data back to client
                    clientConn.send(data)
        except:
            pass

        with open("serverlog.txt", 'a') as logWriter:
            logWriter.write("Access authorized on {} from {} to {}.\n".format(time.asctime(), clientName, webserver))

if __name__ == "__main__":
    config = dict(HOST_NAME='127.0.0.1', BIND_PORT=12345, MAX_REQUEST_LEN=2083, CONNECTION_TIMEOUT=0.5) # 2083 is the maximum size of HTTP URL
    proxy = Server(config)
    proxy.start()
