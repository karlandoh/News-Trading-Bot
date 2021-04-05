#!/usr/local/bin/python3

import zmq
import datetime
import subprocess
import time
import threading

server_ip = '192.168.11.16'

class linux_server(): #THIS DATABASE IS THE WHEEL.
	def __init__(self,server_ip = '192.168.11.16',time_monitor=False):
		self.server_ip = server_ip

		while True:
			try:
				self.server = self.fetch_locks()
				break
			except ConnectionRefusedError:
				print('[LINUX] Waiting for linux server to initiate...')
				time.sleep(1)

		if time_monitor == True:
			self.stop_thread = False
			threading.Thread(target=self.time_monitor).start()


	def time_monitor(self):
		from arbyPOSTGRESstatus import postgresql

		print("[TIME MONITOR] Initiating!")
		print('[TIME MONITOR] Waiting for cache list...')

		status = postgresql()
		status.online()

		while True:
			if self.stop_thread == True:
				print("[TIME MONITOR] Quitting!")
				break

			try:
				self.original_list
				break
			except AttributeError:
				pass

			time.sleep(1)


		print(f'original_list - {self.original_list}')

		while True:

			if self.stop_thread == True:
				break

			try:
				cache_list = self.cache_list
			except AttributeError:
				time.sleep(1)
				continue

			#SWITCH (OFF)
			#if len(cache_list) == 0 and status.fetch() == 'Online':
			#	print('[TIME MONITOR] Nothing is in the list!')
			#	status.offline()

			#SWITCH (ON) | The slots have to be within: | 3 minutes before + 5 minutes after | the target time.
			if any(-5*60 <= (datetime.datetime.now()-x['date']).total_seconds() <= 5*60 for x in self.original_list) == True:
				status.online()
			else:
				status.offline()

			time.sleep(10)

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
		if all('GOOD' in x['status'] for x in the_list) == True:
			return 'GOOD'

		if all('BAD' in x['status'] for x in the_list) == True:
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
			mt4_currency = 'EURUSD'

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
