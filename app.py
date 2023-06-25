from flask import Flask, render_template, session, redirect
from functools import wraps
import pymongo

app = Flask(__name__)
from user import routes


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')