from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_pymongo import PyMongo
import pymongo
import re

app = Flask(__name__, template_folder='template')


app.secret_key = 'Tahve bqltuyej tbrjereq qobfd MvIaTq cmanmvpcuxsz iesh tihkel CnTu dretpyauritompeanstd '

client = pymongo.MongoClient('mongodb+srv://root:admin@ict-hackathon.oksth.mongodb.net')
db = client.stagging
mongo = db['documents']

    

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'ict_hackathon'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('Homepage.html')

@app.route('/dash')
def dash():
    return render_template('dashboard.html')

@app.route('/ls')
def ls():
    return render_template('login.html')

@app.route('/login', methods=['get', 'post'])
def login():
    msg = ''
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT * FROM accounts WHERE username = %s AND passwd = %s', (username, password,))
    account = cursor.fetchone()

    if account:
        session['loggedin'] = True
        session['account_id'] = account['account_id']
        session['username'] = account['username']
        msg = 'Logged in successfully !'
        return render_template('index.html', msg=msg)
    else:
        msg = 'Incorrect username / password !'
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    returner = {}
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('id', None)
    session.pop('username', None)
    returner['status'] = "logout success"
    return returner

@app.route('/upload', methods=['POST'])
def upload():
        if 'inputfile' in request.files:
            file = request.files['inputfile']
            mongo.save_file(file.filename, file)
            mongo.db.documents.insert(
                {'username': '%s', 'document': file.filename}, session['username'])
            mongo.session.commit()
            return f'Uploaded: {file.filename}'
        return "done!"

@app.route('/works/<username>', methods=['POST'])
def retrive(username):
    if ['loggedin' == True]:
        user = mongo.db.user.find_one_or_404({'username' : username})
        return mongo.send_file('file', filename=user['document'])

@app.route('/polling', methods=['POST'])
def polling():
    msg = {}
    if ['loggedin' == True]:
        poll = request.form['poll']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if [session['utype'] == 'Vuser']:
            if [poll == 'Approval']:
                cursor.execute('INSERT INTO polling VALUES (NULL, %s, %s, %s, %s)',
                               (session['username'], session['utype'], '10', '',))
                mysql.connection.commit()
            elif [poll == 'Refusal']:
                cursor.execute('INSERT INTO polling VALUES (NULL, %s, %s, %s, %s)',
                               (session['username'], session['utype'], '', '10',))
                mysql.connection.commit()
        elif [session['utype'] != 'Vuser']:
            if [poll == 'Approval']:
                cursor.execute('INSERT INTO polling VALUES (NULL, %s, %s, %s, %s)',
                               (session['username'], session['utype'], '1', '',))
                mysql.connection.commit()
            elif [poll == 'Refusal']:
                cursor.execute('INSERT INTO polling VALUES (NULL, %s, %s, %s, %s)',
                               (session['username'], session['utype'], '', '1',))
                mysql.connection.commit()
        msg = 'You have casted your vote successfully!'
        return render_template("dashboard.html", msg=msg )

@app.route('/pollingresults', methods=['POST'])
def pollingresult():
    returner = {}
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select sum(Approval) from polling')
    app = cursor.fetchall()
    app = int(app)
    cursor.execute('select sum(Refusal) from polling')
    napp = cursor.fetchall()
    napp = int(napp)
    if (app > napp):
        returner['status'] = 'Document has got Approval!'
    elif (app <= napp):
        returner['status'] = "Document hasn't got Approval!"
    return returner

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password1' in request.form and 'email1' in request.form:
        username = request.form['username']
        password = request.form['password1']
        email = request.form['email1']
        utype = request.form['utype']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists'
        elif (utype == 'professor' or utype == 'Vuser'):
            if not re.match(r'[.edu]+', email):
                msg = 'Not a University/Verified email address'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)',
                        (username, password, email, utype))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    return render_template("login.html", msg=msg)


@app.route('/profile', methods=['POST'])
def profile():
    returner = {}
    if ['loggedin' == True]:
        fname = request.json.get('fname')
        print(fname)
        lname = request.json.get('lname')
        print(lname)
        phno = request.json.get('phno')
        print(phno)
        add1 = request.json.get('add1')
        print(add1)
        add2 = request.json.get('add2')
        print(add2)
        post = request.json.get('post')
        print(post)
        state = request.json.get('state')
        print(state)
        city = request.json.get('city')
        print(city)
        hdp = request.json.get('hdp')
        print(hdp)
        coun = request.json.get('coun')
        print(coun)
        reg = request.json.get('reg')
        print(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not re.match(r'[0-9]+', post):
            msg = 'Postal Code should contain only numbers'
        elif not re.match(r'[0-9]+', phno):
            msg = 'Mobile Number should contain only numbers'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (session['username'], fname, lname, phno, add1, add2, post, state, city, hdp, coun, reg))
            mysql.connection.commit()
            msg = 'You have successfully updated your profile!'


app.run(port=(8090))
