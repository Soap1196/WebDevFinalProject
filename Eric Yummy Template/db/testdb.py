from flask import Flask, request, render_template, session, redirect
import pandas as pd
import numpy as np


menuitems = {'Item':['Cheese Sticks','Cheese Pizza','Spaghetti','Coca-Cola']}

df=pd.DataFrame(menuitems)
df