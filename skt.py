from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, random, string
import mysql.connector
from flask_socketio import SocketIO
from time import sleep
from threading import Thread
#Get the IP4 address of the connnected network
import socket
h_name = socket.gethostname()
IP_addres = socket.gethostbyname(h_name)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='http://'+IP_addres+':4000')

app.config["SECRET_KEY"] = os.urandom(16)  # Set a secret key for security
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True  # Require HTTPS for the session cookie
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent client-side JavaScript access to the session cookie

mydb = mysql.connector.connect(host = 'localhost',
                               user = 'root',
                               password = 'Clashofclan1534')
mycursor = mydb.cursor()
mycursor.execute('USE keshu$userprofile;')
sessions = {}
# A dictionary to store user credentials (username: password)
user_credentials = {}

def generate_random_string(length = 4): #Call function to add code in database during signup.
    exist = True
    val = ""
    while exist:
        alphabet = string.ascii_letters
        for n in range(2):
            val += (''.join(random.choice(alphabet) for i in range(length))+ "-"+ str(random.randint(1001, 9999))).upper()
            if n==0:val+="-"
        mycursor.execute("SELECT room FROM user WHERE room = %s;", [val])        #change table/column or create new table to store
        data = mycursor.fetchone()
        if data:
            pass
        else:
            #exist = False
            return val


def login(email, password, typ=True):
    #mycursor.execute('Use keshu$userprofile;')
    mycursor.execute(f'SELECT * from user where email =%s;', [email] )
    data = mycursor.fetchone()
    if not typ and data:
        return True
    if data is None or not typ:
        return False
    user_credentials = {data[0] : data[2]}
    data = None
    if email in user_credentials and user_credentials[email] == password:
        return True
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    if "email" in sessions:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if login(email, password):
            sessions["email"] = email
            return redirect('/dashboard')
        else:
            return render_template("login.html", message = 'Invalid User or password', email=email, password=password)

    return render_template("login.html")

@app.route('/CheckUsername', methods=['POST'])
def Check_Username():
    email:str = request.json['email']
    #mycursor.execute('Use keshu$userprofile;')
    mycursor.execute(f'SELECT email from user where email =%s;', [email])
    data = mycursor.fetchall()
    for tpl in data:
        if tpl[0]==email:
            return jsonify({'exists': True})
    return jsonify({'exists': False})

@app.route('/Signup')
def Signup():
    return render_template('signup.html')

@app.route('/SignupData', methods=['POST'])
def SignupData():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        if not login(email=email, password=password, typ=False):
            room = generate_random_string()
            #mycursor.execute('USE userconfig;')
            mycursor.execute("INSERT INTO user values( %s, %s, %s, %s);", [email, username, password, room])
            mydb.commit()
            if login(email, password):
                sessions["email"] = email
                return redirect(url_for("dashboard"))
        else:
            return render_template('signup.html', email=email, username=username, message="Email already exist.")

@app.route("/dashboard")
def dashboard():
    if "email" in sessions:
        mycursor.execute(f'SELECT username, room from user where email =%s;', [sessions['email']] )
        data = mycursor.fetchone()
        return render_template("newHomepage.html", email=sessions['email'], username=data[0], room = data[1])
    return redirect(url_for("index"))

@app.route("/logout", methods=['POST'])
def logout():
    sessions.clear()
    return redirect(url_for("index"))
    

if __name__ == "__main__":
    while True:
        if IP_addres != "127.0.0.0":
            app.run(host=IP_addres, port=5000, debug=True)
            print("Running")
        else:
            print("waiting")
            sleep(5)