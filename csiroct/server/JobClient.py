import time
import zmq
import sys
import os
import json

class JobClient(object):
    def __init__(self, jobqueue_frontend_port=5559):
        self._jobqueue_frontend_port = jobqueue_frontend_port

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUSH)
        self._socket.connect(f'tcp://localhost:{self._jobqueue_frontend_port}')

    def submit_job(self, job_json):
        self._socket.send_json(job_json)

        data = json.loads(job_json)

        print(f'Job Submitted: {data}')

        return data['id']


