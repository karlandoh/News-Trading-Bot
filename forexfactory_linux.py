#!/usr/local/bin/python3

import zmq
import datetime
import subprocess
import time
import threading
import os

from forex_factory_main import favourite_times, impact_mode


class linux_server(): 
	def __init__(self,server_ip = '192.168.11.16',time_monitor=False):
		
		self.server_ip = server_ip
		self.stop_thread = False

		while True:
			try:
				self.server = self.fetch_locks()
				break
			except ConnectionRefusedError:
				print('[LINUX] Waiting for linux server to initiate...')
				time.sleep(1)

		if time_monitor == True:
			threading.Thread(target=self.time_monitor).start()


	def time_monitor(self):
		from arbyPOSTGRESstatus import postgresql

		record_thread = threading.Thread(target=self.record_obs)

		print("[TIME MONITOR] Initiating!")
		print('[TIME MONITOR] Waiting for cache list...')

		status = postgresql(self.server_ip)
		status.online(impact_mode)

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

			#SWITCH (ON) | The slots have to be within: | 3 minutes before + 5 minutes after | the target time.
			
			if len(favourite_times)>0:
				for slot in favourite_times:
					print(f"There is a slot in favourite time! {slot}")
					if -5*60 <= (datetime.datetime.now()-datetime.datetime.strptime(slot[0], "%Y.%m.%d %H:%M")).total_seconds() <= 5*60:
						if record_thread.is_alive() == False:
							record_thread = threading.Thread(target=self.record_obs)
							record_thread.start()

						status.online(slot[1])

				if any(-5*60 <= (datetime.datetime.now()-datetime.datetime.strptime(x[0], "%Y.%m.%d %H:%M")).total_seconds() <= 5*60 for x in favourite_times) == False:
					status.offline()

			else:
				if any(-5*60 <= (datetime.datetime.now()-x['date']).total_seconds() <= 5*60 for x in self.original_list) == True:
					
					if record_thread.is_alive() == False:
						record_thread = threading.Thread(target=self.record_obs)
						record_thread.start()

					status.online(impact_mode)
				else:
					status.offline()

			time.sleep(10)

	def record_obs(self):
		os.system("""taskkill /F /IM obs64.exe""")
		os.system("""start /d "C:\\Program Files\\obs-studio\\bin\\64bit" obs64.exe --startrecording""")
		time.sleep(600)

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