#--------------------------------
# 1. SET UP THE FLASK WEATHER APP
#--------------------------------

# Import Dependencies

from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

#--------------------------------
# 2. Database Setup
#--------------------------------

# Access SQLite Database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into classes
Base = automap_base()
Base.prepare(autoload_with=engine)

# Create the classes variables
Station = Base.classes.station
Measurement = Base.classes.measurement

#--------------------------------
# 3. Flask Setup
#--------------------------------

# Define the Flask app
app = Flask(__name__)

#--------------------------------
# 4. Welcome Flask Route
#--------------------------------

# Define Welcome Route
@app.route("/")

# Create the welcome() function
def welcome():
    return(
        '''
	Welcome to the Climate Analysis API!
	Available Routes:
	/api/v1.0/precipitation
	/api/v1.0/stations
	/api/v1.0/tobs
	/api/v1.0/temp/start/end
	''')

#--------------------------------
# 5. Precipitation Flask Route
#--------------------------------

# Define precipitation route
@app.route("/api/v1.0/precipitation")

# Create the precipitation() function
def precipitation():

    # Create session(link) from Python to the DB
    session = Session(engine)
    
	# Calculate the date one year ago from the most recent date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Query: get date and precipitation for prev_year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date >= prev_year).all()
		
	# Create dictionary w/ jsonify()--format results into .JSON
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# -----------------------------
# 6. Stations Route
# -----------------------------

# Define stations route
@app.route("/api/v1.0/stations")

# Create the stations() function
def stations():

    # Create session(link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station).all()
    
	# Convert results array into a list with `list()`
    stations = list(np.ravel(results))
    return jsonify(stations=stations) 

# NOTE: `stations=stations` formats the list into JSON
# NOTE: Flask documentation: https://flask.palletsprojects.com/en/1.1.x/api/#flask.json.jsonify

# -----------------------------
# 7. Monthly Temperature Route
# -----------------------------

# Define monthly temperature 
@app.route("/api/v1.0/tobs")

def temp_monthly():

    # Create session(link) from Python to the DB
    session = Session(engine)
    
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
		filter(Measurement.station == 'USC00519281').\
		filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# -----------------------------
# 8. Statistics Route
# -----------------------------

# Provide both start and end date routes:
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# Add parameters to `stats()`: `start` and `end` parameters
def stats(start=None, end=None):

    # Create session(link) from Python to the DB
    session = Session(engine)
    
	# Query: min, avg, max temps; create list called `sel`
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

	# Check if start date is provided
    if start and end:
        # Query with both start and end dates
    	results = session.query(*sel).\
    		filter(Measurement.date >= start).\
    		filter(Measurement.date <= end).all()
    elif start:
        # Query with only start date
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    else:
        # Handle the case where no dates are provided 
        results = session.query(*sel).all()
    
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug=True)