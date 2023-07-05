from flask import Flask
from flask import jsonify
from flask import request

class User:

  def signup(self):

    user = {
      "_id": "",
      "name": request.form.get('name'),
      "password": request.form.get('password')
    }

    return jsonify(user), 200
