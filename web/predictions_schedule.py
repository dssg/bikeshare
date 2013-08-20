import schedule
from threading import Thread, RLock
from flask import jsonify
import time
import timeit
from poisson_web import make_prediction, getStations
import pickle

lock = RLock()
cache = dict()

def get_prediction_and_save(many_mins=15):
  stations = getStations()
  prediction_list = []
  for station in stations:
    prediction_list.append(make_prediction(station, int(many_mins)))

  lock.acquire()
  try: 
    cache[many_mins] = prediction_list
    pickle.dump(cache, open("cache.p", "wb") )
  finally:
    lock.release()

def predict_all_cache(many_mins=15):
  lock.acquire()

  try:
    if many_mins in cache:
      return jsonify({"predictions": cache[many_mins], "time": many_mins})
    else:
      return jsonify({"predictions": [], "time": many_mins})
  finally:
    lock.release()

def prediction_loop(n):
  start = timeit.default_timer()

  print("Starting Prediction")
  get_prediction_and_save(n)
  print("Finished Prediction")

  stop = timeit.default_timer()
  print stop - start

def run_threaded(job_func, args):
    job_thread = Thread(target=job_func, args = args)
    job_thread.start()

def start_thread():
  schedule.every(5).minutes.do(run_threaded, prediction_loop, (15,)).run()
  schedule.every(5).minutes.do(run_threaded, prediction_loop, (30,)).run()
  # schedule.every(5).minutes.do(run_threaded, prediction_loop, (60,)).run()
  # schedule.every(5).minutes.do(run_threaded, prediction_loop, (120,)).run()

  while True:
    schedule.run_pending()
    time.sleep(10)

if __name__ == "__main__":
  start_thread()