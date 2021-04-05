#!/usr/local/bin/python3

import zmq
import subprocess
import os

class zmq_python():
	
	def __init__(self,port=1980,instances=2):
		# Create ZMQ Context

		self.mt4_processes = []
		self.mt4_processes.append(subprocess.Popen(['C:\\Program Files (x86)\\VantageFX MT4\\terminal.exe'])) #LQDFX
		self.mt4_processes.append(subprocess.Popen(['C:\\Program Files (x86)\\FXCM MetaTrader4\\terminal.exe'])) #COINEXX
		
		self.mt4_instances = []

		self.context = zmq.Context() 
		self.port = port
		self.socket = self.initialize(instances)

		self.active_trades = []

		print('Created class.')

	def initialize(self,instances,currencies=7):

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
				socket.send_string(str(currencies))
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

		if currency == 'CHF':
			mt4_currency = 'USDCHF'

			if status == 'GOOD':
				buyorsell = 'SELL'
			else:
				buyorsell = 'BUY'

		if currency == 'CAD':
			mt4_currency = 'USDCAD'

			if status == 'GOOD':
				buyorsell = 'SELL'
			else:
				buyorsell = 'BUY'


		for identity in self.mt4_instances:
   			
			self.socket.send_string(identity,zmq.SNDMORE)
			self.socket.send_string('',zmq.SNDMORE)

			self.socket.send_string(f"{mt4_currency}|{buyorsell}")

			self.socket.recv().decode()
			self.socket.recv()
			msg = self.socket.recv().decode()
