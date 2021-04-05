#!/usr/local/bin/python3

import zmq
import datetime
import subprocess
import time

server_ip = '192.168.11.16'

class linux_server(): #THIS DATABASE IS THE WHEEL.
	def __init__(self,server_ip = '192.168.11.16'):
		self.server_ip = server_ip

		while True:
			try:
				self.server = self.fetch_locks()
				break
			except ConnectionRefusedError:
				print('[LINUX] Waiting for linux server to initiate...')
				time.sleep(1)

	def fetch_locks(self):
		from multiprocessing.managers import BaseManager
		import multiprocessing

		class QueueManager(BaseManager): pass

		dict = []

		QueueManager.register('shared_datalist')
		QueueManager.register('injector_status')

		m = QueueManager(address=(self.server_ip,50000), authkey=b'key')

		m.connect()

		datalist = m.shared_datalist()
		injector_status = m.injector_status()

		return {'datalist': datalist, 'injector_status': injector_status}

	def duplicate_scan(self,the_list):
		if all(x['status'] == 'GOOD' for x in the_list) == True:
			return 'GOOD'

		if all(x['status'] == 'BAD' for x in the_list) == True:
			return 'BAD'


class zmq_python():
	
	def __init__(self,port=1980,instances=1):
		# Create ZMQ Context

		self.mt4_process = subprocess.Popen(['C:\\Program Files (x86)\\VantageFX MT4\\terminal.exe'])

		self.mt4_instances = []

		self.context = zmq.Context() 
		self.port = port
		self.socket = self.initialize(instances)

		self.active_trades = []



		print('Created class.')

	def initialize(self,instances):

		socket = self.context.socket(zmq.ROUTER)
		socket.bind(f"tcp://127.0.0.1:{self.port}")		


		for i in range(instances):

			identity = socket.recv().decode()
			socket.recv()
			msg = socket.recv().decode()

			print(msg)

			socket.send_string(identity,zmq.SNDMORE)
			socket.send_string('',zmq.SNDMORE)

			if identity not in self.mt4_instances:
				socket.send_string(str(5))
			else:		
				socket.send_string("CONTINUE!")
				continue

			#FLIP TO INVERSE DEALER/REP SETUP.
			socket.recv()
			socket.recv()
			socket.recv()			
			
			print(f'Exchange connection initialized. ({identity})')

			self.mt4_instances.append(identity)

		return socket

	def send_trade_beta(self,currency,price,lot_size,tp):
		pass

	def send_trade(self,currency,status): #CURRENTLY 5 CHARTS

		if currency == 'USD':
			mt4_currency = 'NZDUSD'

			if status == 'GOOD':
				buyorsell = 'SELL'
			else:
				buyorsell = 'BUY'

		if currency == 'EUR':
			mt4_currency = 'EURUSD'
			
			if status == 'GOOD':
				buyorsell = 'BUY'
			else:
				buyorsell = 'SELL'

		if currency == 'NZD':
			mt4_currency = 'NZDUSD'

			if status == 'GOOD':
				buyorsell = 'BUY'
			else:
				buyorsell = 'SELL'

		if currency == 'GBP':
			mt4_currency = 'GBPUSD'

			if status == 'GOOD':
				buyorsell = 'BUY'
			else:
				buyorsell = 'SELL'

		if currency == 'JPY':
			mt4_currency = 'USDJPY'

			if status == 'GOOD':
				buyorsell = 'SELL'
			else:
				buyorsell = 'BUY'

		if currency == 'AUD':
			mt4_currency = 'AUDUSD'

			if status == 'GOOD':
				buyorsell = 'BUY'
			else:
				buyorsell = 'SELL'

		for identity in self.mt4_instances:
   			
			self.socket.send_string(identity,zmq.SNDMORE)
			self.socket.send_string('',zmq.SNDMORE)

			self.socket.send_string(f"{mt4_currency}|{buyorsell}")

			self.socket.recv().decode()
			self.socket.recv()
			msg = self.socket.recv().decode()
