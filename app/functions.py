import csv
from json2html import *
import json
from flask import Markup
import paramiko
from datetime import datetime
from time import gmtime, strftime
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
op_sys = sys.platform

def log_login(attempt ,user, password):
	f = open('pass_log.txt', 'a')
	cur_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	if attempt is False:
		f.write('{} - Failed login attempt - User:{} -  Password:{}\n'.format(cur_time, user, password))
		f.close()
	else:
		f.write('{} - Successful login attempt - User:{} -  Password:{}\n'.format(cur_time, user, password))
		f.close()

def ssh_client_command(arg1, arg2, arg3):
	try:
		# Connect to remote computer
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect('192.168.1.10', username='pi', password='athlon21')
		stdin, stdout, stderr = client.exec_command(
			'sudo python3 /home/pi/wateringsys/new_cron.py {} {} {}'.format(arg1,arg2,arg3))

		status = str(stdout.read())
		cron_status = status[2:-3]
		print(cron_status)
		client.close()

	finally:
		return cron_status






def ssh_client(remote_location,local_location):
	# Connect to remote computer
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect('192.168.1.10', username='pi', password='athlon21')
	# Read remote file

	sftp_client = client.open_sftp()
	sftp_client.get(str(remote_location), str(local_location))


def get_current_timer():
	if op_sys == "win32":
		local_csv = dir_path + str("\\data\\timer_data.csv")
	else:
		local_csv = dir_path + str("/data/timer_data.csv")

	remote_csv = '/home/pi/wateringsys/timer_data.csv'

	# Get file

	ssh_client(
			remote_csv,
			local_csv
			)

	file = open(local_csv)

	str1 = ''.join(file)
	# Split file
	split_file = str1.split(',')
	# Convert to 12 hour time
	d = datetime.strptime("{}:00".format(str(split_file[0])), "%H:%M")
	am_pm_time = d.strftime("%I:%M %p")
	# Convert seconds to minutes
	m, s = divmod(int(split_file[2]), 60)
	timer_string = "The current timer is set to run at {} every {} days(s) for {} minutes and {} seconds".format(
		am_pm_time, split_file[1], m, s)

	return timer_string


def table():
	if op_sys == "win32":
		local_json = dir_path + str("\\data\\weather_data.csv")
	else:
		local_json = dir_path + str("/data/weather_data.csv")

	remote_csv = '/home/pi/wateringsys/weather_data.csv'

	ssh_client(
			remote_csv,
			local_json
			)


	f = open(local_json)

	# Change each field name to the appropriate field name. I know, so difficult.
	reader = csv.DictReader(f, fieldnames=("Time", "Temperature", "Humidity","Water Level"))
	# Parse the CSV into JSON in reverse
	out = json.dumps([row for row in reversed(list(reader))])
	# Save the JSON
	f = open(local_json, 'w')
	f.write(out)
	f.close()

	with open(local_json) as data_file:
		data = json.load(data_file)

	json_obj_in_html = Markup(json2html.convert(
		json=data, table_attributes="class=\"table table-bordered table-hover\""))

	return json_obj_in_html


