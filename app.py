from flask import Flask, render_template, redirect, url_for, request, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import sys, time, datetime, random, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

db_conn = sqlite3.connect('FinalDatabase.db', check_same_thread=False)

print("Database Created")

theCursor = db_conn.cursor()

login_manager = LoginManager()
login_manager.init_app(app)

db_conn.execute("DROP TABLE IF EXISTS Admin")
db_conn.execute("DROP TABLE IF EXISTS User")
db_conn.execute("DROP TABLE IF EXISTS Course")
db_conn.execute("DROP TABLE IF EXISTS Enrolled")
db_conn.commit()

db_conn.execute("""CREATE TABLE Admin(adminid INTEGER PRIMARY KEY AUTOINCREMENT, 
                username STRING(50) NOT NULL,  password STRING(50) NOT NULL);""")

db_conn.execute("""CREATE TABLE User(id INTEGER PRIMARY KEY AUTOINCREMENT, usertype STRING(20) NOT NULL,
                username VARCHAR(50) NOT NULL UNIQUE,  email VARCHAR(50) NOT NULL UNIQUE, 
                password VARCHAR(50) NOT NULL, firstname NOT NULL, lastname NOT NULL, 
                middlename NOT NULL, sex STRING(10) NOT NULL, birthdate TEXT NOT NULL, 
                studentId INT(10) NOT NULL UNIQUE, college STRING(30) NOT NULL, course STRING(10) NOT NULL,
                address STRING(50) NOT NULL);""")

db_conn.execute("""CREATE TABLE Course(courseid INTEGER PRIMARY KEY AUTOINCREMENT,
                coursename STRING(50) UNIQUE NOT NULL);""")

db_conn.execute("""CREATE TABLE Enrolled(enrollmentid INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,  course_id INTEGER, FOREIGN KEY(user_id) REFERENCES User(id),   
                   FOREIGN KEY(course_id) REFERENCES Course(courseid) );""")

print('Table Created')
db_conn.commit()





@login_manager.user_loader
def load_user(user_id):
    searcher = theCursor.execute('SELECT id FROM Users WHERE id =?', user_id)
    return searcher

