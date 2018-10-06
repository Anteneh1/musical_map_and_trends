import os
import pprint
import pymongo
from flask import Flask, render_template, jsonify, request, redirect
from bson import json_util, ObjectId
import json

# Debugging variables
flask_debugging = True # Set to True when in Flask debug mode (DISABLE BEFORE DEPLOYING LIVE)

# Initialize Flask
app = Flask(__name__)

@app.route("/")
def welcome():
    # Return to the dashboard
    return render_template("index.html")

# Route that outputs database results
@app.route("/getCitiesFromMongo")
def getCitiesFromMongo():
    """ Retrieve & return all cities from the MongoDB collection
        Returns: jsonified results """
    db = connectToMongo()

    # If a limit was specified in the querystring, use it to limit our results
    if request.args.get('limit'):
        limit = int(request.args.get('limit'))
        return getJSON(wrapGeoJSON(db.Cities.find().limit(limit)))
    else:
        return getJSON(wrapGeoJSON(db.Cities.find()))

def wrapGeoJSON(cities):
    """ Wrap returned cities array into GeoJSON-friendly format

        Returns: Object
    """
    cities_geojson = {
        "type": "FeatureCollection",
        "features": cities
    }

    return cities_geojson

def getJSON(cities):
    """ JSON formatting of 'cities' array:
        - Dump MongoDB BSON (binary JSON) using 'json_util' package, to valid JSON string
        - Reload it as dictionary
        - Send jsonified results to browser

        Returns: jsonified results

        Arguments: cities -- array of cities (Object[])
                 """
    cities_json = json.loads(json_util.dumps(cities))
    return jsonify(cities_json)

def connectToMongo():
    """ Connect to MongoDB so we can store our 'city' documents as they are being built

        Returns: db -- database connection object
    """
    mongodb_uri = "mongodb://0920_kd:Oct2018@ds223763.mlab.com:23763/heroku_9ck3snh5"
    client = pymongo.MongoClient(mongodb_uri)
    return client.heroku_9ck3snh5  # Declare the DB

#
# *** Main script execution ***
#
if __name__ == "__main__":
    app.run(debug=flask_debugging)
