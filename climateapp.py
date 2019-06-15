# Import Modules
#----------------
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
#----------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# Flask Setup
#-------------
app = Flask(__name__)


# Flask Routes
#--------------


# Home
#--------------
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App <br/>"
        f"<br/>"
        f"<br/>"
        f"Precipitation Data: /api/v1.0/precipitation <br/>"
        f"<br/>"
        f"Station Data: /api/v1.0/stations <br/>"
        f"<br/>"
        f"Temperature Observations: /api/v1.0/tobs <br/>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"View Min, Max & Avg Temps for specific dates or date ranges using the formats below <br/>"
        f"Replace 'yyyy-mm-dd' with chosen dates: <br/>"
        f"<br/>"        
        f"<br/>"  
        f"Temperature Observations Using Single Date <br/>"
        f"------------------------------------------------ <br/>"
        f"/api/v1.0/yyyy-mm-dd <br/>"
        f"<br/>"
        f"<br/>"
        f"Temperature Observations Using Date Range <br/>"
        f"------------------------------------------------ <br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd <br/>"
        f"/api/v1.0/startdate/enddate"
    )


# Precipitation
#---------------
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Run query
    prcpresults = session.query(Measurement).all()

    # Dictionary
    precipitation = []
    for measure in prcpresults:
        precip_dict = {}
        precip_dict["date"] = measure.date
        precip_dict["prcp"] = measure.prcp
        precipitation.append(precip_dict)
    
    return jsonify(precipitation)


# Stations
#--------------
@app.route("/api/v1.0/stations")
def stations():
    stresults = session.query(Station.station, Station.name).all()

    all_stations = list(np.ravel(stresults))

    return jsonify(all_stations)


# Temp Observations
#-------------------
@app.route("/api/v1.0/tobs")
def tobs():
    # Define dates
    start_date_tobs = "2016-08-23"
    end_date_tobs = "2017-08-23"

    # Run query
    tobsresults = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > start_date_tobs).\
        filter(Measurement.date < end_date_tobs).\
        order_by(Measurement.date).all()

    all_tobs = list(np.ravel(tobsresults))

    return jsonify(all_tobs)
    


# Specific Temp Observations
# Start Date Only
#----------------------------
@app.route("/api/v1.0/<start>")
def tobs_by_start(start):
    canonicalized = start  
    
    # Run query
    measurementquery = session.query(Measurement).all()

    # Dictionary
    measure_dict = []
    for mquery in measurementquery:
        m_dict = {}
        m_dict["date"] = mquery.date
        m_dict["tobs"] = mquery.tobs
        measure_dict.append(m_dict)

    for obvs in measure_dict:
        search_term = obvs["date"]

        if search_term == canonicalized:
            
            startresults = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= search_term).all()
            
            all_starts = list(np.ravel(startresults))

            return jsonify(all_starts)

    return jsonify({"error": "Date not in database. Check formatting and refer to Home page."}), 404
   

# Specific Temp Observations
# Start & End Date
#----------------------------
@app.route("/api/v1.0/<start>/<end>")
def tobs_by_range(start, end):
    canonicalized = start

    # Run query
    measurementquery = session.query(Measurement).all()

    # Dictionary
    measure_dict = []
    for mquery in measurementquery:
        m_dict = {}
        m_dict["date"] = mquery.date
        m_dict["tobs"] = mquery.tobs
        measure_dict.append(m_dict)
    
    for obvs in measure_dict:
        search_start = obvs["date"]

        if search_start == canonicalized:
            # Run end date
            canonicalized = end

            # Run query
            measurementquery = session.query(Measurement).all()

            # Dictionary
            measure_dict = []
            for mquery in measurementquery:
                m_dict = {}
                m_dict["date"] = mquery.date
                m_dict["tobs"] = mquery.tobs
                measure_dict.append(m_dict)
                    
            for obvs in measure_dict:
                search_end = obvs["date"]

                if search_end == canonicalized:
                    rangeresults = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= search_start).\
                        filter(Measurement.date <= search_end).all()
                            
                    all_range = list(np.ravel(rangeresults))

                    return jsonify(all_range)
                    
            return jsonify({"error": "End Date not in database. Check formatting and refer to Home page."}), 404

    return jsonify({"error": "Start Date not in database. Check formatting and refer to Home page."}), 404


if __name__ == '__main__':
    app.run(debug=True)