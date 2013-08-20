import schedule
from threading import Thread, RLock
from flask import jsonify
import time
import timeit
from poisson_web import make_prediction, getStations
import pickle

lock = RLock()
cache = dict()

def get_prediction_and_save(many_mins):
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

def start_threads():
  run_threaded(prediction_loop, (0,))
  run_threaded(prediction_loop, (15,))
  run_threaded(prediction_loop, (30,))
  run_threaded(prediction_loop, (45,))
  run_threaded(prediction_loop, (60,))
  run_threaded(prediction_loop, (75,))
  run_threaded(prediction_loop, (90,))
  run_threaded(prediction_loop, (105,))
  run_threaded(prediction_loop, (120,))

if __name__ == "__main__":
  start_threads()