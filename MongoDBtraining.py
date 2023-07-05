from flask import Flask, render_template, session, request, url_for, redirect, session
from functools import wraps
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CustomerDB"]
cuscol = mydb["CustomerCollection"]
mycol = mydb["MenuCollection"]

post = {"_id": 0, "food": "cheese pizza", "type": "pizza", "price": 20.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 1, "food": "pepperoni pizza", "type": "pizza", "price": 20.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 2, "food": "supreme pizza", "type": "pizza", "price": 20.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 3, "food": "chicken alfredo", "type": "pasta", "price": 15.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 4, "food": "spaghetti", "type": "pasta", "price": 15.00,"supply": 15}
mycol.insert_one(post)
post = {"_id": 5, "food": "macaroni", "type": "pasta", "price": 15.00,"supply": 15}
mycol.insert_one(post)
post = {"_id": 6, "food": "pepsi", "type": "drink", "price": 3.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 7, "food": "coke", "type": "drink", "price": 3.00, "supply": 15}
mycol.insert_one(post)
post = {"_id": 8, "food": "water", "type": "drink", "price": 3.00, "supply": 15}
mycol.insert_one(post)