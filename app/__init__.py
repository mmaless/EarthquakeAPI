from flask import Flask
from app.api import api_bp
from app.data import job

app = Flask(__name__)
app.register_blueprint(api_bp)
job()

