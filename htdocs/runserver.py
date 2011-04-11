#!/usr/bin/env python

from os import chdir, path
import BaseHTTPServer, SimpleHTTPServer

def runserver(host="", port=8000):
    svr_cls = BaseHTTPServer.HTTPServer
    hdl_cls = SimpleHTTPServer.SimpleHTTPRequestHandler
    chdir(path.dirname(__file__))
    addr = (host, port)
    hdl_cls.protocol_version = "HTTP/1.0"
    httpd = svr_cls(addr, hdl_cls)
    bound = httpd.socket.getsockname()[0]
    if bound == "0.0.0.0":
        bound = "127.0.0.1"
    print "Go to http://%s:%d/" % (bound, port)
    httpd.serve_forever()

if __name__ == "__main__":
    runserver()
