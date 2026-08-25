from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os


class Base(DeclarativeBase):
   def save(self):
      db.session.add(self)
      db.session.commit()

   def update(self):
      db.session.execute(self)
      db.session.commit()
       
load_dotenv('.env')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app, model_class=Base)






@app.route('/')
@app.route('/login')
def index():
   return render_template('login.html', title='Welcome back')

@app.route('/dashboard')
def dashboard():
   return render_template('dashboard.html', title='Dashboard')

@app.route('/forgot-password')
def forgot_password():
   pass

if __name__ == '__main__':
   app.run(debug=True)