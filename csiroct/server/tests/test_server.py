import pytest
import logging
import os.path
import time
import uuid
import csiroct.server as server
from multiprocessing import Process

logging.basicConfig(level=logging.DEBUG)

class TestServer:
    def client_process(self):
        jc = server.JobClient()

        for i in range(3):
            data = {}

            id = str(uuid.uuid1())

            # Geneate job id
            data['id'] = id
            data['name'] = i

            # Generate json
            json_data = json.dumps(data)

            jc.submit_job(json_data)

        print(f'Client process exiting')

    def server_process(self):
        js = server.JobServer()
        js.start()
        time.sleep(30)
        js.stop()
        
        print(f'Server process exiting')

    def test_server(self):
        # Create a server job client and on separate processes
        Process(target=self.server_process).start()
        time.sleep(1)
        Process(target=self.client_process).start()