import configparser
from flask_apscheduler import APScheduler
from database import Database
from flask import Flask


db = Database()

cfg = configparser.ConfigParser()
cfg.read('configuration.ini')

messages = configparser.ConfigParser()
messages.read('messages.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertgfdsa'

# initialize scheduler
scheduler = APScheduler()

# if you don't want to use config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
