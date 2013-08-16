from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for
import json
import time
import timeit

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

  # file = open("./static/data/washingtondc.json", "rb")
  # temp = json.load(file)
  return str(make_prediction(station_id, int(many_mins)))
  # return jsonify({"washingtondc": temp})

@app.route("/predict_all/<many_mins>")
def predict_all(many_mins=10):
  stations = getStations()
  prediction_list = []
  start_time = time.clock()
  for station in stations:
    prediction_list.append(make_prediction(station, int(many_mins)))
  finish_time = time.clock()
  request_time = "%.2gs" % (finish_time - start_time)
  return jsonify({"predictions": prediction_list, "time": many_mins, "request_time": request_time})
	
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=80)
