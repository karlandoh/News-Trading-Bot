import os
import time
import zmq
import datetime
import multiprocessing, threading
import statistics as stats

import pandas as pd 
import numpy as np

context = zmq.Context()  

class zmq_python():
    
    def __init__(self):
        # Create ZMQ Context

        print('Created class.')

    def initialize(self):

        socket = self.connect()

        print('Waiting for open sockets from MT4...')

        i=0

        socket.send_string('Requesting connection.')

        msg = socket.recv().decode()

        print(f"Message reply -> {msg}")

        print('Successful python connection!')


    def dump_port(self,port=1980):
        import subprocess, os
        from pprint import pprint

        try:
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
        except Exception as e:
            if str(e) == "Command 'netstat -ano | findstr :5585' returned non-zero exit status 1.":
                return None

        pprint(output)

        ls = list(set([int(x.strip().split(' ')[-1]) for x in output.split('\r\n') if x.strip().split(' ')[-1] != '0' and x.strip().split(' ')[-1] != '']))

        for number in ls:
            os.system(f"taskkill/pid  {number} /F")

    def connect(self):

        socket = context.socket(zmq.REQ)
        socket.bind(f"tcp://127.0.0.1:1980")

        return socket

    def send_trade(self,price,lot_size,tp):
        pass



if __name__ == '__main__':
    a = zmq_python()

    a.initialize()

    #a.stress_test()

    #zmq_python().send_off("GBPUSD|no")