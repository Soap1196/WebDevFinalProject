from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_login import UserMixin
app = Flask(__name__)

db = SQLAlchemy(app)

# class User(db.Model, UserMixin):

#   _id = db.Column("id", db.Integer, primary_key=True)
#   name: db.Column("name" , db.String(100), nullable=False)
#   password: db.Column("password", db.String(100), nullable=False)
  
#   def __init__(self, name, password):
#     self.name = name
#     self.password = password

  # def signup(self):



    # user = {
    #   "_id": "",
    #   "name": request.form.get('name'),
    #   "password": request.form.get('password')
    # }

    # return jsonify(user), 200
