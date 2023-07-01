from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from functools import wraps
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import pymongo
import os


app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

db_name = 'sample.db'
app.config['SECRET_KEY'] = "mysecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), nullable=False)
  password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})   
    password = PasswordField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"}) 
    
    submit = SubmitField("Register")
    
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})   
    password = PasswordField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"}) 
    
    submit = SubmitField("Login")

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    
    return render_template('home.html', form=form)


@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user
    return redirect(url_for('home'))

@app.route('/dashboard/' ,  methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('dashboard.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/Menu/')
def menu():
    
    return render_template('menu.html')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)