from flask import Flask, render_template, session, request, url_for, redirect, session
from functools import wraps
import pymongo

app = Flask(__name__)
from user import routes


app = Flask(__name__)
app.secret_key = "testing"




myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CustomerDB"]
mycol = mydb["CustomerCollection"]

records = mycol



@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        
        
        user_input = {'name': user, 'email': email, 'password': password1}
        records.insert_one(user_input)
            
        user_data = records.find_one({"email": email})
        new_email = user_data['email']
   
        return render_template('logged_in.html', email=new_email)
    return render_template('index.html')

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))
    

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password1']
            #encode the password and check if it matches
            if (password == passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


if __name__ == "__main__":
  app.run(debug=True)