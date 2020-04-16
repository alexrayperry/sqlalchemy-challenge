# Import dependencies.
from flask import Flask, jsonify
from datetime import datetime
import datetime as dt

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

# Create engine for connecting to sqlite file.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()

# Set up base to reflect the database in sqlite file.
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create Variable to be used for querying tables/classes.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Start session between python and database.
session = Session(engine)

# Flask setup. 
app = Flask(__name__)

# First flask route setup
@app.route("/")

# Define function for homepage and list all available routes.
def welcome():
    return(
        f"Welcome to my home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end>"
    )
# Flask route setup.
@app.route("/api/v1.0/precipitation")

# Define function and query results to a dictionary using date as the key and prcp as the value
def precipitation():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    # For lookp through results and append date results as Key and prcp results as values to a dictionary.
    all_prcp = []
    for date, prcp in results:
        prcp_dict ={date:prcp}
        all_prcp.append(prcp_dict)

    # Return results
    return jsonify(all_prcp)

# Flask route setup    
@app.route("/api/v1.0/stations")

# Define funtion and query to return a JSON list of stations from the dataset.
def stations():

    all_stations = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(all_stations))

    return jsonify(stations)

# Flask Setup.
@app.route("/api/v1.0/tobs")

# Define function and query the dates and temperature observations of the most active station 
# for the last year of data to return JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temps = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == "USC00519281").\
            filter(Measurement.date >= last_year).all()

    session.close()    

# For loop to append results into a dictionary of a list rather than just listing the temperature by itself.
# Include the date as the key and the temp as the value so that the data made more sense.
    tobs_list = []
    for date, tobs in temps:
        tobs_dict ={date:tobs}
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

# Flask setup.
@app.route("/api/v1.0/<start>")

# Define function and query to return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for for all dates greater or equal to a given start date.
def begin(start):

    # Set new variable to hold the date-string inputted by user in datetime format (year, month, day).
    new_start = datetime.strptime(start, "%Y-%m-%d").date()

    # Query for all dates in the datebase and set results in a list.
    dates = session.query(Measurement.date).all()
    dates = list(np.ravel(dates))

    # Loop through dates and set dates in datetime format. Same format as new_start.
    for date in dates:
        search_date = datetime.strptime(date,"%Y-%m-%d").date()

        # Set if condition. If date in the database is the same as date inputted by user, query for 
        # the TMIN, TAVG, and TMAX and return results in json list.
        if search_date == new_start:
            start_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
            return jsonify(start_temps)
    
    session.close()
    
    # If the date a user inputted is not a date in the database, display below error.
    return jsonify(f'{start} cannot be found. Please try a date prior to 2017-08-23.')

#Flask setup
@app.route("/api/v1.0/<start>/<end>")

# Define function. Query to calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
# and return in JSON list.
def calc_temps(start, end):
     return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
     filter(Measurement.date >= start).filter(Measurement.date <= end).all())

session.close()

# Boilerplate ending syntax for app.
if __name__ == "__main__":
    app.run(debug=True)







