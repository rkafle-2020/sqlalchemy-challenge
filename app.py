import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# Reflect an existing database into a new model.
Base = automap_base()
# Reflect the tables.
Base.prepare(engine, reflect=True)

# Save reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station
# print(Base.classes.keys())

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
        f"Welcome to the Climate App API!<br>"
        f"Use this API if you dare...<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query to retrieve the last 12 months of precipitation data and return the results."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database.
    #most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # ('2017-08-23')
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores.

    prcp_data= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=year_ago).all()

    session.close()


     # Convert the query results to a dictionary using date as the key and prcp as the value.
    all_precipication = [] ('2017-08-23')
    for date, prcp in prcp_data:
        if prcp != None:
            precip_dict = {}
            precip_dict[date] = prcp
            all_precipication.append(precip_dict)

    # Return the JSON representation of dictionary.
    return jsonify(all_precipication)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point for the most active station."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database.
    #most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # ('2017-08-23')
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Find the most active station.
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()

    # Get the station id of the most active station.
    (most_active_station_id, ) = most_active_station
    print(f"The station id of the most active station is {most_active_station_id}.")

    # Perform a query to retrieve the data and temperature scores for the most active station from the last year.
    temp_last_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= year_ago).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and temperature as the value.
    all_temperatures = []
    for date, temp in temp_last_year:
            temp_dict = {}
            temp_dict["date"] = date
            temp_dict["temp"] = temp
            all_temperatures.append(temp_dict)
            
    # Return the JSON representation of dictionary.
    return jsonify(all_temperatures)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for stations.
    stations = session.query(Station.station, Station.name,
                             Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Convert the query results to a dictionary.
    all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    # Return the JSON representation of dictionary.
    return jsonify(all_stations)



if __name__ == '__main__':
    app.run(debug=True)