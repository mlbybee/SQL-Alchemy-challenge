# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################

database_path = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# List all available routes
@app.route("/")
def welcome():
    """List all available API routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# App routing for precipitation analysis list (12 months of data)
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session 
    session = Session(engine)

    # Query the last 12 months of precipitation data - Measurement Table
    cutoff_date = '2016-08-23'
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date > cutoff_date).all()
    session.close()

    # Create a dictionary from the results and append to a list 
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

# App routing for stations analysis list  
@app.route("/api/v1.0/stations")
def stations(): 
    # Create session 
    session = Session(engine)

    station_data = session.query(station.station).all()
    session.close()  

    # Create a dictionary of the active stations and their counts and append to a list of stations_data
    station_list = []
    for station in station_data:
        stations_dict = {}
        stations_dict["station"] = station
        station_list.append(stations_dict)
        
    return jsonify (station_list) 

# App routing for temperatures observed analysis list (Previous 12 months of data)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session 
    session = Session(engine)

    # Query the last 12 months of temperature data from the most active observation station - Measurement Table
    cutoff_date = '2016-08-23'
    tobs_data_12months = session.query(measurement.date, measurement.tobs).\
    filter((measurement.station == 'USC00519281') & (measurement.date > cutoff_date)).all()
    session.close()

    #create a dictionary of t_obs data for the most active station
    tobs_list_12months = []
    for date, tobs in tobs_data_12months:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Oberved Temperature"] = tobs
        tobs_list_12months.append(tobs_dict)

    return jsonify(tobs_list_12months)

# App routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    session = Session(engine)

    start_date_tobs_data = session.query(func.avg(measurement.tobs), func.min(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    start_date_tobs_list = []
    for avg, min, max in start_date_tobs_data:
        start_date_tobs_dict = {}
        start_date_tobs_dict["Average"] = avg
        start_date_tobs_dict["Minimum"] = min
        start_date_tobs_dict["Maximum"] = max
        start_date_tobs_list.append(start_date_tobs_dict)

    return jsonify(temp_list)

# App routing for min, max, avg temp for a given start date and end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    start_end_date_tobs_data = session.query(func.avg(measurement.tobs), func.min(measurement.tobs), func.max(measurement.tobs)).\
        filter((measurement.date >= start_date)&(measurement.date <= end_date)).all()

    start_end_date_tobs_list = []
    for avg, min, max in start_end_date_tobs_data:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["Average"] = avg
        start_end_tobs_date_dict["Minimum"] = min
        start_end_tobs_date_dict["Maximum"] = max
        start_end_date_tobs_list.append(start_end_tobs_date_dict)

    return jsonify(start_end_date_tobs_list)

# Define main branch
if __name__ == '__main__':
    app.run(debug=True)