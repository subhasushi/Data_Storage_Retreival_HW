#import dependencies
import datetime
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Database Set up
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurements = Base.classes.measurements
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Flask set up
app = Flask(__name__)

#Flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App:<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    """Return a list of all precipitation data"""
    # Query all date and tobs for last year
    first_date = session.query(measurements.prcp,measurements.date).order_by(measurements.date.desc()).first()
    last_date = datetime.datetime.strptime(str(first_date.date), '%Y-%m-%d') - datetime.timedelta(days=365)

    prcp_data = session.query(measurements.date,measurements.prcp).filter(measurements.date > last_date ).order_by(measurements.date.desc()).all()
    
    # Convert list into dict
    
    # for data in prcp_data:
    #     prcp_dict = {}
    #     prcp_data.to_dict(data)

    prcp_dict = []
    for data in prcp_data:
        result = {}
        result['date'] = data[0]
        result['prcp'] = data[1]
        prcp_dict.append(result)

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def station():
    """Returns a list of all the stations"""
    station_data = session.query(stations.name).all()

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of temperature observation data for the previous year"""
    #Getting the latest date and station ID for station with highest tobs
    first_date_tobs = session.query(measurements.tobs,measurements.date).order_by(measurements.date.desc()).first()
    last_date_tobs = datetime.datetime.strptime(str(first_date_tobs.date), '%Y-%m-%d') - datetime.timedelta(days=365)
    tobs_data = session.query(measurements.tobs).filter(measurements.date > last_date_tobs).all()

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def min_avg_max(start):
    """Returns min, avg and max temperatures for dates > the start date"""
    print ( f"start --- {start}")
    min_max_avg_start = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date > start).all()
    return jsonify(min_max_avg_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    print ( f"start --- {start} {end}")
    """Returns TMIN, TAVG, and TMAX for dates between the start and end date inclusive"""
    min_max_avg_range = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).filter(measurements.date <= end).all()
    return jsonify(min_max_avg_range)
    
    
if __name__ == '__main__':
    app.run(debug=True)
