from flask import Flask, url_for

app = Flask(__name__)

from global_fertility_rate import routes
