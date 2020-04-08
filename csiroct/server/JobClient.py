import time
import zmq
import sys

class JobClient(object):
    def __init__(self, port_job=5000, port_control=5001):
        self.port_job = port_job
        self.port_control = port_control

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(f'tcp://*:{port_job}')

    def submit_job(self):
        pass

    def stop_server(self):
        pass