import logging
#import itk
import os.path
#import numpy as np
#import math
import time
import zmq
import csiroct.server as server
from multiprocessing import Process
import json
import uuid
from zmq.devices.basedevice import ProcessDevice

def client_process():
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

def server_process():
    js = server.JobServer()
    js.start()
    time.sleep(30)
    js.stop()
    
    print(f'Server process exiting')

if __name__ == "__main__":
    # Create a server job client and on separate processes
    Process(target=server_process).start()
    time.sleep(1)
    Process(target=client_process).start()