@app.route('/', methods=['POST', 'GET'])
def main():
    num = 1
    check = theCursor.execute("SELECT * FROM Admin WHERE adminid=?", (num,))
    user = theCursor.execute("SELECT * FROM User WHERE username=?", ('admin',)).fetchone()
    if check is None or user is None:
        db_conn.execute('INSERT INTO Admin(username, password) VALUES (?,?);', ['admin', 'adminpass']);
        db_conn.execute('INSERT INTO User(usertype, username, email, password, firstname, lastname, middlename, \
                        sex, birthdate, studentId, college, course, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', \
                        ['admin', 'admin', 'admin@gmail.com', 'adminpass', 'admin', 'admin', 'admin', 'Male', 'admin', 'admin', \
                         'admin', 'admin', 'admin']);

        db_conn.commit()
    return render_template('index.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        if request.form['username'] == 'admin':
            user = theCursor.execute("SELECT * FROM User WHERE username=?", ('admin',)).fetchone()
            username = theCursor.execute("SELECT username FROM User WHERE username=?", ('admin',)).fetchone()
            if user is not None:
                session['user'] = request.form['username']
                g.user = session['user']
                return redirect(url_for('.admindashboard', user=username))
            else:
                return redirect('/login')
        else:
            username = request.form['username']
            password = request.form['password']
            user = theCursor.execute("SELECT * FROM User WHERE username=? AND password=?", (username,password)).fetchone()
            username = theCursor.execute("SELECT username FROM User WHERE username=?", (username,)).fetchone()
            if user is not None:
                session['user'] = request.form['username']
                return redirect(url_for('.userdashboard', user=username[0]))
            else:
                return redirect('/login')
    return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if g.user:
        session.pop('user', None)
        return redirect('/')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if request.form['password'] == request.form['password2']:
            db_conn.execute('INSERT INTO User(usertype, username, email, password, firstname, lastname, middlename, \
                            sex, birthdate, studentId, college, course, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', \
                            ['user', request.form['username'], request.form['email'], request.form['password'], request.form['firstname'], request.form['lastname'], \
                             request.form['middlename'], request.form.get('sex'), (request.form['birthdate']), request.form['studentId'], \
                             request.form.get('college'), request.form['course'], request.form['address']]);
            db_conn.commit()
            user = theCursor.execute("SELECT * FROM User WHERE username=?  AND password=?", (request.form['username'],request.form['password'],)).fetchone()
            session['user'] = request.form['username']
            g.user = session['user']
            return redirect(url_for('.userdashboard', user=user[2]))
        else:
            return redirect(url_for('signup'))
    else:
        return render_template('signup.html')

@app.route('/<user>', methods=['POST', 'GET'])
def userdashboard(user):
    if g.user:
        return render_template('userdashboard.html', user = user)

@app.route('/<user>/profile', methods=['POST', 'GET'])
def profile(user):
    if g.user:
        thisuser = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                            address, studentId, college, course, id FROM User WHERE username=?", (user,)).fetchone()

        return render_template('profile.html', user=user, mainuser=thisuser)

@app.route('/<user>/profile/edit', methods=['POST', 'GET'])
def editinfo(user):
    if g.user:
        if request.method == 'POST':
            userid = theCursor.execute("SELECT id FROM User WHERE username=?", (user,)).fetchone()
            db_conn.execute('UPDATE User SET username = ? WHERE id = ?', (request.form['username'], userid[0]))
            db_conn.execute('UPDATE User SET email = ? WHERE id = ?', (request.form['email'], userid[0]))
            db_conn.execute('UPDATE User SET firstname = ? WHERE id = ?', (request.form['firstname'], userid[0]))
            db_conn.execute('UPDATE User SET lastname = ? WHERE id = ?', (request.form['lastname'], userid[0]))
            db_conn.execute('UPDATE User SET middlename = ? WHERE id = ?', (request.form['middlename'], userid[0]))
            db_conn.execute('UPDATE User SET birthdate = ? WHERE id = ?', (request.form['birthdate'], userid[0]))
            db_conn.execute('UPDATE User SET studentId = ? WHERE id = ?', (request.form['studentId'], userid[0]))
            db_conn.execute('UPDATE User SET college = ? WHERE id = ?', (request.form['college'], userid[0]))
            db_conn.execute('UPDATE User SET course = ? WHERE id = ?', (request.form['course'], userid[0]))
            db_conn.execute('UPDATE User SET address = ? WHERE id = ?', (request.form['address'], userid[0]))
            db_conn.commit()
            thisuser = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                address, studentId, college, course, id FROM User WHERE username=?",(request.form['username'],)).fetchone()
            usernew = theCursor.execute("SELECT username FROM User WHERE username=?", (request.form['username'],)).fetchone()

            return redirect(url_for('profile', user=usernew[0], mainuser=thisuser))
        else:
            thisuser = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                                            address, studentId, college, course, id FROM User WHERE username=?",
                                         (user,)).fetchone()
            return render_template('editInfo.html', user=user, mainuser=thisuser)


@app.route('/<user>/userlist', methods=['POST', 'GET'])
def userlist(user):
    if g.user:
        users = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                    address, studentId, college, course, id FROM User WHERE usertype=?",
                                  ('user',)).fetchall()
        return render_template('userlist.html', users=users, user=user)

@app.route('/<user>/courses')
def enrolledCourses(user):
    if g.user:
        usercourses = ()
        thisuser = theCursor.execute("SELECT id FROM User where username=?", (user,)).fetchone()
        courses = theCursor.execute("SELECT course_id FROM Enrolled where user_id=?", (thisuser[0],)).fetchall()
        for course in courses:
           course1 = theCursor.execute("SELECT coursename FROM Course where courseid=?", (course[0],)).fetchone()
           usercourses = usercourses + (course1,)

        courses1 = theCursor.execute("SELECT * FROM Course").fetchall()
        return render_template('usercourses.html', user=user, courses=usercourses, coursesoption=courses1)

@app.route('/<user>/courses/addcourse', methods=['POST'])
def userAddcourse(user):
    if g.user:
        if request.method == 'POST':
            usercourses = ()
            thisuser = theCursor.execute("SELECT id FROM User where username=?", (user,)).fetchone()
            coursefind = theCursor.execute("SELECT courseid FROM Course where coursename=?", (request.form.get('coursename1'),)).fetchone()
            coursefind2 = theCursor.execute("SELECT coursename FROM Course where coursename=?", (request.form.get('coursename1'),)).fetchone()
            verifycourse = theCursor.execute("SELECT course_id FROM Enrolled where user_id=? AND course_id=?",(thisuser[0],coursefind[0])).fetchone()
            if verifycourse is None:
                courses = theCursor.execute("SELECT user_id FROM Enrolled where user_id=?",(thisuser[0],)).fetchall()
            else:
                return redirect(url_for('enrolledCourses', user=user))
            for course in courses:
                course1 = theCursor.execute("SELECT coursename FROM Course where courseid=?", (course[0],)).fetchone()
                usercourses = usercourses + (course1,)

            print(usercourses)
            for i in usercourses:
                if i[0] is theCursor.execute("SELECT coursename FROM Course where coursename=?", (request.form.get('coursename1'),)).fetchone():
                    return redirect(url_for('enrolledCourses', user=user))

            db_conn.execute('INSERT INTO Enrolled(course_id, user_id) VALUES (?,?);', [coursefind[0], thisuser[0]]);
            db_conn.commit()
            return redirect(url_for('enrolledCourses', user=user))

