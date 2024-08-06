# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/15132/OneDrive/Desktop/SQL Alchemy/Starter_Code/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement 

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
    )

# Returns json with the date as the key and the value as the precipitation 
    
@app.route("/api/v1.0/precipitation")
def precipitation():

    #Returns json with the date as the key and the value as the precipitation
    results = session.query(measurement.date, measurement.prcp).all()
    
    #Only returns the jsonified precipitation data for the last year in the database
    dict = {str(date): prcp for date, prcp in results}
    return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():
    
    #Returns jsonified data of all of the stations in the database
    # Query all stations
    results2 = session.query(station.station_id, station.name, station.latitude, station.longitude, station.elevation).all()

    #Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station_id, name, latitude, longitude, elevation in results2:
        stations_dict = {}
        stations_dict["station_id"] = station_id
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    #Returns jsonified data for the most active station (USC00519281)
    results3 = session.query(measurement.date, measurement.prcp, measurement.tobs).filter(measurement.station == "USC00519281",measurement.date >= dt.date(2016,8,23)).all()

    
    #Only returns the jsonified data for the last year of data
    dict2 = {str(date): {"prcp": prcp, "tobs": tobs} for date, prcp, tobs in results3}
    return jsonify(dict2)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_stats(start, end=None):

    #Define the selection of the min, avg, and max temperatures
    selection = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    #Query the database
    start_end = session.query(*selection).filter(measurement.date >= start)
    if end:
        start_end = start_end.filter(measurement.date <= end)

    #Execute results

    results4 = start_end.all()
    
    #Extract results
    temperatures = list(results4[0])  # results is a list of tuples, we need the first (and only) tuple

    #Return the results as JSON
    return jsonify({
        "temp_min": temperatures[0],
        "temp_avg": temperatures[1],
        "temp_max": temperatures[2]})


if __name__ == '__main__':
    app.run(debug=True)