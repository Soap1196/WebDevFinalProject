from flask import Flask, request, render_template, session, redirect
import pandas as pd
import numpy as np

# menuitems = {'Item':['Cheese Sticks','Cheese Pizza','Spaghetti','Coca-Cola']}

# df=pd.DataFrame(menuitems)

testdb = Flask(__name__, template_folder='Eric Yummy Template')
@testdb.route('/')
def index():
    return render_template("menu.html")

if __name__ == '__main__':
    testdb.run(debug=True)
