import time
import zmq
import sys
from  multiprocessing import Process, Manager
from zmq.eventloop import ioloop, zmqstream

def getcommand(msg):
	print(f'Received control command: {msg}')
	if msg[0].decode('utf-8') == 'Exit':
		print('Received exit command, client will stop receiving messages')
		ioloop.IOLoop.instance().stop()
        
def process_message(msg):
	print(f'Processing ... {msg}')

def server(port_push, port_sub):    
	context = zmq.Context()
	socket_pull = context.socket(zmq.PULL)
	socket_pull.connect ("tcp://localhost:%s" % port_push)
	stream_pull = zmqstream.ZMQStream(socket_pull)
	stream_pull.on_recv(getcommand)
	print(f'Connected to server with port {port_push}')
	
	socket_sub = context.socket(zmq.SUB)
	socket_sub.connect ("tcp://localhost:%s" % port_sub)
	#socket_sub.setsockopt(zmq.SUBSCRIBE, "9")
	stream_sub = zmqstream.ZMQStream(socket_sub)
	stream_sub.on_recv(process_message)
	print(f'Connected to publisher with port {port_sub}')
	ioloop.IOLoop.instance().start()
	print('Worker has stopped processing messages.')


class JobServer(object):
    def __init__(self, port_job=5000, port_control=5001):
        self.port_job = port_job
        self.port_control = port_control

        self._manager = Manager()
        self._server_dict = self._manager.dict()
        self._server_dict['port_job'] = port_job
        self._server_dict['port_control'] = port_control

        ioloop.install()
       
    def start(self):
        # Start server in separate process
        Process(target=server, args=(self.port_control, self.port_job,)).start()
        time.sleep(2)

    def stop(self):
        print(f'Requesting server stop')
        # Request the server to stop
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://*:%s" % self.port_control)
        socket.send_string('Exit')

