from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re

app = Flask(__name__)


#Old SQLlite Datebase
#app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///users.db'
#MySQL DB Connection
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://@localhost/users'
#Secret Key
app.secret_key=""
#Initalize The Database
db = SQLAlchemy(app)

#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(250))
    #date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
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

@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html')

# Update student database record
@app.route('/updatestudent', methods = ['POST', 'GET'])
def updatestudent():
    
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
        return render_template('updatestudent.html')

#Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a Form Class
class Namerform(FlaskForm):
    name = StringField("What is your Name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
#Create Password Form Class
class Passwordform(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create Name Page
@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = Namerform()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data     
        form.name.data = '' 
        flash("Form Submitted Successfully")  
        
    return render_template("name.html", 
                           name = name, 
                           form = form)
    
@app.route('/user/add', methods=['POST','GET'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.id)
    return render_template('add_user.html', 
                           form = form, 
                           name = name,
                           our_users=our_users)
    
#Update Database Record
@app.route('/update_user/<int:id>', methods=['GET','POST'])
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            try:
                db.session.commit()
                flash("User Updated Successfully")
                return render_template('update.html',
                                       form = form,
                                       name_to_update = name_to_update)
            except:
                flash("Error! Looks like there was a problem")
                return render_template('update.html',
                                       form = form,
                                       name_to_update = name_to_update,
                                       id=id)
    else:
        return render_template('update.html',
                                       form = form,
                                       name_to_update = name_to_update,
                                       id=id)
        
@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
        
        our_users = Users.query.order_by(Users.id)
        return render_template('add_user.html', 
                           form = form, 
                           name = name,
                           our_users=our_users,
                           id=id)
    except:     
        flash("Whoops! There was a problem deleting user, try again")
        return render_template('add_user.html', 
                           form = form, 
                           name = name,
                           our_users=our_users,
                           id = id)
                
#Create Test_PW Page
@app.route('/test_pw', methods=['GET','POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = Passwordform()
    
    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data  
        
        form.email.data = '' 
        form.password_hash.data = ''
        #flash("Form Submitted Successfully")
        pw_to_check = Users.query.filter_by(email=email).first()
        
        #Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)  
        
    return render_template("test_pw.html", 
                           email = email,
                           password = password, 
                           pw_to_check = pw_to_check,
                           passed = passed,
                           form = form)                

if __name__ == "__main__": 
    app.run(debug=True)
