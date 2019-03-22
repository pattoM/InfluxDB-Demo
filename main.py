from flask import Flask,request, abort,jsonify
from datetime import datetime
import rfc3339
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import random
from influxdb import InfluxDBClient

#app init for flask
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secrejslfwfsfsnjuettoeepwlslsldsmc,saala'

cors = CORS(app)

uri = 'https+influxdb://avnadmin:pbc584brpvkjnfj@influx1-nine6959-eg8c.aivencloud.com:13986/mydb' #get influx uri and insert here. Current value is obsolete
client = InfluxDBClient.from_dsn(uri, timeout=3.0, ssl=True)

#set up functions
def time_logger():
    """
    Generates a random number every X minutes and saves to influx db
    Inputs:
        None
    Returns:
        None
    """
    number = random.randint(0,100)
    rfc_time = rfc3339.rfc3339(datetime.now(), utc=True, use_system_timezone=False)
    json_body = [
        {
            "measurement": "randomdata",
            "tags": {
                "source": "randomgenerator",
            },
            "time": rfc_time,
            "fields": {
                "level": number
            }
        }
    ]
    client.write_points(json_body)




#Running the task every X mins
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
main_task = scheduler.add_job(time_logger,'interval',seconds=10)


#serve data from the db. Demo route
@app.route('/get-data/<date>', methods=['GET'])
def fetch_timeseries(date):
    if date == 'all':
        query_st = "select * from randomdata"
        res = client.query(query_st)
        return jsonify(res.raw)
    else:
        query_st = "select * from randomdata where time > '{}'".format(date)
        res = client.query(query_st)
        return jsonify(res.raw)

if __name__=='__main__':
    app.run(port=5007, debug=True)
