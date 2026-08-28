from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, joinedload, selectinload
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema 
from dotenv import load_dotenv
from datetime import datetime, timezone, date
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
      return db.session.scalars(cls).all() 

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
   solar_panels: Mapped[List['SolarArray']] = relationship(back_populates='farm', cascade='all, delete-orphan')

class SolarArray(db.Model):
   __tablename__ = 'solar_array'
   solar_array_id: Mapped[int] = mapped_column(primary_key=True)
   panel_model: Mapped[str] = mapped_column(nullable=False)
   total_panels: Mapped[int] = mapped_column(nullable=False)
   panel_kw_rating: Mapped[float] = mapped_column(nullable=False)
   status: Mapped[str] = mapped_column(nullable=False)
   farm_id: Mapped[int] = mapped_column(ForeignKey('solar_farm.farm_id'), nullable=False)
   farm: Mapped['SolarFarm'] = relationship(back_populates='solar_panels')
   power_log: Mapped[List['PowerLog']] = relationship(back_populates='solar_array_power', cascade='all, delete-orphan')

class PowerLog(db.Model):
   __tablename__ = 'power_log'
   usage_id: Mapped[int] = mapped_column(primary_key=True)
   kw_generated: Mapped[float] = mapped_column(nullable=False)
   logged_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
   solar_array_id: Mapped[int] = mapped_column(ForeignKey('solar_array.solar_array_id'), nullable=False)
   solar_array_power: Mapped['SolarArray'] = relationship(back_populates='power_log')

class History(db.Model):
   __tablename__ = 'history'
   history_id: Mapped[int] = mapped_column(primary_key=True)
   solar_array_id: Mapped[int] = mapped_column(nullable=False)
   repair_status: Mapped[str] = mapped_column(nullable=False)
   user_id: Mapped[int] = mapped_column(ForeignKey('staff.user_id'), nullable=False)
   panel_maintenance: Mapped['Staff'] = relationship(back_populates='jobs')


class PowerLogSchema(SQLAlchemyAutoSchema):
   class Meta:
      model = PowerLog
      load_instance = True

class SolarArraySchema(SQLAlchemyAutoSchema):
   class Meta:
      model = SolarArray
      load_instance = True
   power_log = fields.Nested(PowerLogSchema, many=True)

class SolarFarmSchema(SQLAlchemyAutoSchema):
   class Meta:
      model = SolarFarm
      load_instance = True
   solar_panels = fields.Nested(SolarArraySchema, many=True)

class HistorySchema(SQLAlchemyAutoSchema):
   class Meta:
      model = History
      sql_asession = db.session
      load_instance = True

class StaffSchema(SQLAlchemyAutoSchema):
   class Meta:
      model = Staff
      sql_session = db.session
      load_instance = True
   jobs = fields.Nested(HistorySchema, many=True)

class PowerLogResults:
   #get the current, high and low kW generated for the day
   def kW_calculator(self, daily_kW_measurement, sa_id):
      if daily_kW_measurement == 'CURRENT':
          stmt = self._current_kW(sa_id)
      elif daily_kW_measurement == 'HIGH':
          stmt = self._daily_kW_high(sa_id)
      elif daily_kW_measurement == 'LOW':
          stmt = self._daily_kW_low(sa_id)
      elif daily_kW_measurement == 'kWh':
          stmt = self._daily_kWh(sa_id)
      return db.session.scalar(stmt) or 0.0

   @classmethod
   def _current_kW(cls, sa_id):
      return select(PowerLog.kw_generated)\
             .where(PowerLog.solar_array_id == sa_id)\
             .order_by(PowerLog.logged_at.desc())\
             .limit(1)
         
   @classmethod
   def _daily_kW_high(cls, sa_id):
      return select(func.max(PowerLog.kw_generated))\
            .where(PowerLog.solar_array_id == sa_id)\
            .where(func.date(PowerLog.logged_at) == date.today())
             
   @classmethod
   def _daily_kW_low(cls, sa_id):
      return select(func.min(PowerLog.kw_generated))\
            .where(PowerLog.solar_array_id == sa_id)\
            .where(func.date(PowerLog.logged_at) == date.today())

   @classmethod
   def _daily_kWh(cls, sa_id):  
      return select(func.sum(PowerLog.kw_generated))\
           .where(PowerLog.solar_array_id == sa_id)\
           .where(func.date(PowerLog.logged_at) == date.today())
            
   def date_formatter(self, log_date):
      result_date = datetime.fromisoformat(log_date)
      return result_date.strftime('%m-%d-%Y %I:%M %p')

@app.route('/')
@app.route('/login')
def index():
   return render_template('login.html', title='Welcome back')

@app.route('/dashboard')
def dashboard():
   solar_stmt = (
         select(SolarFarm)
        .options(
           selectinload(SolarFarm.solar_panels)
           .selectinload(SolarArray.power_log)
         )
   )
   solar_farms = db.session.scalars(solar_stmt).all()
   solar_schema = SolarFarmSchema(many=True)
   solar_farms_result = solar_schema.dump(solar_farms)
   power_log_results = PowerLogResults()
   solar_farm_stats = []
   for farm in solar_farms_result:
      for solar_panel in farm['solar_panels']:
         farms = {}
         farms.update(
           {
            'name' : farm['name'],
            'power_log' : solar_panel['power_log'],
            'model' : solar_panel['panel_model'],
            'total_panels' : solar_panel['total_panels'],
            'kWh' : power_log_results.kW_calculator('kWh', solar_panel['solar_array_id']),
            'status' : solar_panel['status'],
            'log_date' : power_log_results.date_formatter([
                logged_date['logged_at'] for logged_date in solar_panel['power_log']][0]
            ),
            'current_kw' : power_log_results.kW_calculator('CURRENT', solar_panel['solar_array_id']),
            'daily_low' : power_log_results.kW_calculator('LOW', solar_panel['solar_array_id']),
            'daily_high' : power_log_results.kW_calculator('HIGH', solar_panel['solar_array_id']),
           }
         ) 
         solar_farm_stats.append(farms)
   return render_template('dashboard.html', solar_farms=solar_farm_stats)
         
@app.route('/forgot-password')
def forgot_password():
   pass

if __name__ == '__main__':
   app.run(debug=True)