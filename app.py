from flask import Flask, render_template, session, request, url_for, redirect, session
from functools import wraps
import pymongo
import pandas as pd

app = Flask(__name__)
from user import routes


app = Flask(__name__)
app.secret_key = "testing"


ManagmentUserName = "M"
ManagementPassword = "P"

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
        return render_template('logged_in.html', email=email,)
    else:
        return redirect(url_for("login"))
    

@app.route("/login", methods=["POST", "GET"])
def login():
    message = ''

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password1']
            if (password == passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        if (password == ManagementPassword) and (email == ManagmentUserName):
            return redirect(url_for('managementLogin'))
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/Managment", methods=("POST", "GET"))
def managementLogin():

    if request.method == "POST":
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["CustomerDB"]
        myfood = mydb["MenuCollection"]
        UpdateFoodname = request.form.get("UpdateFoodName")
        UpdatePrice = request.form.get("UpdatePrice")
        UpdateAmount = request.form.get("UpdateAmount")
        if UpdateAmount != "":
            myfood.update_one({ "food": UpdateFoodname }, { "$set": { "supply": UpdateAmount } })
        
        if UpdatePrice != "":
            myfood.update_one({ "food": UpdateFoodname }, { "$set": { "price": UpdatePrice } })
        
        print(UpdateAmount)
        print(UpdateFoodname)
        # fresh connection to database
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["CustomerDB"]
        myfood = mydb["MenuCollection"]

        fullmenu = myfood.find()
        df =  pd.DataFrame(list(fullmenu))
        return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["CustomerDB"]
    myfood = mydb["MenuCollection"]

    fullmenu = myfood.find()
    df =  pd.DataFrame(list(fullmenu))
    return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)


if __name__ == "__main__":
  app.run(debug=True)