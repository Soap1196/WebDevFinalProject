from flask import Flask, render_template, session, request, url_for, redirect, session
from functools import wraps
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CustomerDB"]
mycol = mydb["CustomerCollection"]

post = {"_id": 0, "fullname": "john", "email": "test1@gmail.com", "password1": "password"}

mycol.insert_one(post)