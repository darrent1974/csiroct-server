import time
import zmq
from zmq.devices.basedevice import ProcessDevice
from zmq.utils.strtypes import asbytes
from multiprocessing import Process
import json

class JobServer(object):
    def __init__(self, 
                jobqueue_frontend_port=5559, 
                jobqueue_backend_port=5560,
                jobstatus_frontend_port=5561,
                jobstatus_backend_port=5562):

        self.jobqueue_frontend_port = jobqueue_frontend_port
        self.jobqueue_backend_port = jobqueue_backend_port
        self.jobstatus_frontend_port = jobstatus_frontend_port
        self.jobstatus_backend_port = jobstatus_backend_port
       
        # Setup jobqueue streamer device
        self._jobqueue_streamer_device = self._setup_jobqueue_streamer_device(
            self.jobqueue_frontend_port,
            self.jobqueue_backend_port)

        '''
        # Setup jobstatus forwarder device
        self._jobstatus_forwarder_device = self._setup_jobstatus_forwarder_device(
            self.jobstatus_frontend_port,
            self.jobstatus_backend_port)
        '''

        # Create jobstatus forwarder process
        self._jobstatus_forwarder_process = Process(
            target=self._jobstatus_forwarder, 
            args=(self.jobstatus_frontend_port, self.jobstatus_backend_port,))

        # Create jobworker process
        self._jobworker_process = Process(
            target=self._jobworker, 
            args=(self.jobqueue_backend_port, self.jobstatus_frontend_port,))

        self._jobstatus_process = Process(
            target=self._jobstatus, 
            args=(self.jobstatus_backend_port,))


    def _setup_jobqueue_streamer_device(self, frontend_port, backend_port):
        print(f'Setting up streamer device, ports: {frontend_port}, {backend_port}')

        # Create a PyZMQ streamer device to serve as the jobqueue
        device = ProcessDevice(zmq.STREAMER, zmq.PULL, zmq.PUSH)

        print('created streamer device')

        # Setup device, need to use 127.0.0.1 rather than localhost
        # TODO: Look into why
        device.bind_in(f'tcp://127.0.0.1:{frontend_port}')
        device.bind_out(f'tcp://127.0.0.1:{backend_port}')
        device.setsockopt_in(zmq.IDENTITY, 'PULL'.encode('utf-8'))
        device.setsockopt_out(zmq.IDENTITY, 'PUSH'.encode('utf-8'))

        return device

    '''
    def _setup_jobstatus_forwarder_device(self, frontend_port, backend_port):
        print(f'Setting up forwarder device, ports: {frontend_port}, {backend_port}')

        # Create a PyZMQ fowarder device to serve as the job status
        device = ProcessDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)

        print('created forwarder device')

        # Setup device, need to use 127.0.0.1 rather than localhost
        # TODO: Look into why
        device.bind_in(f'tcp://127.0.0.1:{frontend_port}')
        device.bind_out(f'tcp://127.0.0.1:{backend_port}')

        device.setsockopt_in(zmq.IDENTITY, 'SUB'.encode('utf-8'))
        device.setsockopt_out(zmq.IDENTITY, 'PUB'.encode('utf-8'))
        #device.setsockopt_out(zmq.SUBSCRIBE, ''.encode('utf-8'))

        return device
    '''

    def _jobstatus_forwarder(self, frontend_port, backend_port):
        context = zmq.Context()
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind(f'tcp://*:{frontend_port}')
        
        frontend.setsockopt_string(zmq.SUBSCRIBE, '')
        
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind(f'tcp://*:{backend_port}')

        print(f'Starting forwarder: {frontend_port} {backend_port}')

        # Start the device
        zmq.device(zmq.FORWARDER, frontend, backend)

        print('Forwarder finished')

    def _jobworker(self, jobqueue_port, jobstatus_port):
        context = zmq.Context()

        # Setup  pull socket for receiving jobs
        socket_pull = context.socket(zmq.PULL)
        socket_pull.connect(f'tcp://localhost:{jobqueue_port}')

        socket_pub = context.socket(zmq.PUB)
        socket_pub.connect(f'tcp://localhost:{jobstatus_port}')

        time.sleep(1)
        print(f'Jobworker process listening on port: {jobqueue_port}')
        
        while True:
            # Receive job json
            job_json = socket_pull.recv_json()

            # Execute the job
            self._run_job(json.loads(job_json), socket_pub)

        print(f'Exiting jobworker process')

    def _jobstatus(self, jobstatus_port):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(f'tcp://localhost:{jobstatus_port}')
        socket.setsockopt_string(zmq.SUBSCRIBE, '')

        print(f'Jobstatus process listening on port: {jobstatus_port}')

        while True:
            # Receive status string
            message = socket.recv_string()
            print(f'Jobstatus: {message}')

        print(f'Exiting jobstatus process')


    def _run_job(self, job_data, socket_pub):
        job_id = job_data['id']

        socket_pub.send_string(f'JobWorker running job, id: {job_id}')
        time.sleep(5)
        socket_pub.send_string(f'JobWorker job completed, id: {job_id}')

     
    def start(self):
        print(f'Starting JobServer')

        # Start the jobstatus fowarder running in it's own process
        self._jobstatus_forwarder_process.start()

        # Start the jobstatus process
        self._jobstatus_process.start()

        # Start the jobqueue stream running in it's own process
        self._jobqueue_streamer_device.start()

        # Start the jobworker process
        self._jobworker_process.start()


    def stop(self):
        # Terminate process
        self._jobstatus_forwarder_process.terminate()
        self._jobworker_process.terminate()
        self._jobstatus_process.terminate()

        print(f'Stopped JobServer')
