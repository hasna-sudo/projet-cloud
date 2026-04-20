
from flask import Flask, jsonify

import datetime

app = Flask(__name__)

@app.route('/')

def home():

    return '<h1>Cloud Platform</h1><p>Pipeline CI/CD operationnel</p>'

@app.route('/health')

def health():

    return jsonify({

        "status": "ok",

        "service": "flask-app",

        "time": str(datetime.datetime.now())

    })

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)

