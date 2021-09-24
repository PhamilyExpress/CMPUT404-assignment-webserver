#  coding: utf-8 
import socketserver, os, urllib.parse

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        parsed_data = urllib.parse.urlparse(self.data)
        path = parsed_data.path.decode().split('\r\n')[0]
        url = path.split(' ')[1]
        self.url = "www" + url
        header = ""

        method = path.split(' ')[0]
        if method != "GET":
            header = "HTTP/1.1 405 Method Not Allowed\nContent-Type: text/plain\nContent-Length: 0\r\n"
        else:
            header = self.fileSearch()

        self.request.sendall(bytearray(header, 'utf-8'))

    def fileSearch(self):
        content_type = "text/plain;"

        url_periods_split = self.url.split(".")

        if os.path.exists(self.url):
            if self.url[-1] == "/":
                self.url += "index.html"
                content_type = "text/html;"

            elif os.path.isdir(self.url):
                self.url += "/"
                message = "HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080" + self.url[3:] + "\r\nContent-Type: " \
                    + content_type +" charset=UTF-8\r\nContent-Length: 0\r\nConnection: close\r\n"
                return message

            elif url_periods_split[-1] == "html":
                content_type = "text/html;"

            elif url_periods_split[-1] == "css":
                content_type = "text/css;"

            elif os.path.isfile(self.url):
                self.url += "index.html"
                try:
                    file = open(self.url, "r").read()
                except:
                    return self.Code404()

            try:
                file = open(self.url, "r").read()
                header = "HTTP/1.1 200 OK\r\nContent-Type: " + content_type + " charset=UTF-8\r\nConnection: close\r\n\r\n" + file + "\r\n"
                return header
            except:
                return self.Code404()
        else:
            return self.Code404()

    def Code404(self):
        header = "HTTP/1.1 404 Not Found\nContent-Type: text/plain\r\nConnection: close\r\n\r\n"
        return header

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
