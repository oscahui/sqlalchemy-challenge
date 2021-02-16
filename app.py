#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"        
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    data=session.query(measurement.date,measurement.prcp).filter(measurement.date > '2016-08-23').all()
        
    prcp=[]
    for item  in data:
        prcp_dict = {}
        prcp_dict["date"] = item.date
        prcp_dict["prcp"] = item.prcp
        prcp.append(prcp_dict)    
    
    return jsonify(prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    query = session.query(station.id, station.station, station.name).all()

    station_1 = []
    for item in query:
        station_dict = {}
        station_dict["id"] = item.id
        station_dict["station"] = item.station
        station_dict['name'] = item.name
        station_1.append(station_dict)

    return jsonify(station_1)

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    most = session.query(measurement.station, func.count(measurement.date).label('count')).group_by(measurement.station).order_by(func.count(measurement.date).desc()).first()
    query = session.query(measurement.date, measurement.tobs).filter(measurement.station == most.station, measurement.date>'2016-08-23').all()
    
    temp = []
    for item in query:
        temp_dict = {}
        temp_dict["date"] = item.date
        temp_dict["temperature"] = item.tobs
        temp.append(temp_dict)    
    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def temp(start):
    session = Session(engine)     
    try:
        start= dt.datetime.strptime(str(start),"%Y-%m-%d") 
        data=session.query(measurement.date,measurement.tobs).filter(measurement.date >= start).all()
        
        df_weather = pd.DataFrame(data=data,columns=["date","temp"])
        min_temp = df_weather["temp"].min()
        max_temp = df_weather["temp"].max()
        mean_temp = df_weather["temp"].mean()
        
        return jsonify({'MIN': min_temp}, {'AVG': mean_temp}, {'MAX': max_temp})

    except:        
        print("YYYY-MM-DD")

@app.route("/api/v1.0/<start>/<end>")   
def temp2(start,end):
    session = Session(engine)     
    try:
        start= dt.datetime.strptime(str(start),"%Y-%m-%d") 
        end= dt.datetime.strptime(str(end),"%Y-%m-%d") 
        data=session.query(measurement.date,measurement.tobs).filter(measurement.date >= start).filter(measurement.date <= end).all()
        
        df_weather = pd.DataFrame(data=data,columns=["date","temp"])
        min_temp = df_weather["temp"].min()
        max_temp = df_weather["temp"].max()
        mean_temp = df_weather["temp"].mean()
        
        return jsonify({'MIN': min_temp}, {'AVG': mean_temp}, {'MAX': max_temp})

    except:        
        print("YYYY-MM-DD")


if __name__ == '__main__':
    app.run(debug=True)

