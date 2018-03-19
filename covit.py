from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import sys
import os.path
app = Flask(__name__)
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'
database_name = ["userinfo.db"] # doign this so it is passed by reference
# Python Processing
def eprint(*s):
	print(*s, file=sys.stderr)

# Initial Variable Management
@app.before_first_request
def initial():
	eprint("STARTUP")
	database_name[0] = "userinfo.db"
	if len(sys.argv) > 1:
		database_name[0] = sys.argv[1];
	if not os.path.isfile("data/%s" % database_name[0]):
		eprint("Covit: Database not found in /data, creating new database at /data/%s" % database_name[0])
		conn = sqlite3.connect("data/%s" % database_name[0])
		cursor = conn.cursor()
		cursor.execute(("CREATE TABLE user_info ( username TEXT, password TEXT, extras TEXT);"))
	session.clear()
	session['username'] = None;
	session['tempusername'] = None;
	session['extras'] = None;
	session['signupfailures'] = [False, False, False, False];

# Managing Database
@app.before_request
def before_request():
	g.db = sqlite3.connect("data/%s" % database_name[0])

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# Routing
@app.route('/')
def homepage():
	users = g.db.execute("SELECT username FROM user_info").fetchall()
	eprint(session['username'], users);
	return render_template('homepage.html', username=session['username'])

@app.route('/signup')
def signup():
	eprint(session['signupfailures'])
	return render_template('signup.html',signupfailures=session['signupfailures'],pastUsername=session['tempusername'],pastExtras=session['extras'])

# Check that all of the fields were properly filled out, return to the page otherwise (with progress saved)
@app.route('/signupHandler', methods=['POST'])
def signupHandler():
	session['tempusername'] = request.form['username']
	session['password'] = request.form['password']
	session['extras'] = request.form['extras']
	# Invalid Username
	same = g.db.execute('SELECT * FROM user_info WHERE username = ?', [request.form['username']]).fetchall()
	session['signupfailures'][0] = (len(same) != 0);
	# Invalid Password
	session['signupfailures'][1] = len(session['password']) < 8;
	# Invalid Confirm
	session['signupfailures'][2] = not session['signupfailures'][1] and (session['password'] != request.form['password2']);
	# Invalid Extras
	session['signupfailures'][3] = False;
	if True in session['signupfailures']:
		return redirect('/signup')
	else:
		# Sucessful Account Creation
		session['username'] = request.form['username']
		g.db.execute("INSERT INTO user_info VALUES (?,?,?)", [session['username'], session['password'], session['extras']]);
		g.db.commit()
		return redirect('/')

@app.route('/signin')
def signin(failed=False):
	return render_template('signin.html',failed=failed)

# Check if password matches, if not, pass back entered username
@app.route('/signinHandler', methods=['POST'])
def signinHandler():
	username = g.db.execute('SELECT * FROM user_info WHERE username = ?', [request.form['username']]).fetchall()
	
	if len(username) == 0:
		return signin(failed=True);
	elif len(username) > 1:
		eprintf("Duplicate Users");
	else:
		if username[0][1] == request.form['password']:
			session['username'] = request.form['username'];
			return redirect('/')
		else:
			return signin(failed=True);

@app.route('/signout', methods=['POST'])
def signout():
	session['username'] = None;
	return redirect('/')

@app.route('/post')
def post():
    return redirect('/')

@app.route('/debug')
def debug():
    return redirect('/')

# Running
if __name__ == "__main__":
    app.run(port=33333)