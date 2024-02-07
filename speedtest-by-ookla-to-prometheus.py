#!/usr/bin/python3

import subprocess
from subprocess import PIPE
import json

from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from random import randrange
import time
import timeit
from urllib.parse import parse_qs, urlparse
import threading

import sys

from prometheus_client import start_http_server
from prometheus_client import Counter, Summary, Gauge

def data():

    while True:

        global ping
        #global download
        #global upload

        speedtest = subprocess.run("speedtest -s 48463 -f json", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        speedtest_result = speedtest.stdout
        #Debug print
        # print('{}'.format(speedtest_json)

        speedtest_json = json.loads(speedtest_result)

        #Debug print
        #print(speedtest_json)

        #data get and input
        ping = speedtest_json['ping']['latency']
        download_bps = speedtest_json['download']['bandwidth']
        upload_bps = speedtest_json['upload']['bandwidth']
        #packetloss = speedtest_json['packetLoss']

        #bps to Mbps
        download = download_bps/125000
        upload = upload_bps/125000

        #Debug print
        #print(ping)
        #print(download)
        #print(upload)

        ping_gauge.set(ping)
        download_gauge.set(download)
        upload_gauge.set(upload)
        #packetloss_gauge.set(packetloss)

        time.sleep(300)

ping_gauge = Gauge('my_home_internet_ping_nuro', 'My Home Internet Ping (NURO)')
download_gauge = Gauge('my_home_internet_download_nuro', 'My Home Internet Download (NURO)')
upload_gauge = Gauge('my_home_internet_upload_nuro', 'My Home Internet Upload (NURO)')
#packetloss_gauge = Gauge('my_home_internet_packetloss_nuro', 'My Home Internet PacketLoss (NURO)')

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'Hello World!! from {self.path} as GET'.encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

        content_length = int(self.headers['content-length'])
        body = self.rfile.read(content_length).decode('utf-8')

        print(f'body = {body}')

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'Hello World!! from {self.path} as POST'.encode('utf-8'))

if __name__ == '__main__':
    thread_1 = threading.Thread(target=data)
    thread_1.start()
    start_http_server(8000)

    with ThreadingHTTPServer(('0.0.0.0', 8080), MyHTTPRequestHandler) as server:
        print(f'[{datetime.now()}] Server startup.')
        server.serve_forever()
