from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.secret_key = "prathmesh"
db = SQLAlchemy(app)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
from . import models

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return models.Admin.query.get(user_id)
# Session(app)
