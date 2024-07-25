# -*- coding: utf-8 -*-
# It was developed by JM-1000.

import sys
import socket
import unittest
import threading
from os import path
from time import sleep
from json import loads
# Local library imports
# Add the sensor directory of 'custom_sensor_lib' to the system path
dir = path.dirname(path.dirname(path.dirname(__file__)))
sys.path.append(dir) 
from custom_sensor_lib import client_socket


# This class act as the iceriver miner server
class ServerSocket():
    def __init__(self, address: tuple):
        self.commands = []
        self.returned_data = 'Ok'
        self.stop_server = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(address)
        self._socket.listen(5)
        self.server_thread = threading.Thread(daemon=True, 
                                              target=self.handle_request)

    # Receive request and send response to a client socket
    def handle_request(self):
        client_sock, _ = self._socket.accept()
        while not self.stop_server:
            try:
                sleep(0.1)
                request = str(client_sock.recv(1024), 'ascii')
                for index, cmd in enumerate(self.commands):
                    if loads(request)['id'] == cmd:
                        response = bytes("%s\n" %self.returned_data[index],
                                        'ascii')
                        client_sock.send(response)
            except: 
                client_sock.close()
                client_sock, _ = self._socket.accept()
        self._socket.shutdown()


class TestClientSocket(unittest.TestCase):
    # This function is executed before each test function
    def setUp(self):
        # Sample of the data returned by an iceriver miner 
        self.iceriver_miner_data = [
                '{"id": "fan", "ret": {"code": 0, "fans": [300, 100]}}', 
                '{"id": "board", "ret": {"code": 0, "boards": [' 
                    '{"no": 1, "chipnum": 18, "rtpow": "36.71G",' 
                    '"intmp": 34, "outtmp": 52, "state": true}]}}', 
                '{"id": "boardpow", "ret": {' 
                    '"code": 0, "rtpow": "155G", "avgpow": "152G",' 
                    '"runtime": "00:09:21:23", "unit": "G"}}', 
                '{"id": "getnet", "ret": ' 
                    '{"code": 0, "nic": "eth0", "host": "KS0-2"}}', 
                '{"id": "getpool", "ret": {"code": 0, "pools": [' 
                    '{"no": 1, "connect": true, "diff": "2199.02 G",' 
                    '"priority": 1, "accepted": 2418, "rejected": 0,' 
                    '"state": 1}]}}'
        ]
        # Server side
        self.address = ('127.0.0.1', 41111)
        self.server = ServerSocket(self.address)
        self.server.commands = ['fan', 'board', 
                                'boardpow', 'getnet','getpool']
        self.server.returned_data = self.iceriver_miner_data
        self.server.server_thread.start()
    

    # Client side
    def test_client_socket_class(self): 
        # Execution
        client_sock = client_socket.ClientSocket(*self.address, 
                                                 self.server.commands,
                                                 '{"id": "%s"}\n')
        returned_data = client_sock.fetch_data()
        # Testing the expected result
        self.assertEqual(len(returned_data), 5)
        for element in returned_data:
            self.assertIn(element.replace('\n', ''), 
                          self.iceriver_miner_data)


    # This function is executed after each test function
    def tearDown(self): 
        self.server.stop_server = True


if __name__ == '__main__':
    unittest.main()
    