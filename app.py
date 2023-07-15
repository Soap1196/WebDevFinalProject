from flask import Flask, render_template, session, request, url_for, redirect
import pymongo, json
import pandas as pd

app = Flask(__name__)
app.secret_key = "testing"

from user import routes

ManagementUserName = "M"
ManagementPassword = "P"

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
        email = session["email"]
        return render_template('logged_in.html', email=email,)
    else:
        return redirect(url_for("login"))
@app.route('/order', methods=["GET"])
def place_Order():
 if "email" in session:   
    total = []
    totalCart = []
    currentCart = []
    newCart = []
    
    for entry in customer_collection.find():
        total = entry.get('cart_total')
        if total:
            totalCart.append(total)
    for entry in customer_collection.find():
        currentCart = entry.get('cart')
        if currentCart:
            print(customer_collection)
            print(currentCart)
    
    return render_template('order.html', total=total, totalCart=totalCart)

@app.route("/login", methods=["POST", "GET"])
def login():
    message = ''
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = customer_collection.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
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

        if menu_collection.find_one({"food": UpdateFoodname}) == None:
            menu_collection.insert_one(
                {"food": UpdateFoodname, "supply": UpdateAmount, "price": UpdatePrice})

        if UpdateAmount != "":
            menu_collection.update_one({"food": UpdateFoodname}, {
                                       "$set": {"supply": UpdateAmount}})

        if UpdatePrice != "":
            menu_collection.update_one({"food": UpdateFoodname}, {
                                       "$set": {"price": UpdatePrice}})

        print(UpdateAmount)
        print(UpdatePrice)
        print(UpdateFoodname)

        fullmenu = menu_collection.find()
        df = pd.DataFrame(list(fullmenu))
        return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

    fullmenu = menu_collection.find()
    df = pd.DataFrame(list(fullmenu))
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

@app.route('/cart')
def cart():
    try:
        cuslst = customer_collection.find()
        dataItems = []
        for customer in cuslst:
            cart = customer.get('cart', [])
            dataItems.extend(cart)
        return render_template('cart.html', cart_data=dataItems)
    except Exception as e:
        print(f"Error retrieving cart data: {e}")

@app.route('/update', methods=['POST'])
def updateCart():
    try:
        requestJson = request.get_json()
        prodId = int(requestJson.get('prodId'))
        qty = requestJson.get('qty')
        
        if "email" in session:
            customer_collection.update_one(
                {'email': session["email"], 'cart._id': prodId},
                {'$set': {'cart.$.quantity': qty}}
            )
        else:
            print("email not in session")

        return qty

    except Exception as e:
        print(f"Error updating cart item: {e}")

@app.route('/getTotal', methods=['GET'])
def get_total():

    try:
        customer = customer_collection.find_one({'email': session["email"]})
        cart = customer.get('cart', [])

        cart_total = 0
        for item in cart:
            price = item.get('price', 0)
            qty = int(item.get('quantity', 0))
            cart_total += price * qty

        customer_collection.update_one(
            {'email': session['email']},
            {'$set': {'cart_total': cart_total}}
        )
        return str(cart_total)

    except Exception as e:
        print(f"Error calculating cart total: {e}")

@app.route('/delete', methods=['POST'])
def delete_cart_item():
    try:
        requestJson = request.get_json()
        prodId = int(requestJson.get('prodId'))

        customer_collection.update_one(
            {"email": session["email"]},
            {"$pull": {"cart": {"_id": prodId}}}
        )

        return redirect('/cart')

    except Exception as e:
        print(f"Error removing cart item: {e}")

# Add To Cart feature
# references:
# - https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
# - https://stackoverflow.com/questions/45412228/sending-json-and-status-code-with-a-flask-response
# - https://www.w3schools.com/python/python_mongodb_update.asp
# - https://www.mongodb.com/docs/manual/reference/operator/update/
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    # log request data
    requestJson = request.get_json()
    print(f"received /add-to-cart request with data: {requestJson}")

    # check user
    if "email" not in session or not session["email"]:
        message = "could not add to cart; user not logged in"
        return {"message": message}, 401  # unauthorized

    # check item
    itemJson = requestJson.get('item')
    if not itemJson:
        message = "Could not add to cart; item not sent"
        return {"message": message}, 400  # Bad request

    item = json.loads(itemJson)

    # Check if the item already exists in the cart
    existing_item = customer_collection.find_one(
        {'email': session['email'], 'cart.food': item['food']}
    )

    # the below condition will check the item in cart, it it exist it will increase the quantity otherwise it will add item in cart with quantity=1
    if existing_item:
        customer_collection.update_one(
            {'email': session['email'], 'cart.food': item['food']},
            {'$inc': {'cart.$.quantity': 1}}
        )
    else:
        item['quantity'] = 1
        customer_collection.update_one(
            {'email': session['email']},
            {'$push': {'cart': item}}
        )

    # increment user cart total
    customer_collection.update_one(
        {'email': session['email']},
        {'$inc': {'cart_total': item['price']}},
        upsert=False
    )

    print(f"added {item['food']} to cart for user {session['email']}")
    return {"message": "successfully added item to cart"}, 200


if __name__ == "__main__":
    app.run(debug=True)
