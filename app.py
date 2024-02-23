from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key="super secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'toor'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_DB'] = 'students'
 
 
mysql = MySQL(app)

@app.route('/', methods=['GET','POST'])
def index():
    msg=''
    cur =mysql.connection.cursor()
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute('SELECT * FROM user WHERE username=%s AND password=%s', (username, password))
        record = cur.fetchone()
        if record:
            session['loggedin']= True
            session['username']= record[1]
            msg='success'
            print(msg)
            return redirect(url_for('home'))
        else:
            msg='Incorrect username/password.Try again'
            print(msg)           
    return render_template('index.html',msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    
    cur =mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    
    return render_template('home.html', students = data, username = session['username'])

@app.route('/insert', methods = ['POST'])
def insert():
    
    if request.method == "POST":       
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students ( name, email, phone) VALUES ( %s, %s, %s)", ( name, email, phone))
        mysql.connection.commit()
        return redirect(url_for('home'))
    
@app.route('/update', methods = ['POST', 'GET'])    
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE students
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
        
                    
        """, (name, email, phone, id_data))
        mysql.connection.commit()
        return redirect(url_for('home'))
        

@app.route('/register', methods=['GET','POST'])
def register():
    msg=''
    if request.method == "POST":       
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user ( username, password) VALUES ( %s, %s)", ( username, password))
        mysql.connection.commit()
        msg='success'
    return render_template('register.html')

@app.route('/admin')
def admin():
    
    cur =mysql.connection.cursor()
    cur.execute("SELECT * FROM user")
    data = cur.fetchall()
    cur.close()
    
    return render_template('admin.html', user = data)

@app.route('/userdelete/<string:userid>', methods = ['POST', 'GET'])
def userdelete(userid):
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user WHERE userid = %s", (userid))
    mysql.connection.commit()
    return redirect(url_for('admin'))

@app.route('/newstudent', methods=['GET','POST'])
def newstudent():
    
    
        if request.method == "POST":       
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
        
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO students ( name, email, phone) VALUES ( %s, %s, %s)", ( name, email, phone))
            mysql.connection.commit()
            return redirect(url_for('home'))
        return render_template('newstudent.html')

@app.route('/deletestudent/<string:id_data>', methods = ['POST', 'GET'])
def deletestudent(id_data):
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", [id_data])
    mysql.connection.commit()
    return redirect(url_for('home'))

if __name__ == "__main__": 
    app.run(debug=True)