from flask import render_template, request, flash, redirect, url_for, Markup, send_from_directory
from app import app
import os
from app import functions
from flask_login import LoginManager, UserMixin
import flask_login
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename


hash_pwd = "$pbkdf2-sha256$200000$2VurNaZUilGKMYbQGkOIEQ$Ye8XIkqYZVCaPnttm0W27whUajlEA6NvFPIaJhLOorU"
users = ['bobcat']

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.urandom(12)
login_manager.login_view = 'login'


class User(UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
		if email not in users:
			return
		user = User()
		user.id = email
		return user

@login_manager.request_loader
def request_loader(request):
		email = request.form.get('email')
		if email not in users:
			return
		user = User()
		user.id = email

		# DO NOT ever store passwords in plaintext and always compare password
		# hashes using constant-time comparison!
		user.is_authenticated = pbkdf2_sha256.verify(request.form['password'], hash_pwd)
		return user

@login_manager.unauthorized_handler
def handle_needs_login():
    flash("You have to be logged in to access this page.")

    return redirect(url_for('login', next_page=request.endpoint))

@app.route('/login', methods=['GET', 'POST'])
def login():

		next_page = request.args.get("next_page")

		if request.method == 'GET':
			# Pass variable to html so it doesn't get lost
			return render_template("login.html", next_page = request.args.get("next_page"))

		email = request.form['email']
		if request.form['email'] is None:

			return redirect(url_for('login'))
		next_page = request.form['location']
		print(next_page)
		if pbkdf2_sha256.verify(request.form['password'], hash_pwd) is True:
				# Get stored html variable back for redirect to next page.
				next_page = request.form['location']
				print(next_page)
				user = User()
				user.id = email
				flask_login.login_user(user)
				print(next_page[:-1])


				return redirect(url_for(next_page))
				#return index()
		else:
			functions.log_login(pbkdf2_sha256.verify(request.form['password'], hash_pwd), email, request.form['password'])
			flash("Wrong login or password.")

			return redirect(url_for('login'))



@app.route('/logout')
def logout():
	flask_login.logout_user()
	return login()


@app.route('/')
@flask_login.login_required
def home():

	return render_template("index.html")


@app.route('/protected')
@flask_login.login_required
def protected():

	return 'Logged in as: ' + flask_login.current_user.id


@app.route('/index')
@flask_login.login_required
def index():

	return render_template("index.html")


@app.route('/internet')
@flask_login.login_required
def internet():
	table = functions.service_table()

	return render_template("internet.html", service_status=table)


@app.route('/about')
@flask_login.login_required
def about():

	return render_template("about.html")


@app.route('/watersys')
@flask_login.login_required
def watersys():

	return render_template(
		"watersys.html",
		table_data=functions.weather_table(),
		current_timer=functions.get_current_timer(),
		entries=[
			"1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM",
			"9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM", "4PM",
			"5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM", "12AM"],
		days=[1, 2, 3, 4, 5, 6, 7, 8]
			)


@app.route("/water_time", methods=['GET', 'POST'])
@flask_login.login_required
def time_input():
	x = (request.form['button1'].split(','))
	d = datetime.strptime(x[0], "%I%p")
	hour = d.strftime("%H")
	cron_status = functions.ssh_client_command(hour, x[1], x[2])
	flash(cron_status)

	return redirect(url_for('watersys'))
# return ('', 204)


@app.route('/upload')
@flask_login.login_required
def upload():
	table = Markup(functions.getfiles())

	return render_template('upload.html', file_table=table)


@app.route('/uploader', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	try:
		if request.method == 'POST':
			for f in request.files.getlist('file'):
				f.save(os.path.join(app.instance_path, secure_filename(f.filename)))

				flash('{} uploaded successfully.'.format(f.filename))

			return redirect(url_for("upload"))
	except UnboundLocalError:
		flash("No file selected.")
		return redirect(url_for("upload"))

@app.route('/downloader', methods=['GET', 'POST'])
@flask_login.login_required
def get_file():
	if request.method == 'POST':
		f = request.form['filename']
		send_from_directory(os.path.join(app.instance_path), f)

	return send_from_directory(os.path.join(app.instance_path), f, as_attachment=True)


@app.route('/remove_file', methods=['GET', 'POST'])
@flask_login.login_required
def remove_file():
	if request.method == 'POST':
		f = request.form['filename']
		path = "{}{}{}".format(os.path.join(app.instance_path), functions.get_slash(), f)
		os.remove(path)

		return redirect(url_for("upload"))

