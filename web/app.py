from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for
import json

# import config
from poisson_web import make_prediction, getStations

app = Flask(__name__)

@app.route("/maps/")
def show_map():
	return render_template('template.html')

@app.route("/")
def hello():
	return render_template('template.html')

@app.route("/predict/<station_id>/<many_mins>")
def predict(station_id, many_mins):
  stations = getStations()
  return jsonify(make_prediction(stations[int(station_id)], int(many_mins)))

@app.route("/predict_all/<many_mins>")
def predict_all(many_mins=0):
  stations = getStations()[:73]
  prediction_list = []
  for station in stations:
    prediction_list.append(make_prediction(station, int(many_mins)))
  return jsonify({"predictions": prediction_list, "time": many_mins})
	
if __name__ == "__main__":
    app.run(debug=True)