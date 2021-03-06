import csv
from json2html import *
import html
from flask import Markup
import paramiko
from datetime import datetime
from time import gmtime, strftime
import os
from app import app
import urllib.request


dir_path = os.path.dirname(os.path.realpath(__file__))
op_sys = sys.platform


def log_login(attempt, user, password):
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
	"""Get the current timer status"""
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


def weather_table():
	"""Create table to view weather stats"""
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
	json_file = ([row for row in reversed(list(reader))])

	f.close()

	json_obj_in_html = Markup(json2html.convert(
		json=json_file, table_attributes="class=\"table table-bordered table-hover\""))

	return json_obj_in_html


def service_table():
	"""Create a table to see services running"""
	# Add services that you want to check, set to false.
	services = [({"Service":'Sonarr',"Status": False, "Port": "8090"}),
				({"Service": 'Plex Media Server', "Status": False, "Port": "N/A"}),
				({"Service": 'OpenVPN', "Status": False, "Port": "N/A"}),
				({"Service": 'Tautulli', "Status": False, "Port": "8090"}),
				({"Service": 'Jackett', "Status": False, "Port": "9117"}),
				({"Service": 'Cockpit', "Status": 'apache2', "Port": "9090"}),
				({"Service": 'Guacamole', "Status": 'apache2', "Port": "8080"}),
				({"Service": 'Qbittorrent', "Status": 'apache2', "Port": "8090"}),
				#({"Service": 'OpenVPN Status', "Status": 'apache2', "Port": "5555"}),
				]

	for k in services:
		print(k)
		# Get the status of all services, if 0 (Running) else (Not running)
		if k['Status'] is False:
			stat = os.system('service {} status'.format(k['Service'].replace(" ", "").lower()))
			print(stat)
			print(k['Service'].replace(" ", "").lower())
			if stat == 0:
				k['Status'] = True
		if k['Status'] is "apache2":
			k['Status'] = False
			try:
				status = urllib.request.urlopen("http://127.0.0.1:{}".format(k['Port'])).getcode()
			except urllib.error.URLError:
				continue
			print(status)
			if status is 200:
				k['Status'] = True
			else:
				k['Status'] = False
	json_obj_in_html = Markup(json2html.convert(
		json=services, table_attributes="class=\"table table-bordered table-hover\""))

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


def remove_file(file):
	"""Remove file from uploads"""
	os.remove(file)


def get_slash():
	"""Get the string of correct backslash for windows/linux"""
	if op_sys == "win32":
		slash = str("\\")
	else:
		slash = str("/")

	return slash


def getfiles():
	"""Create table of all files in directory"""
	direc = os.path.join(app.instance_path)
	# Get current working directory
	file_list = []
	slash = get_slash()

	json_obj = []
	# Create dict to convert into json
	for file in os.listdir(direc):
		if file == ".gitignore":
			continue
		file_list.append(file)
		size = os.path.getsize(app.instance_path + "{}{}".format(slash, file))
		json_obj.append({"File":
								"<form action = '/downloader' method = 'POST'> <button type = 'submit' name ='filename' value = '{}' id = 'name' class = 'btn-link'> {} </button></form>".format(file, file, file),
								"Size" : humanbytes(size),"Remove" : "<form action = '/remove_file' method = 'POST'> <button type = 'submit' name ='filename' value = '{}' id = 'name' class = 'btn-link'> {} </button></form>".format(file, "Delete")})


	# Pass to json2html and wrap with Markup to ensure all chars are returned into html format.
	json_obj_in_html = json2html.convert(
		json=json_obj, table_attributes="class=\"table table-bordered table-hover\"")

	return [file_list, Markup(html.unescape(json_obj_in_html))]

