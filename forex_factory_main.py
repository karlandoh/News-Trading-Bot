#!/usr/local/bin/python3

import datetime
import threading

from forexfactory_linux import *
from forexfactory_mt4 import *

favourite_times = []

if len(favourite_times) > 0:
	impact_mode = favourite_times[0][1]
else:
	impact_mode = 'High'

def dump_port(port=1980):
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

def main(s,mt4):
	
	#status = postgresql()

	s.server['injector_status'].set('ONLINE')

	print('Changed to online.')

	t = 0

	s.original_list = s.server['datalist'].get()
		
	while True:

		#THIS STILL STANDS!
		today = datetime.datetime.now()

		#SWITCH (ON) | The slots have to be within: | 3 minutes before + 5 minutes after | the target time.
		#if time_monitor == True:
		#	if any(-3*60 <= (today-x['date']).total_seconds() <= 5*60 for x in original_list) == True and status.fetch() == 'Offline':
		#		status.online()
		#		print('[TIME MONITOR] Turning back on!')

		t+=1
		online_list = s.server['datalist'].get()

		print(t)

		#print(online_list)

		#I want entries that EARLY by 5 minutes max.
		filtered_list = [x for x in online_list if -5*60 <= (today-x['date']).total_seconds()]

		#Dont keep an expired entry for more than 5 minutes.
		filtered_list = [x for x in filtered_list if (today-x['date']).total_seconds() <= 5*60]

		#Filter out the late entries that are active trades.
		filtered_list = [x for x in filtered_list if [x['title'],x['date'],x['currency']] not in mt4.active_trades]
		
		s.cache_list = filtered_list

		#SWITCH (OFF)
		#if time_monitor == True:
		#	if len(filtered_list) == 0 and status.fetch() == 'Online':
		#		print('[TIME MONITOR] Nothing is in the list!')
		#		status.offline()

		print(filtered_list)

		duplicate_list = [x for x in filtered_list if x['mode'] == 'DUPLICATE'] #BETA

		if any(x['mode'] == 'DUPLICATE' for x in filtered_list) == True:

			result = s.duplicate_scan(duplicate_list)
			
			if result == 'GOOD' or result == 'BAD':
				mt4.send_trade(duplicate_list[0]['currency'], result) #BETA
				for duplicate_result in duplicate_list:
					mt4.active_trades.append([duplicate_result['title'],duplicate_result['date'],duplicate_result['currency']])

		for entry in filtered_list:
			if entry['mode'] == 'DUPLICATE':
				pass
			else:
				print('BETA')
				if entry['status'] == 'GOOD' or entry['status'] == 'BAD':
					#import ipdb
					#ipdb.set_trace()
					mt4.send_trade(entry['currency'],entry['status'])
					mt4.active_trades.append([entry['title'],entry['date'],entry['currency']])



if __name__ == '__main__':
	server_ip = '192.168.11.16'

	s = linux_server(server_ip,time_monitor=True)
	mt4 = zmq_python()

	try:
		main(s,mt4)
	except:
		raise
	finally:

		for process in mt4.mt4_processes:
			process.kill()

		s.stop_thread = True
		
		try:
			s.server['injector_status'].set('OFFLINE')
		except:
			pass

		for i in range(5):
			try:
				dump_port()
			except:
				continue