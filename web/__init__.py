from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
# from . import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)
