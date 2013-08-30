from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for
import json
from threading import Thread
import pickle

# import config
from poisson_web import make_prediction, getStations

app = Flask(__name__)

@app.route("/map/")
def show_map():
	return render_template('template.html')

@app.route("/table/")
def show_table():
  return render_template('table.html')

@app.route("/")
def hello():
	return render_template('template.html')

@app.route("/predict/<station_id>/<many_mins>")
def predict(station_id, many_mins):
  stations = getStations()
  return jsonify(make_prediction(stations[int(station_id)], int(many_mins)))

@app.route("/predict_all/")
def predict_all():
  d = dict()
  cache = pickle.load(open("cache.p", "rb"))
  return jsonify(cache)

if __name__ == "__main__":
    app.run(debug=True)
