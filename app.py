from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List
import os

class Base(DeclarativeBase):
   def save(self):
      db.session.add(self)
      db.session.commit()
      return self

   @classmethod
   def retrieve_by_id(cls, id):
      return db.session.get(cls, id)

   @classmethod
   def retrieve_all(cls):
      return db.session.scalars(select(cls)).all() 

load_dotenv('.env')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app, model_class=Base)
csrf = CSRFProtect(app)

class Staff(db.Model):
   __tablename__ = 'staff'
   user_id: Mapped[int] = mapped_column(primary_key=True)
   fullname: Mapped[str] = mapped_column(nullable=False)
   email: Mapped[str] = mapped_column(unique=True, nullable=False)
   user_password: Mapped[str] = mapped_column(nullable=False)
   user_role: Mapped[str] = mapped_column(nullable=False)
   available: Mapped[bool] = mapped_column(nullable=False)
   jobs: Mapped[List['History']] = relationship(back_populates='panel_maintenance', cascade='all, delete-orphan')

class SolarFarm(db.Model):
   __tablename__ = 'solar_farm'
   farm_id: Mapped[int] = mapped_column(primary_key=True)
   name: Mapped[str] = mapped_column(unique=True,nullable=False)
   location: Mapped[str] = mapped_column(unique=True, nullable=False)
   solar_panel_models: Mapped[List['SolarArray']] = relationship(back_populates='farm', cascade='all, delete-orphan')

class SolarArray(db.Model):
   __tablename__ = 'solar_array'
   solar_array_id: Mapped[int] = mapped_column(primary_key=True)
   panel_model: Mapped[str] = mapped_column(nullable=False)
   total_panels: Mapped[int] = mapped_column(nullable=False)
   panel_kw_rating: Mapped[float] = mapped_column(nullable=False)
   status: Mapped[str] = mapped_column(nullable=False)
   farm_id: Mapped[int] = mapped_column(ForeignKey('solar_farm.farm_id'), nullable=False)
   farm: Mapped['SolarFarm'] = relationship(back_populates='solar_array')
   power_usage: Mapped[List['PowerUsage']] = relationship(back_populates='solar_array_power', cascade='all, delete-orphan')

class PowerUsage(db.Model):
   __tablename__ = 'power_usage_log'
   usage_id: Mapped[int] = mapped_column(primary_key=True)
   kw_generated: Mapped[float] = mapped_column(nullable=False)
   logged_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
   solar_array_id: Mapped[int] = mapped_column(ForeignKey('solar_array.solar_array_id'), nullable=False)
   solar_array_power: Mapped['SolarArray'] = relationship(back_populates='power_usage_log')

class History(db.Model):
   __tablename__ = 'history'
   history_id: Mapped[int] = mapped_column(primary_key=True)
   solar_array_id: Mapped[int] = mapped_column(nullable=False)
   repair_status: Mapped[str] = mapped_column(nullable=False)
   user_id: Mapped[int] = mapped_column(ForeignKey('staff.user_id'), nullable=False)
   panel_maintenance: Mapped['Staff'] = relationship(back_populates='history')







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