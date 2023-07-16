from flask import Flask, render_template, session, request, url_for, redirect
import pymongo, json
import pandas as pd

app = Flask(__name__)
app.secret_key = "testing"

from user import routes

ManagementUserName = "M"
ManagementPassword = "P"

cart = []

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["CustomerDB"]
customer_collection = mongo_db["CustomerCollection"]
menu_collection = mongo_db["MenuCollection"]

# for converting Python objects to JSON strings in HTML templates
# https://flask.palletsprojects.com/en/2.2.x/templating/#registering-filters
@app.template_filter('json_dumps')
def json_dumps(value):
    return json.dumps(value)

@app.route("/", methods=['POST', 'GET'])
def index():
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password1")
        user_input = {
            'name': user,
            'email': email,
            'password': password,
            'cart': [],
            'cart_total': 0
        }
        customer_collection.insert_one(user_input)
        session["email"] = email
        return render_template('logged_in.html', email=email)
    return render_template('index.html')

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        return render_template('logged_in.html', email=session["email"])
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    global cart
    cart = []
    message = ''
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = customer_collection.find_one({"email": email})
        if (password == ManagementPassword) and (email == ManagementUserName):
            return redirect(url_for('managementLogin'))
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
        if (password == ManagementPassword) and (email == ManagementUserName):
            return redirect(url_for('managementLogin'))
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/management", methods=["POST", "GET"])
def managementLogin():
    if request.method == "POST":
        UpdateFoodname = request.form.get("UpdateFoodName")
        UpdatePrice = request.form.get("UpdatePrice")
        UpdateAmount = request.form.get("UpdateAmount")

        if menu_collection.find_one({ "food" : UpdateFoodname}) == None:
            menu_collection.insert_one({ "food": UpdateFoodname, "supply": UpdateAmount, "price": UpdatePrice})

        if UpdateAmount != "":
            menu_collection.update_one({ "food": UpdateFoodname }, { "$set": { "supply": UpdateAmount } })

        if UpdatePrice != "":
            menu_collection.update_one({ "food": UpdateFoodname }, { "$set": { "price": UpdatePrice } })

        print(UpdateAmount)
        print(UpdatePrice)
        print(UpdateFoodname)

        fullmenu = menu_collection.find()
        df =  pd.DataFrame(list(fullmenu))
        return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

    fullmenu = menu_collection.find()
    df =  pd.DataFrame(list(fullmenu))
    return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route("/menu", methods=["GET"])
def foodmenu():
    
    fullmenu = []
    for x in menu_collection.find():
        fullmenu.append(x)

    email = ""
    if "email" in session:
        email = session["email"]

    return render_template('menu.html', fullmenu=fullmenu, email=email)

# Add To Cart feature
# references:
# - https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
# - https://stackoverflow.com/questions/45412228/sending-json-and-status-code-with-a-flask-response
# - https://www.w3schools.com/python/python_mongodb_update.asp
# - https://www.mongodb.com/docs/manual/reference/operator/update/
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    global cart
    # log request data
    requestJson = request.get_json()
    print(f"received /add-to-cart request with data: {requestJson}")

    # check user
    if "email" not in session or not session["email"]:
        message = "could not add to cart; user not logged in"
        return {"message": message}, 401 # unauthorized

    # check item
    itemJson = requestJson.get('item')
    if not itemJson:
        message = "could not add to cart; item not sent"
        return {"message": message}, 400 # bad request

    item = json.loads(itemJson)

    if menu_collection.find_one({ "food" : item['food']}):
        foodSupply = (menu_collection.find_one({ "food" : item['food']})['supply'])
        if foodSupply < 1:
            print("out of food")
            return {"message": "Out of food item"}, 200
        else:
            cart.append(foodSupply)
            print(cart)
            print("The food item is added")
            

    # add item to user cart
    customer_collection.update_one(
        {'email': session['email']},
        {'$push': {'cart': item}},
        upsert=False
    )

    # increment user cart total
    customer_collection.update_one(
        {'email': session['email']},
        {'$inc': {'cart_total': item['price']}},
        upsert=False
    )

        #cart.append([])
    print(f"added {item['food']} to cart for user {session['email']}")
    return {"message": "successfully added item to cart"}, 200

if __name__ == "__main__":
  app.run(debug=True)