@app.route('/<user>/courses/removecourse/<coursename>', methods=['POST', 'GET'])
def userRemovecourse(user, coursename):
    if g.user:
        if request.method == 'POST':
            thisuser = theCursor.execute("SELECT id FROM User where username=?", (user,)).fetchone()
            course = theCursor.execute("SELECT * FROM Course where coursename=?",(coursename,)).fetchone()
            db_conn.execute("DELETE FROM Enrolled WHERE course_id=? AND user_id=?", (course[0], thisuser[0]))
            db_conn.commit()
            return redirect(url_for('enrolledCourses', user=user))


@app.route('/admin')
def admindashboard():
    if g.user:
        return render_template('admindashboard.html')

@app.route('/admin/manageusers', methods=['POST', 'GET'])
def manageUsers():
    if g.user:
        users = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                            address, studentId, college, course, id FROM User WHERE usertype=?", ('user',)).fetchall()
        return render_template('adminuserlist.html', users=users)

@app.route('/admin/manageusers/adduser', methods=['POST','GET'])
def addUser():
    if g.user:
        if request.method == 'POST':
            if request.form['password'] == request.form['password2']:
                db_conn.execute('INSERT INTO User(usertype, username, email, password, firstname, lastname, middlename, \
                                sex, birthdate, studentId, college, course, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', \
                                ['user', request.form['username'], request.form['email'], request.form['password'],
                                 request.form['firstname'], request.form['lastname'], \
                                 request.form['middlename'], request.form.get('sex'), request.form['birthdate'],
                                 request.form['studentId'], \
                                 request.form.get('college'), request.form['course'], request.form['address']]);
                db_conn.commit()
                users = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                                                    address, studentId, college, course, id FROM User WHERE usertype=?",
                                          ('user',)).fetchall()
                return redirect(url_for('manageUsers', users=users))
            else:
                users = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                                    address, studentId, college, course, id FROM User WHERE usertype=?",
                                          ('user',)).fetchall()
                return redirect(url_for('manageUsers', users=users))
        else:
            return render_template('adminadduser.html')

@app.route('/admin/manageusers/deleteuser/<id>', methods=['POST', 'GET'])
def deleteUser(id):
    if g.user:
        if request.method == 'POST':
            db_conn.execute("DELETE FROM User WHERE id=?", (id,)).fetchone()
            db_conn.commit()
            users = theCursor.execute("SELECT username, email, firstname, middlename, lastname, sex, birthdate, \
                                    address, studentId, college, course, id FROM User WHERE usertype=?", ('user',)).fetchall()
            return redirect(url_for('manageUsers', users=users))

@app.route('/admin/managecourses')
def managecourses():
    if g.user:
        courses = theCursor.execute("SELECT * FROM Course").fetchall()
        return render_template('admincourses.html', courses=courses)

@app.route('/admin/managecourses/addcourse', methods=['POST', 'GET'])
def addcourse():
    if g.user:
        if request.method == 'POST':
            db_conn.execute("INSERT INTO Course(coursename) VALUES (?);", [request.form['coursename']])
            db_conn.commit()
            return redirect(url_for('managecourses'))
        else:
            return redirect(url_for('managecourses'))


@app.route('/admin/managecourses/removecourse/<coursename>', methods=['POST', 'GET'])
def removecourse(coursename):
    if g.user:
        if request.method == 'POST':
            db_conn.execute("DELETE FROM Course WHERE coursename=?", (coursename,)).fetchone()
            db_conn.commit()
            return redirect(url_for('managecourses'))

@app.route('/admin/managecourses/editcourse/<coursename>', methods=['POST', 'GET'])
def editcourse(coursename):
    if g.user:
        if request.method == 'POST':
            db_conn.execute('UPDATE Course SET coursename = ? WHERE coursename = ?', (request.form['coursename'], coursename))
            db_conn.commit()
            return redirect(url_for('managecourses'))
        else:
            course = theCursor.execute("SELECT coursename FROM Course WHERE coursename=?", (coursename,)).fetchone()
            return render_template('admineditcourse.html', course=course)

if __name__ == '__main__':
    app.run(debug=True)