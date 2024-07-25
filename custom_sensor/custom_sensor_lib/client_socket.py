# -*- coding: utf-8 -*-
# MIT License

# Copyright (c) 2024 Juari Marcolino

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
from time import sleep


class ClientSocket():
    """
    This class is used to create a client socket to 
    communicate with the miner.
    """

    _CONNECTION_TYPE = (socket.AF_INET, socket.SOCK_STREAM)
    _ENCODING = 'utf-8'
    _BUFFER_SIZE = 4096

    def __init__(self, server_ip: str, server_port: int, 
                 miner_cmds: list, miner_msg_format: str, 
                 wait_time: float=100):
        """
        Constructor for the ClientSocket class.

        Parameters:
        server_ip (str)         : The IP address of the miner.
        server_port (int)       : The port for the miner monitoring interface.
        miner_cmds (list)       : Miner specific commands. 
        miner_msg_format (str)  : Miner specific request message format. 
        wait_time (float)       : The waiting time for the socket 
        in milliseconds (> 100ms).
        """

        self._data = []
        self._server_addr = (server_ip, server_port)
        self._wait_time = wait_time / 1000 if wait_time > 100 else 0.1
        self._commands = miner_cmds
        self._msg_format = miner_msg_format
        
    
    def _connect(self):
        # Create a socket and connect to the miner
        try:
            self._socket = socket.socket(*self._CONNECTION_TYPE)
            self._socket.connect(self._server_addr)
        except Exception as e:
            raise Exception(e)


    def _recv_msg(self):
            try:
                self._data.append("")
                while 1:
                    # Set a timeout to listen to a response
                    self._socket.settimeout(self._wait_time * 3)
                    _msg = str(self._socket.recv(self._BUFFER_SIZE), 
                               self._ENCODING)
                    if _msg: self._data[-1] += _msg
                    else: break
            except socket.timeout: pass
            except (ConnectionAbortedError, OSError) as e: 
                self._socket.close()
            except Exception as e:
                self._socket.close()
                raise Exception(e)


    def _send_msg(self, _msg: str):
        try:
            if _msg:
                self._socket.send(_msg.encode(self._ENCODING))
        except OSError:
            self._socket.close()
        except Exception as e: 
            self._socket.close()
            raise Exception(e)


    def fetch_data(self) -> list:
        """
        This method is used to fetch data from the miner.

        It sends a request with a command in a specific format and then  
        listen for the response using a receaving thread function.
        """

        self._connect()
        for _cmd in self._commands:
            for _ in range(3):
                self._send_msg(self._msg_format %_cmd)
                # Try to receive the response
                self._recv_msg()
                if self._data[-1]: break
                else: 
                    # Resend the command
                    self._data.pop()
                    self._connect()
                    sleep(self._wait_time * 3)
        self._socket.close()
        return self._data

