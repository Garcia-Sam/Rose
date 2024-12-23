from flask import Flask, session
from flask_session import Session
app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from app import routes