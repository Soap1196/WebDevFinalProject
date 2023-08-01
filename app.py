from flask import Flask, render_template, session, request, url_for, redirect
import pymongo, json
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = "testing"

from user import routes

ManagementUserName = "M"
ManagementPassword = "P"

cart = []
orderQ = []

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
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template('logged_in.html', email=session["email"])


@app.route("/login", methods=["POST", "GET"])
def login():
    global cart
    cart = []
    message = 'Welcome'
    if request.method == "POST":
        if (request.form.get("password") == ManagementPassword) and (request.form.get("email") == ManagementUserName):
            return redirect(url_for('managementLogin'))
        if customer_collection.find_one({"email": request.form.get("email")}):
            e_val = customer_collection.find_one({"email": request.form.get("email")})
            checkpassword = customer_collection.find_one({"email": request.form.get("email")})['password']
            if (request.form.get("password") == checkpassword):
                session["email"] = e_val['email']
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Password not in database'
                return render_template('login.html', message=message)
        if (request.form.get("password") == ManagementPassword) and (request.form.get("email") == ManagementUserName):
            return redirect(url_for('managementLogin'))
        else:
            message = 'Email not in database'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/cart", methods=["POST", "GET"])
def displayCart():
    global cart
    total = 0
    # commenting because total of cart is hendled through the items in cart at line 92
    # for i in cart:
    #     total = total + i['price']

    # this method will sync the cart variable and cart data om database
    refreshCart()
    

    for item in cart:
        price = item.get('price', 0)
        qty = int(item.get('quantity', 0))
        total += price * qty
    if request.method == "POST":
        # changed the condition because Quantity is added for ease
        # for i in cart:
        #     menu_collection.update_one(i, { "$set": { "supply": (int(i['supply']) - 1) } })
        for item in cart:
            filter_query = {'_id': item['_id']}
            new_supply = int(item['supply']) - int(item['quantity'])
            update_query = {"$set": {"supply": new_supply}}
            menu_collection.update_one(filter_query, update_query)

        global orderQ
        orderQ.append([cart,total])
        cart = []
        total = 0
        print('post')
        # empty the cart data when click on submit
        emptyCart()
        return render_template('cart.html', Totalcart = cart, total = total, cart_data =cart)
    print(cart)
   
    return render_template('cart.html', Totalcart = cart, total = total, cart_data =cart)

@app.route("/management", methods=["POST", "GET"])
def managementLogin():
    global orderQ
    if request.method == "POST":
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["CustomerDB"]
        myfood = mydb["MenuCollection"]
        Radio = request.form.get("Radio")
        UpdateFoodname = request.form.get("UpdateFoodName")
        UpdateType = request.form.get("UpdateType")
        UpdatePrice = request.form.get("UpdatePrice")
        UpdateAmount = request.form.get("UpdateAmount")
        DeleteItem = request.form.get("DeleteItem")
        print("||||")
        print(Radio)

        # fresh connection to database
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["CustomerDB"]
        myfood = mydb["MenuCollection"]

        fullmenu = myfood.find()
        df =  pd.DataFrame(list(fullmenu))
        
        if (Radio =="Delete") and (myfood.find_one({"food" : UpdateFoodname})!= None):
            myfood.delete_one({ "food": UpdateFoodname})
            fullmenu = myfood.find()
            df =  pd.DataFrame(list(fullmenu))
            return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values, orderQ = orderQ)
        if Radio == "Add":
            # updating the limit because it is going out of integer limit and we never gonna have more than 999 types of food items.
            myfood.insert_one({ "_id":random.randint(0,999), "food": UpdateFoodname, "type": UpdateType, "supply": int(UpdateAmount), "price": int(UpdatePrice)})
            fullmenu = myfood.find()
            df =  pd.DataFrame(list(fullmenu))
            return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values, orderQ = orderQ)
        if Radio == "Modify":
            if UpdateAmount != "":
                myfood.update_one({ "food": UpdateFoodname }, { "$set": { "supply": int(UpdateAmount) } })
            
            if UpdatePrice != "":
                myfood.update_one({ "food": UpdateFoodname }, { "$set": { "price": int(UpdatePrice) } }) 

            if UpdateType != "":
                myfood.update_one({ "food": UpdateFoodname }, { "$set": { "type": UpdateType } })   

            fullmenu = myfood.find()
            df =  pd.DataFrame(list(fullmenu))
        return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values, orderQ = orderQ)

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["CustomerDB"]
    myfood = mydb["MenuCollection"]

    fullmenu = myfood.find()
    df =  pd.DataFrame(list(fullmenu))
    #df.insert(loc = 5,column = 'Delete',value = '<input type="checkbox" \>')
    #df.style
    return render_template('management.html',  tables=[df.to_html(classes='data')], titles=df.columns.values, orderQ = orderQ)


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

    # Check if the item already exists in the cart
    existing_item = customer_collection.find_one(
        {'email': session['email'], 'cart.food': item['food']}
    )

    if menu_collection.find_one({ "food" : item['food']}):
        foodSupply = (menu_collection.find_one({ "food" : item['food']})['supply'])
        if int(foodSupply) < 1:
            print("out of food")
            return {"message": "Out of food item"}, 200
        else:
            # adding this quantity to check whether the product is in cart or no. ifit exist in cart then increment the quantity else add product in cart.
            if existing_item:
                cart_item = next((item for item in existing_item['cart'] if item['food'] == item['food']), None)
                if cart_item:
                    quantity = cart_item['quantity']
                    item['quantity'] = quantity +1
                else:
                    item['quantity'] = 1

                customer_collection.update_one(
                    {'email': session['email'], 'cart.food': item['food']},
                    {'$inc': {'cart.$.quantity': 1}}
                )                
            else:
                item['quantity'] = 1
                customer_collection.update_one(
                    {'email': session['email']},
                    {'$push': {'cart': item}},
                    upsert=False
                )   
            #  commenting the below line because the cart is handled through refreshCart() at line 270
            # cart.append(menu_collection.find_one({ "food" : item['food']}))
            print(cart)
            print("The food item is added")
            

    # add item to user cart
    # customer_collection.update_one(
    #     {'email': session['email']},
    #     {'$push': {'cart': item}},
    #     upsert=False
    # )

    # increment user cart total
    customer_collection.update_one(
        {'email': session['email']},
        {'$inc': {'cart_total': item['price']}},
        upsert=False
    )

    #cart.append([])
    refreshCart()
    print(f"added {item['food']} to cart for user {session['email']}")
    return {"message": "successfully added item to cart"}, 200

