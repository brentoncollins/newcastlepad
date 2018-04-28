import csv
from json2html import *
import json
from flask import Markup
import paramiko
from datetime import datetime
from time import gmtime, strftime
import os
from app import app


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


def service_table():
	services = {"Sonarr": False, "Plex Media Server": False, "Open VPN": False, "Tautulli": False}
	for k, v in services.items():
		stat = os.system('service {} status'.format(k.replace(" ", "").lower()))
		print(k.replace(" ", "").lower())
		if stat == 0:
			services[k] = True
	data = json.dumps([{'Service': k, 'Status': v} for k, v in services.items()], indent=4)

	json_obj_in_html = Markup(json2html.convert(
		json=data, table_attributes="class=\"table table-bordered table-hover\""))

	return json_obj_in_html


def humanbytes(b):
	"""Return the given bytes as a human friendly KB, MB, GB, or TB string"""
	b = float(b)
	kb = float(1024)
	mb = float(kb ** 2) # 1,048,576
	gb = float(kb ** 3) # 1,073,741,824
	tb = float(kb ** 4) # 1,099,511,627,776

	if b < kb:
		return '{0} {1}'.format(b, 'Bytes' if 0 == b > 1 else 'Byte')
	elif kb <= b < mb:
		return '{0:.2f} KB'.format(b/kb)
	elif mb <= b < gb:
		return '{0:.2f} MB'.format(b/mb)
	elif gb <= b < tb:
		return '{0:.2f} GB'.format(b/gb)
	elif tb <= b:
		return '{0:.2f} TB'.format(b/tb)


def getfiles():
	direc = os.path.join(app.instance_path)
	# Get current working directory

	file_dict = {}
	# Create an empty dict

	# Select only files with the ext extension
	if op_sys == "win32":
		slash = str("\\")
	else:
		slash = str("/")

	for file in os.listdir(direc):

		if file == ".gitignore":
			continue
		size = os.path.getsize(app.instance_path + "{}{}".format(slash, file))
		file_dict[file] = humanbytes(size)

	data = json.dumps([{'File': k, 'Size': v} for k, v in file_dict.items()], indent=4)

	json_obj_in_html = Markup(json2html.convert(
		json=data, table_attributes="class=\"table table-bordered table-hover\""))

	return json_obj_in_html




