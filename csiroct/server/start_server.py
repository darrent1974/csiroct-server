import logging
import os.path
import time
import csiroct.server as server

if __name__ == "__main__":
    # Create and start server
    js = server.JobServer()
    js.start()