# this method will update the quatity of product updated by user through the cart page
# it will take prodid = item id and qty= quantity of item
@app.route('/update', methods=['POST'])
def updateCart():
    global cart
    msg =""
    try:
        requestJson = request.get_json()
        prodId = int(requestJson.get('prodId'))
        qty = requestJson.get('qty')
        
        if "email" in session:
            # this code will check whether the quantity is under supply or not and update the supply in inventory .
            itemInMenu = menu_collection.find_one({ '_id' : prodId})
            if int(itemInMenu['supply']) < int(qty):
                print("can not add this quantity")
                
                msg ="Requested quantity is not available in storage "
            else:
                customer_collection.update_one(
                    {'email': session["email"], 'cart._id': prodId},
                    {'$set': {'cart.$.quantity': qty}}
                )
                msg ="Quantity updated successfully "
        else:
            print("email not in session")
            msg ="email not in session"

        refreshCart()

    except Exception as e:
        print(f"Error updating cart item: {e}")
    
    return msg

# this method will return the total price of cart
@app.route('/getTotal', methods=['GET'])
def get_total():
    global cart
    cart_total = 0
    try:
        for item in cart:
            price = item.get('price', 0)
            qty = int(item.get('quantity', 0))
            cart_total += price * qty

        # customer_collection.update_one(
        #     {'email': session['email']},
        #     {'$set': {'cart_total': cart_total}}
        # )
        return str(cart_total)

    except Exception as e:
        print(f"Error calculating cart total: {e}")

# this method will delete the item from cart and database
# it takes prodId = item id
@app.route('/delete', methods=['POST'])
def delete_cart_item():
    try:
        requestJson = request.get_json()
        prodId = int(requestJson.get('prodId'))

        customer_collection.update_one(
            {"email": session["email"]},
            {"$pull": {"cart": {"_id": prodId}}}
        )
        refreshCart()
        return redirect('/cart')

    except Exception as e:
        print(f"Error removing cart item: {e}")

# this method will sync the cart global variable and cart in database
def refreshCart():
    global cart
    cart=[]
    try:
        cart_data = customer_collection.find_one(
            {'email': session['email']}
        )
        if cart_data:
            cart = cart_data['cart']
        else:
            # If the customer's cart is not found in the database, initialize it as an empty list
            cart = []
    except Exception as e:
        print(f"Error removing cart item: {e}")

# this method will empty the cart of user when submit button clicked from cart page clicked
def emptyCart():
    try:
        customer_collection.update_one(
            {'email': session["email"]},
            {'$set': {'cart': []}}
        )

    except Exception as e:
        print(f"Error removing cart item: {e}")
if __name__ == "__main__":
  app.run(debug=True)
